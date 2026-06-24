import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListView, QLineEdit, QLabel, QFrame, 
                             QSlider, QColorDialog, QPushButton, QFileDialog, QComboBox, QCheckBox, QStyledItemDelegate, QStyle)
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QFont, QFontDatabase, QColor, QPixmap, QPainter, QKeySequence, QShortcut, QStandardItemModel, QStandardItem

CYBER_FONT_STYLE = """
QMainWindow { background-color: #0f141c; }
QWidget { background-color: #0f141c; color: #e1e4e8; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QFrame#Card { background-color: #161c24; border: 1px solid #2f3640; border-radius: 6px; }
QLineEdit { background-color: #161c24; border: 1px solid #343e4c; border-radius: 6px; padding: 10px; color: #f0f6fc; font-size: 16px; font-weight: bold; }
QListView { background-color: #161c24; border: 1px solid #2f3640; border-radius: 6px; padding: 5px; }
QSlider::groove:horizontal { border: 1px solid #343e4c; height: 6px; background: #0f141c; border-radius: 3px; }
QSlider::handle:horizontal { background: #58a6ff; width: 14px; margin: -4px 0; border-radius: 7px; }
QComboBox { background-color: #212830; border: 1px solid #343e4c; border-radius: 6px; padding: 6px; color: #e1e4e8; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #343e4c; border-radius: 3px; background-color: #161c24; }
QCheckBox::indicator:checked { background-color: #238636; border-color: #56d364; }
QPushButton { background-color: #212830; border: 1px solid #343e4c; border-radius: 6px; padding: 10px; font-weight: bold; color: #58a6ff; }
QPushButton:hover { background-color: #2d3744; border-color: #48586c; }"""

class FontDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

    def paint(self, painter, option, index):
        family = index.model().data(index, Qt.ItemDataRole.UserRole)
        text = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        
        if not family or not text:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, QColor("#212830"))
        else:
            painter.fillRect(option.rect, self.main_window.bg_color)

        sys_font = QFont("Segoe UI", 10)
        sys_font.setBold(True)
        painter.setFont(sys_font)
        painter.setPen(QColor("#8b949e"))
        
        name_rect = QRect(option.rect.left() + 15, option.rect.top(), 180, option.rect.height())
        painter.drawText(name_rect, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), family)

        painter.setPen(QColor("#2f3640"))
        painter.drawLine(option.rect.left() + 200, option.rect.top() + 10, option.rect.left() + 200, option.rect.bottom() - 10)

        size = self.main_window.slide_size.value()
        spacing = self.main_window.slide_spacing.value()
        weight = self.main_window.get_selected_weight()
        
        custom_font = QFont(family, size)
        custom_font.setWeight(weight)
        custom_font.setItalic(self.main_window.check_italic.isChecked())
        custom_font.setUnderline(self.main_window.check_underline.isChecked())
        custom_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, spacing)
        
        painter.setFont(custom_font)
        painter.setPen(self.main_window.text_color)
        
        text_rect = QRect(option.rect.left() + 220, option.rect.top(), option.rect.width() - 230, option.rect.height())
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), text)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 75)

class FontSandbox(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FontForge Live :: Матрица Шрифтов")
        self.resize(1400, 850)
        self.setStyleSheet(CYBER_FONT_STYLE)
        
        self.text_color = QColor("#58a6ff")
        self.bg_color = QColor("#161c24")
        self.init_ui()
        self.load_system_fonts()
        
        self.shortcut_copy = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut_copy.activated.connect(self.copy_selection_to_clipboard)

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        self.input_text = QLineEdit()
        self.input_text.setText("Cyberpunk 2026")
        self.input_text.textChanged.connect(self.render_matrix)
        main_layout.addWidget(self.input_text)

        splitter = QHBoxLayout()
        splitter.setSpacing(15)

        self.list_view = QListView()
        self.model = QStandardItemModel()
        self.list_view.setModel(self.model)
        
        self.delegate = FontDelegate(self)
        self.list_view.setItemDelegate(self.delegate)
        
        splitter.addWidget(self.list_view, stretch=3)

        sidebar = QFrame()
        sidebar.setObjectName("Card")
        sidebar.setFixedWidth(340)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(15)

        sidebar_layout.addWidget(QLabel("<b>🎨 ПАНЕЛЬ УПРАВЛЕНИЯ СТИЛЕМ</b>"))

        color_layout = QHBoxLayout()
        btn_color = QPushButton("Цвет текста")
        btn_color.clicked.connect(self.pick_text_color)
        btn_bg = QPushButton("Цвет фона")
        btn_bg.clicked.connect(self.pick_bg_color)
        color_layout.addWidget(btn_color)
        color_layout.addWidget(btn_bg)
        sidebar_layout.addLayout(color_layout)

        sidebar_layout.addWidget(QLabel("Начертания (Жирность):"))
        self.combo_weight = QComboBox()
        self.combo_weight.addItems(["Обычный (Normal)", "Полужирный (Medium)", "Жирный (Bold)", "Тонкий (Light)"])
        self.combo_weight.currentIndexChanged.connect(self.render_matrix)
        sidebar_layout.addWidget(self.combo_weight)

        style_layout = QHBoxLayout()
        self.check_italic = QCheckBox("Курсив")
        self.check_underline = QCheckBox("Подчеркнутый")
        self.check_italic.stateChanged.connect(self.render_matrix)
        self.check_underline.stateChanged.connect(self.render_matrix)
        style_layout.addWidget(self.check_italic)
        style_layout.addWidget(self.check_underline)
        sidebar_layout.addLayout(style_layout)

        sidebar_layout.addWidget(QLabel("Размер отображения текста:"))
        self.slide_size = QSlider(Qt.Orientation.Horizontal)
        self.slide_size.setRange(14, 45)
        self.slide_size.setValue(26)
        self.slide_size.valueChanged.connect(self.update_view)
        sidebar_layout.addWidget(self.slide_size)

        sidebar_layout.addWidget(QLabel("Межсимвольный интервал (Кернинг):"))
        self.slide_spacing = QSlider(Qt.Orientation.Horizontal)
        self.slide_spacing.setRange(-5, 30)
        self.slide_spacing.setValue(0)
        self.slide_spacing.valueChanged.connect(self.update_view)
        sidebar_layout.addWidget(self.slide_spacing)

        btn_copy = QPushButton("📋 КОПИРОВАТЬ ТЕКСТ")
        btn_copy.clicked.connect(self.copy_selection_to_clipboard)
        sidebar_layout.addWidget(btn_copy)

        btn_save = QPushButton("💾 СОХРАНИТЬ В PNG")
        btn_save.clicked.connect(self.save_to_png)
        sidebar_layout.addWidget(btn_save)

        sidebar_layout.addStretch()
        splitter.addWidget(sidebar, stretch=1)
        main_layout.addLayout(splitter)

        cw = QWidget()
        cw.setLayout(main_layout)
        self.setCentralWidget(cw)

    def load_system_fonts(self):
        self.font_families = sorted(list(set(QFontDatabase.families())))
        self.render_matrix()

    def pick_text_color(self):
        color = QColorDialog.getColor(self.text_color, self)
        if color.isValid():
            self.text_color = color
            self.update_view()

    def pick_bg_color(self):
        color = QColorDialog.getColor(self.bg_color, self)
        if color.isValid():
            self.bg_color = color
            self.update_view()

    def get_selected_weight(self):
        idx = self.combo_weight.currentIndex()
        if idx == 0: return QFont.Weight.Normal
        if idx == 1: return QFont.Weight.Medium
        if idx == 2: return QFont.Weight.Bold
        return QFont.Weight.Light

    def render_matrix(self):
        text = self.input_text.text()
        if not text: text = " "

        self.model.clear()

        for idx, family in enumerate(self.font_families):
            if idx > 200: break
            
            item = QStandardItem(text)
            item.setData(family, Qt.ItemDataRole.UserRole)
            self.model.appendRow(item)

    def update_view(self):
        self.list_view.viewport().update()

    def copy_selection_to_clipboard(self):
        indexes = self.list_view.selectedIndexes()
        if not indexes: return
        
        clean_text = indexes[0].data(Qt.ItemDataRole.DisplayRole)
        if clean_text:
            QApplication.clipboard().setText(clean_text)

    def save_to_png(self):
        indexes = self.list_view.selectedIndexes()
        if not indexes: return
        
        index = indexes[0]
        family = index.model().data(index, Qt.ItemDataRole.UserRole)
        clean_text = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        
        if not family or not clean_text: return
        
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить надпись", f"{family}_text.png", "PNG Files (*.png)")
        if path and path.strip():
            pixmap = QPixmap(900, 120)
            pixmap.fill(self.bg_color)
            painter = QPainter()
            if painter.begin(pixmap):
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setPen(self.text_color)
                
                size = self.slide_size.value()
                spacing = self.slide_spacing.value()
                weight = self.get_selected_weight()
                
                font = QFont(family, size)
                font.setWeight(weight)
                font.setItalic(self.check_italic.isChecked())
                font.setUnderline(self.check_underline.isChecked())
                font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, spacing)
                
                painter.setFont(font)
                painter.drawText(pixmap.rect().adjusted(25, 0, 0, 0), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), clean_text)
                painter.end()
                pixmap.save(path, "PNG")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FontSandbox()
    window.show()
    sys.exit(app.exec())