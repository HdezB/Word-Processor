import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit,
    QFileDialog, QMessageBox, QInputDialog, QLineEdit, QAction, QUndoStack, QUndoCommand
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QTextCursor



class WordProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Just Write")
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.setGeometry(100, 100, 800, 600)

        self.text_edit = QTextEdit(self)
        
        self.setCentralWidget(self.text_edit)

        self.create_menu()
        self.create_toolBar()
        

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        new_action = QAction(QIcon(), "New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction(QIcon(), "Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction(QIcon(), "Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

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
        toolBar.setIconSize(QSize(16, 16))
        
        toolBar.addSeparator()
        # <a href="https://www.freepik.com/search">Icon by Anggara</a>
        copy = QAction(QIcon("icons/copy_icon.png"), "Copy", self)
        copy.setShortcut("Ctrl+C")
        copy.triggered.connect(self.toggle_copy)
        toolBar.addAction(copy)
        # <a href="https://www.freepik.com/search">Icon by Pixel perfect</a>
        paste = QAction(QIcon("icons/paste_icon.png"), "Paste", self)
        paste.setShortcut("Ctrl+V")
        paste.triggered.connect(self.toggle_paste)
        toolBar.addAction(paste)

        toolBar.addSeparator()
        self.bold = QAction(QIcon("icons/bold_icon.png"), "Bold", self)
        self.bold.setShortcut("Ctrl+B")
        self.bold.triggered.connect(self.toggle_bold)
        toolBar.addAction(self.bold)
        italic = QAction(QIcon("icons/italic_icon.png"), "Italic", self)
        italic.setShortcut("Ctrl+I")
        italic.triggered.connect(self.toggle_italic)
        toolBar.addAction(italic)
        underline = QAction(QIcon("icons/underline_icon.png"), "Underline", self)
        underline.triggered.connect(self.toggle_underline)
        toolBar.addAction(underline)
        strikethrough = QAction(QIcon("icons/strikethrough_icon.png"), "Strikethrough", self)
        strikethrough.triggered.connect(self.toggle_strikethrough)
        toolBar.addAction(strikethrough)
        toolBar.addSeparator()

    def toggle_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.textCursor().selection().toHtml())

    def toggle_paste(self):
        clipboard = QApplication.clipboard()
        self.text_edit.textCursor().insertHtml(clipboard.text())

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
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    word_processor = LockdownWordProcessor()
    word_processor.show()
    sys.exit(app.exec_())
