import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit,
    QFileDialog, QMessageBox, QInputDialog, QLineEdit, QAction, QUndoStack, QUndoCommand, QFontDialog, QShortcut, QFontComboBox, QLabel, QMenu, QComboBox
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QTextBlockFormat, QKeySequence, QFontDatabase


class WordProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JustWrite")
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.setGeometry(100, 100, 800, 600)

        self.text_edit = QTextEdit(self)

        self.setCentralWidget(self.text_edit)

        self.create_menu()
        self.create_toolBar()

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        format_menu = menu_bar.addMenu("Format")
        layout_menu = menu_bar.addMenu("Layout")
        
        # New File
        self.new_action = QAction(QIcon("icons/new_file_icon.png"), "New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)
        # Open File
        open_action = QAction(QIcon("icons/open_folder_icon.png"), "Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        # Save File
        self.save_action = QAction(QIcon("icons/save_icon.png"), "Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        # Exit File
        exit_action = QAction(QIcon("icons/exit_icon.png"), "Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addActions([self.new_action, open_action, self.save_action, exit_action])
        
        # Edit Menu Bar
        # Copy
        # <a href="https://www.freepik.com/search">Icon by Anggara</a>
        self.copy_action = QAction(QIcon("icons/copy_icon.png"), "Copy", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self.toggle_copy)

        # Paste
        # <a href="https://www.freepik.com/search">Icon by Pixel perfect</a>
        self.paste_action = QAction(QIcon("icons/paste_icon.png"), "Paste", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.toggle_paste)

        # Cut
        self.cut_action = QAction(QIcon("icons/cut_icon.png"), "Cut", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.triggered.connect(self.toggle_cut)

        edit_menu.addActions([self.copy_action, self.paste_action, self.cut_action])
        
        # Format Menu
        # Bold
        self.bold_action = QAction(QIcon("icons/bold_icon.png"), "Bold", self)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self.toggle_bold)

        # Italic
        self.italic_action = QAction(QIcon("icons/italic_icon.png"), "Italic", self)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.triggered.connect(self.toggle_italic)

        # Underline
        self.underline_action = QAction(
            QIcon("icons/underline_icon.png"), "Underline", self)
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.triggered.connect(self.toggle_underline)

        # Strikethrough
        self.strikethrough_action = QAction(
            QIcon("icons/strikethrough_icon.png"), "Strikethrough", self)
        self.strikethrough_action.setShortcut("Ctrl+Shift+S")
        self.strikethrough_action.triggered.connect(self.toggle_strikethrough)

        format_menu.addActions([self.bold_action, self.italic_action, self.underline_action, self.strikethrough_action])
        
        # Layout
        self.align_left = QAction(QIcon("icons/align_left.png"), "Align Left", self)
        self.align_left.setCheckable(True)
        self.align_left.setChecked(True)
        self.align_left.triggered.connect(self.toggle_align_left)

        self.align_center = QAction(
            QIcon("icons/align_center.png"), "Align Center", self)
        self.align_center.setCheckable(True)
        self.align_center.triggered.connect(self.toggle_align_center)

        self.align_right = QAction(
            QIcon("icons/align_right.png"), "Align Right", self)
        self.align_right.setCheckable(True)
        self.align_right.triggered.connect(self.toggle_align_right)

        self.align_justify = QAction(
            QIcon("icons/align_justify.png"), "Align Justify", self)
        self.align_justify.setCheckable(True)
        self.align_justify.triggered.connect(self.toggle_align_justify)

        layout_menu.addActions([self.align_left, self.align_center, self.align_right, self.align_justify])
        
        self.tools_menu = menu_bar.addMenu("Tools")

    def new_file(self):
        if self.text_edit.toPlainText().strip():
            reply = QMessageBox.question(self, "Unsaved Changes",
                                         "Do you want to save changes?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.No:
                self.text_edit.clear()
        else:
            self.text_edit.clear()

    def open_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Text Files (*.txt);;All Files (*)",
            options=options
        )

        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.text_edit.setText(content)
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Could not open file: {e}")

    def save_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "",
            "Text Files (*.txt);;All Files (*)",
            options=options
        )

        if file_path:
            try:
                with open(file_path, 'w') as file:
                    content = self.text_edit.toPlainText()
                    file.write(content)
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Could not save file: {e}")

    def create_toolBar(self):
        toolBar = self.addToolBar("Bold")
        toolBar.setIconSize(QSize(17, 17))
        toolBar.addActions([self.new_action, self.save_action])
        toolBar.addSeparator()
        toolBar.addActions([self.copy_action, self.paste_action])

        toolBar.addSeparator()
        self.font_combo_box = QFontComboBox(self)
        self.font_size_combo_box = QComboBox(self)
        self.font_size_combo_box.addItems(
            [str(size) for size in range(8, 65, 2)])
        self.font_combo_box.currentFontChanged.connect(self.change_font)
        self.font_size_combo_box.currentTextChanged.connect(
            self.change_font_size)
        toolBar.addWidget(self.font_combo_box)
        toolBar.addWidget(self.font_size_combo_box)
        toolBar.addSeparator()
        toolBar.addActions([self.bold_action, self.italic_action,
                           self.underline_action, self.strikethrough_action])
        toolBar.addSeparator()
        toolBar.addActions([self.align_left, self.align_center,
                           self.align_right, self.align_justify])

    def toggle_align_right(self):
        cursor = self.text_edit.textCursor()
        if self.align_justify.isChecked:
            self.align_justify.setChecked(False)
        if self.align_center.isChecked:
            self.align_center.setChecked(False)
        if self.align_left.isChecked:
            self.align_left.setChecked(False)
        self.align_right.setChecked(True)
        if cursor.hasSelection():
            block_format = QTextBlockFormat()
            block_format.setAlignment(Qt.AlignRight)
            cursor.mergeBlockFormat(block_format)
            self.text_edit.setTextCursor(cursor)
        else:
            self.text_edit.setAlignment(Qt.AlignRight)

    def toggle_align_left(self):
        if self.align_justify.isChecked:
            self.align_justify.setChecked(False)
        if self.align_center.isChecked:
            self.align_center.setChecked(False)
        if self.align_right.isChecked:
            self.align_right.setChecked(False)
        self.align_left.setChecked(True)
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            block_format = QTextBlockFormat()
            block_format.setAlignment(Qt.AlignLeft)
            cursor.mergeBlockFormat(block_format)
            self.text_edit.setTextCursor(cursor)
        else:
            self.text_edit.setAlignment(Qt.AlignLeft)

    def toggle_align_center(self):
        if self.align_justify.isChecked:
            self.align_justify.setChecked(False)
        if self.align_right.isChecked:
            self.align_right.setChecked(False)
        if self.align_left.isChecked:
            self.align_left.setChecked(False)
        self.align_center.setChecked(True)
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            block_format = QTextBlockFormat()
            block_format.setAlignment(Qt.AlignCenter)
            cursor.mergeBlockFormat(block_format)
            self.text_edit.setTextCursor(cursor)
        else:
            self.text_edit.setAlignment(Qt.AlignCenter)

    def toggle_align_justify(self):
        if self.align_right.isChecked:
            self.align_right.setChecked(False)
        if self.align_center.isChecked:
            self.align_center.setChecked(False)
        if self.align_left.isChecked:
            self.align_left.setChecked(False)
        self.align_justify.setChecked(True)
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            block_format = QTextBlockFormat()
            block_format.setAlignment(Qt.AlignJustify)
            cursor.mergeBlockFormat(block_format)
            self.text_edit.setTextCursor(cursor)
        else:
            self.text_edit.setAlignment(Qt.AlignJustify)

    def change_font(self, font: QFont):
        self.text_edit.setCurrentFont(font)

    def change_font_size(self, size: str):
        font = self.text_edit.currentFont()
        font.setPointSize(int(size))
        self.text_edit.setCurrentFont(font)

    def toggle_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.textCursor().selection().toHtml())

    def toggle_paste(self):
        clipboard = QApplication.clipboard()
        self.text_edit.textCursor().insertHtml(clipboard.text())

    def toggle_cut(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.textCursor().selection().toHtml())
        self.text_edit.textCursor().removeSelectedText()

    def left_to_right_select(self, cursor):
        if cursor.hasSelection() and not cursor.atBlockStart() and cursor.position() == cursor.selectionStart():
            text_size = len(cursor.selectedText())
            cursor.setPosition(cursor.position())
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, text_size)

    def toggle_bold(self):
        cursor = self.text_edit.textCursor()
        self.left_to_right_select(cursor)
        char_format = cursor.charFormat()
        if char_format.fontWeight() == QFont.Bold:
            char_format.setFontWeight(QFont.Normal)
        else:
            char_format.setFontWeight(QFont.Bold)
        cursor.mergeCharFormat(char_format)
        self.text_edit.setTextCursor(cursor)

    def toggle_italic(self):
        cursor = self.text_edit.textCursor()
        self.left_to_right_select(cursor)
        char_format = cursor.charFormat()
        if char_format.fontItalic() == True:
            char_format.setFontItalic(False)
        else:
            char_format.setFontItalic(True)
        cursor.mergeCharFormat(char_format)
        self.text_edit.setTextCursor(cursor)

    def toggle_underline(self):
        cursor = self.text_edit.textCursor()
        self.left_to_right_select(cursor)
        char_format = cursor.charFormat()
        if cursor.charFormat().fontUnderline() == True:
            char_format.setFontUnderline(False)
        else:
            char_format.setFontUnderline(True)
        cursor.mergeCharFormat(char_format)
        self.text_edit.setTextCursor(cursor)

    def toggle_strikethrough(self):
        cursor = self.text_edit.textCursor()
        self.left_to_right_select(cursor)
        char_format = cursor.charFormat()
        if cursor.charFormat().fontStrikeOut() == True:
            char_format.setFontStrikeOut(False)
        else:
            char_format.setFontStrikeOut(True)
        cursor.mergeCharFormat(char_format)
        self.text_edit.setTextCursor(cursor)


class LockdownWordProcessor(WordProcessor):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JustWrite")
        self.lockdown_enabled = False
        self.lockdown_password = None

        self.add_lockdown_menu()

        self.unlock_action = QAction("Unlock", self)
        self.unlock_action.triggered.connect(self.unlock_mode)
        self.unlock_action.setVisible(False)
        self.menuBar().addAction(self.unlock_action)

    def add_lockdown_menu(self):
        tools_menu = self.tools_menu

        lockdown_action = QAction("Enable Lockdown Mode", self)
        lockdown_action.triggered.connect(self.enable_lockdown_mode)
        tools_menu.addAction(lockdown_action)

    def enable_lockdown_mode(self):
        if self.lockdown_enabled:
            QMessageBox.warning(
                self, "Lockdown Mode", "Lockdown Mode is already enabled."
            )
            return

        password, ok = QInputDialog.getText(
            self,
            "Enable Lockdown Mode",
            "Set a password to disable Lockdown Mode:",
            QLineEdit.Password  # Corrected here
        )
        if ok and password:
            self.lockdown_password = password
            self.lockdown_enabled = True

            # Hide window decorations and make fullscreen
            self.showFullScreen()
            self.setWindowFlag(Qt.WindowCloseButtonHint, False)
            self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self.setWindowFlag(Qt.FramelessWindowHint, True)
            self.showFullScreen()  # Apply the changes

            QMessageBox.information(
                self,
                "Lockdown Mode",
                "Lockdown Mode has been activated."
            )

            # Show the unlock action
            self.unlock_action.setVisible(True)
        else:
            QMessageBox.warning(
                self,
                "Invalid Password",
                "You must set a password to enable Lockdown Mode."
            )

    def unlock_mode(self):
        password, ok = QInputDialog.getText(
            self,
            "Unlock Mode",
            "Enter password to unlock:",
            QLineEdit.Password  # Corrected here
        )
        if ok and password == self.lockdown_password:
            self.lockdown_enabled = False
            self.lockdown_password = None  # Clear the password

            # Restore window decorations
            self.setWindowFlag(Qt.WindowCloseButtonHint, True)
            self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.setWindowFlag(Qt.FramelessWindowHint, False)
            self.showNormal()  # Apply the changes

            QMessageBox.information(
                self,
                "Lockdown Mode",
                "Lockdown Mode has been deactivated."
            )
            self.unlock_action.setVisible(False)
        else:
            QMessageBox.warning(
                self,
                "Incorrect Password",
                "The password you entered is incorrect."
            )

    def closeEvent(self, event):
        if self.lockdown_enabled:
            event.ignore()
            QMessageBox.warning(
                self,
                "Lockdown Mode",
                "You cannot close the application in Lockdown Mode."
            )
        else:
            reply = QMessageBox.question(self, "Exit Confirmation",
                                     "Are you sure you want to exit?",
                                     QMessageBox.Yes | QMessageBox.Save | QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            elif reply == QMessageBox.Save:
                self.save_file()
                event.accept()
            else:
                event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    word_processor = LockdownWordProcessor()
    word_processor.show()
    sys.exit(app.exec_())
