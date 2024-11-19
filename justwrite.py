import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLabel,
    QFileDialog, QMessageBox, QAction, QDialog,
    QLineEdit, QPushButton, QGridLayout
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QIntValidator



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

class TimerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Timer")
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout(self)
        
        # Labels
        hours_label = QLabel("Hours:")
        minutes_label = QLabel("Minutes:")
        seconds_label = QLabel("Seconds:")
        
        # Line edits for input
        self.hours_edit = QLineEdit("0")
        self.minutes_edit = QLineEdit("0")
        self.seconds_edit = QLineEdit("0")
        
        # Only allow integers within valid ranges
        self.hours_edit.setValidator(QIntValidator(0, 999))
        self.minutes_edit.setValidator(QIntValidator(0, 59))
        self.seconds_edit.setValidator(QIntValidator(0, 59))
        
        # Buttons
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        # Add widgets to layout
        layout.addWidget(hours_label, 0, 0)
        layout.addWidget(self.hours_edit, 0, 1)
        layout.addWidget(minutes_label, 1, 0)
        layout.addWidget(self.minutes_edit, 1, 1)
        layout.addWidget(seconds_label, 2, 0)
        layout.addWidget(self.seconds_edit, 2, 1)
        layout.addWidget(ok_button, 3, 0)
        layout.addWidget(cancel_button, 3, 1)


class LockdownWordProcessor(WordProcessor):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JustWrite")
        self.lockdown_enabled = False
        self.lockdown_timer = None  # Initialize the timer variable
        self.remaining_time = 0

        # Create a QLabel for displaying the countdown
        self.countdown_label = QLabel(self)
        self.countdown_label.setStyleSheet("color: red; font-size: 24px;")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.hide()  # Hide it initially

        self.add_lockdown_menu()

    def add_lockdown_menu(self):
        tools_menu = self.tools_menu

        self.lockdown_action = QAction("Enable Lockdown Mode", self)
        self.lockdown_action.triggered.connect(self.toggle_lockdown_mode)
        tools_menu.addAction(self.lockdown_action)

    def toggle_lockdown_mode(self):
        if not self.lockdown_enabled:
            self.enable_lockdown_mode()
        else:
            self.disable_lockdown_mode()

    def enable_lockdown_mode(self):
        # Create and display the timer dialog
        timer_dialog = TimerDialog(self)
        if timer_dialog.exec_() == QDialog.Accepted:
            try:
                hours = int(timer_dialog.hours_edit.text())
                minutes = int(timer_dialog.minutes_edit.text())
                seconds = int(timer_dialog.seconds_edit.text())

                # Validate inputs
                if hours < 0 or minutes < 0 or seconds < 0:
                    raise ValueError

                total_seconds = hours * 3600 + minutes * 60 + seconds

                # Proceed to activate Lockdown Mode
                self.lockdown_enabled = True

                # Hide window decorations and make fullscreen
                self.setWindowFlag(Qt.WindowCloseButtonHint, False)
                self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
                self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
                self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
                self.showFullScreen()  # Apply the changes

                # Update the menu action text
                self.lockdown_action.setText("Disable Lockdown Mode")

                # Inform the user that Lockdown Mode has been activated
                QMessageBox.information(
                    self,
                    "Lockdown Mode",
                    "Lockdown Mode has been activated."
                )

                # After the message box is closed, start the timer
                if total_seconds == 0:
                    # No timer set
                    self.lockdown_timer = None
                    self.remaining_time = 0
                    self.countdown_label.hide()
                else:
                    # Initialize the remaining time in seconds
                    self.remaining_time = total_seconds

                    # Set up the timer to disable Lockdown Mode after the duration
                    self.lockdown_timer = QTimer(self)
                    self.lockdown_timer.setSingleShot(True)
                    self.lockdown_timer.timeout.connect(self.disable_lockdown_mode)
                    self.lockdown_timer.start(total_seconds * 1000)  # Convert to milliseconds

                    # Set up the update timer to refresh the label every second
                    self.update_timer = QTimer(self)
                    self.update_timer.timeout.connect(self.update_countdown_label)
                    self.update_timer.start(1000)  # Update every 1000 milliseconds (1 second)
                    self.countdown_label.show()
                    self.update_countdown_label()  # Update immediately

                    # Inform the user about the timer
                    QMessageBox.information(
                        self,
                        "Timer Set",
                        f"Lockdown Mode will automatically disable after {hours}h {minutes}m {seconds}s."
                    )

            except ValueError:
                self.lockdown_enabled = False
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please enter valid non-negative integers for hours, minutes, and seconds."
                )
        else:
            # User canceled the timer dialog; do not activate Lockdown Mode
            self.lockdown_enabled = False
            QMessageBox.information(
                self,
                "Lockdown Mode",
                "Lockdown Mode activation canceled."
            )

    def update_countdown_label(self):
        if self.remaining_time > 0:
            hours, remainder = divmod(self.remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_text = f"Time Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}"
            self.countdown_label.setText(time_text)
            self.countdown_label.adjustSize()
            # Position the label at the top center of the window
            self.countdown_label.move(
                (self.width() - self.countdown_label.width()) // 2,
                10  # 10 pixels from the top
            )
            self.remaining_time -= 1
        else:
            # Time is up, disable Lockdown Mode
            self.update_timer.stop()
            self.countdown_label.hide()

    def disable_lockdown_mode(self):
        if not self.lockdown_enabled:
            return  # Already disabled

        self.lockdown_enabled = False

        # Restore window decorations
        self.setWindowFlag(Qt.WindowCloseButtonHint, True)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.showNormal()  # Apply the changes

        # Stop the lockdown timer if it's running
        if self.lockdown_timer and self.lockdown_timer.isActive():
            self.lockdown_timer.stop()
            self.lockdown_timer = None

        # Stop the update timer if it's running
        if hasattr(self, 'update_timer') and self.update_timer.isActive():
            self.update_timer.stop()
            self.countdown_label.hide()

        self.remaining_time = 0

        QMessageBox.information(
            self,
            "Lockdown Mode",
            "Lockdown Mode has been deactivated."
        )

        # Update the menu action text
        self.lockdown_action.setText("Enable Lockdown Mode")

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
