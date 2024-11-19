import sys

import re 

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit,
    QFileDialog, QMessageBox, QInputDialog, QLineEdit, QAction, QUndoStack, QUndoCommand, QFontDialog, QShortcut, QFontComboBox, QLabel, QMenu, QComboBox
)
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent, QRect
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QTextBlockFormat, QKeySequence, QFontDatabase, QTextCharFormat, QColor, QSyntaxHighlighter, QPainter, QScreen
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from spellchecker import SpellChecker

#Custom QTextEdit widget that integrates spell-checker
class CustomSpellCheckTextEdit(QTextEdit):
    def __init__(self, spell_checker):
        super().__init__()
        self.spell_checker = spell_checker
        self.spell_check_enabled = True
        self.misspelled_words = []

        #adding custome words to spell check database to prevent faulty flagging
        custom_words = ["ok", "functionalities"]
        for word in custom_words:
            self.spell_checker.word_frequency.add(word)

        #connects content change signal of document to spell check so words can be rechecked for spelling
        self.document().contentsChange.connect(self.handle_contents_change)

    #toggles spell check on or off, rechecking all words if enabled
    def toggle_spell_check(self):
        self.spell_check_enabled = not self.spell_check_enabled
        if self.spell_check_enabled:
            self.recheck_all_words()
        self.viewport().update()

    #rechecks mispelled words
    def recheck_all_words(self):
        self.misspelled_words.clear()  

        #exit if spell checking is disabled
        if not self.spell_check_enabled:
            return

        #check from beginning of document
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)

        #iterate through all words in document, check for mispellings, and record position of mispelled words
        while not cursor.atEnd():
            cursor.select(QTextCursor.WordUnderCursor)
            word = cursor.selectedText()
            clean_word = ''.join(filter(str.isalnum, word))

            if clean_word and clean_word in self.spell_checker.unknown([clean_word]):
                self.misspelled_words.append((cursor.selectionStart(), cursor.selectionEnd()))

            cursor.movePosition(QTextCursor.NextWord)

    #checks for mispelled words near the edited position when document is changed
    def handle_contents_change(self, position, chars_removed, chars_added):
        if not self.spell_check_enabled:
            return

        #skip rechecking all words; only check near the edited position
        self.recheck_all_words()

    #pain function to indicate mispelled words with red underline
    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.spell_check_enabled or not self.misspelled_words:
            return

        painter = QPainter(self.viewport())
        painter.setPen(QColor("red"))

        #highlight each mispelled word
        for start, end in self.misspelled_words:
            self.draw_red_line(start, end, painter)

    #draws red underline under mispelled words, from start to end position
    def draw_red_line(self, start, end, painter):
        document = self.document()
        cursor = self.textCursor()

        cursor.setPosition(start)
        word_start_rect = self.cursorRect(cursor)

        cursor.setPosition(end)
        word_end_rect = self.cursorRect(cursor)

        if word_start_rect.top() == word_end_rect.top():
            line_start = word_start_rect.bottomLeft()
            line_end = word_end_rect.bottomRight()
            painter.drawLine(line_start, line_end)

    #clears list of mispelled words and refreshes viewport to remove highlights
    def clear_misspelled_words(self):
        self.misspelled_words.clear()
        self.viewport().update()

#main window class for managing text editor, layout, and UI components
class WordProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JustWrite")
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.setGeometry(100, 100, 800, 600)

        #initialize spell checker
        self.spell_checker = SpellChecker()

        #get screen dpi
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch() 

        #calculate page dimension based on dpi (8.5 inch x 11 inch  with 1 inch margins)
        page_width = int(8.5 * dpi)  
        page_height = int(11 * dpi)  
        margin_pixels = int(1 * dpi)  

        #create page view
        self.page_widget = QWidget(self)
        self.page_widget.setStyleSheet("""
            background: white;
            border: 1px solid #ccc;
        """)
        
        self.page_widget.setFixedSize(page_width, page_height)

        #create the text editor
        self.text_edit = CustomSpellCheckTextEdit(self.spell_checker)
        self.text_edit.setFont(QFont("Times New Roman", 12))  # Default font
        self.text_edit.setStyleSheet("background: transparent;")  # Match text area with the page
        self.text_edit.setFrameShape(QTextEdit.NoFrame)  # Remove extra borders

        #set text margins using QTextFrame
        doc = self.text_edit.document()
        root_frame = doc.rootFrame()
        frame_format = root_frame.frameFormat()
        margin_bias = 0
        frame_format.setLeftMargin(margin_pixels-margin_bias)
        frame_format.setRightMargin(margin_pixels-margin_bias)
        frame_format.setTopMargin(margin_pixels-margin_bias)
        frame_format.setBottomMargin(margin_pixels-margin_bias)
        root_frame.setFrameFormat(frame_format)

        #use layout to embed text editor in the page
        page_layout = QVBoxLayout(self.page_widget)
        page_layout.setContentsMargins(0, 0, 0, 0)  # No extra margins around the editor
        page_layout.addWidget(self.text_edit)

        #create a container to center the page
        self.page_container = QWidget(self)
        self.page_container.setStyleSheet("background: #eaeaea;")  # Workspace background
        container_layout = QVBoxLayout(self.page_container)
        container_layout.addWidget(self.page_widget, alignment=Qt.AlignCenter)

        #set the container as the central widget
        self.setCentralWidget(self.page_container)

        #create menus and toolbars
        self.create_menu()
        self.create_toolBar()

        #connect textChanged signal to update_word_count
        self.text_edit.textChanged.connect(self.update_word_count)

    #function for main menu bar (includes file menu, edit menu, format menu, layout menu, and tools menu)
    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        format_menu = menu_bar.addMenu("Format")
        layout_menu = menu_bar.addMenu("Layout")
        
        #new File
        self.new_action = QAction(QIcon("icons/new_file_icon.png"), "New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)
        #open File
        open_action = QAction(QIcon("icons/open_folder_icon.png"), "Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        #save File
        self.save_action = QAction(QIcon("icons/save_icon.png"), "Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        #exit File
        exit_action = QAction(QIcon("icons/exit_icon.png"), "Exit", self)
        exit_action.triggered.connect(self.close)

        file_menu.addActions([self.new_action, open_action, self.save_action, exit_action])
        
        #edit Menu Bar
        #copy
        #<a href="https://www.freepik.com/search">Icon by Anggara</a>
        self.copy_action = QAction(QIcon("icons/copy_icon.png"), "Copy", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self.toggle_copy)

        #paste
        #<a href="https://www.freepik.com/search">Icon by Pixel perfect</a>
        self.paste_action = QAction(QIcon("icons/paste_icon.png"), "Paste", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.toggle_paste)

        #cut
        self.cut_action = QAction(QIcon("icons/cut_icon.png"), "Cut", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.triggered.connect(self.toggle_cut)

        edit_menu.addActions([self.copy_action, self.paste_action, self.cut_action])
        
        #format menu
        #bold
        self.bold_action = QAction(QIcon("icons/bold_icon.png"), "Bold", self)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self.toggle_bold)

        #italic
        self.italic_action = QAction(QIcon("icons/italic_icon.png"), "Italic", self)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.triggered.connect(self.toggle_italic)

        #underline
        self.underline_action = QAction(
            QIcon("icons/underline_icon.png"), "Underline", self)
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.triggered.connect(self.toggle_underline)

        #strikethrough
        self.strikethrough_action = QAction(
            QIcon("icons/strikethrough_icon.png"), "Strikethrough", self)
        self.strikethrough_action.setShortcut("Ctrl+Shift+S")
        self.strikethrough_action.triggered.connect(self.toggle_strikethrough)

        format_menu.addActions([self.bold_action, self.italic_action, self.underline_action, self.strikethrough_action])
        
        #layout
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
        #check if there is text to be saved, prompt user to save if there is
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
    '''
    def open_file(self):
        """
        Open and load a file into the editor with optimized performance.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Text Files (*.txt);;All Files (*)",
            options=options
        )

        if file_path:
            try:
                # Open and read the file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Temporarily disable signals and rendering
                self.text_edit.blockSignals(True)
                self.text_edit.spell_check_enabled = False
                self.text_edit.clear()
                self.text_edit.setPlainText(content)
                self.text_edit.blockSignals(False)

                # Re-enable spell-checking after loading
                QTimer.singleShot(500, self.text_edit.recheck_all_words)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

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
    '''
    def save_file(self):
        #file dialog to select save location and file format
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "",
            "Rich Text Format (*.rtf);;Text Files (*.txt);;PDF Files (*.pdf);;All Files (*)",
            options=options
        )

        if file_path:
            try:
                if file_path.endswith(".pdf"):
                    #save as pdf
                    printer = QPrinter(QPrinter.HighResolution)
                    printer.setOutputFormat(QPrinter.PdfFormat)
                    printer.setOutputFileName(file_path)
                    printer.setPageSize(QPrinter.Letter)
                    self.text_edit.document().print_(printer)
                elif file_path.endswith(".rtf"):
                    #save as rtf
                    with open(file_path, 'w', encoding='utf-8') as file:
                        content = self.text_edit.document().toHtml()
                        file.write(content)
                else:
                    #save as txt
                    with open(file_path, 'w', encoding='utf-8') as file:
                        content = self.text_edit.toPlainText()
                        file.write(content)

                QMessageBox.information(self, "File Saved", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def open_file(self):
        #file dialog to select file to open
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Rich Text Format (*.rtf);;Text Files (*.txt);;All Files (*)",
            options=options
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                #temporarily disable the spell checker and signals
                self.text_edit.blockSignals(True)
                self.text_edit.spell_check_enabled = False

                if file_path.endswith(".rtf"):
                    #load rtf content
                    self.text_edit.setHtml(content)
                else:
                    #load txt content
                    self.text_edit.setPlainText(content)

                #re-enable spell checker and signals 
                self.text_edit.blockSignals(False)

                #recheck spelling asynchronously to avoid UI delays
                QTimer.singleShot(500, self.text_edit.recheck_all_words)

                QMessageBox.information(self, "File Opened", "File opened successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    #function to create toolbar and set properties
    def create_toolBar(self):
        self.toolBar = self.addToolBar("Bold")
        self.toolBar.setIconSize(QSize(17, 17))
        #add file operations (new, save)
        self.toolBar.addActions([self.new_action, self.save_action])
        

        #add edition operations (copy, paste)
        self.toolBar.addSeparator()
        self.toolBar.addActions([self.copy_action, self.paste_action])

        #add font selection dropdown
        self.toolBar.addSeparator()
        self.font_combo_box = QFontComboBox(self)
        self.font_size_combo_box = QComboBox(self)
        default_font_family = "Times New Roman"
        index = self.font_combo_box.findText(default_font_family)
        if index != -1:
            self.font_combo_box.setCurrentIndex(index)
        
        #add font size dropdown
        self.font_size_combo_box.addItems(
            [str(size) for size in range(8, 65, 2)])
        self.font_combo_box.currentFontChanged.connect(self.change_font)
        self.font_size_combo_box.currentTextChanged.connect(
            self.change_font_size)
        default_font_size = 12 
        index = self.font_size_combo_box.findText(str(default_font_size))
        if index != -1:
            self.font_size_combo_box.setCurrentIndex(index)
        self.toolBar.addWidget(self.font_combo_box)
        self.toolBar.addWidget(self.font_size_combo_box)

        #add text formatting options (bold, italic, underline, strikethrough)
        self.toolBar.addSeparator()
        self.toolBar.addActions([self.bold_action, self.italic_action,
                           self.underline_action, self.strikethrough_action])
        
        #add text alighnment actions (left, right, center, justify)
        self.toolBar.addSeparator()
        self.toolBar.addActions([self.align_left, self.align_center,
                           self.align_right, self.align_justify])
        
        #add spell check toggle
        self.toolBar.addSeparator() 
        self.spell_check_action = QAction(QIcon("icons/spell_check_icon.png"), "Toggle Spell Check", self)
        self.spell_check_action.setCheckable(True)
        self.spell_check_action.setChecked(True)  # Default: Enabled
        self.spell_check_action.triggered.connect(self.toggle_spell_check)
        self.toolBar.addAction(self.spell_check_action)

        #add spacer to move word count label to the right
        self.toolBar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolBar.addWidget(spacer)

        #add word count label 
        self.word_count_label = QLabel("Word Count: 0")
        self.word_count_label.setContentsMargins(0, 0, 10, 0)
        self.toolBar.addWidget(self.word_count_label)  # Display word count in the toolbar

    #update word count displayed in tool bar
    def update_word_count(self):
        text = self.text_edit.toPlainText()
        #ignore special characters
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        self.word_count_label.setText(f"Word Count: {word_count}")

    #functions to toggle text alignment right 
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

    #functions to toggle text alignment left
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

    #functions to toggle text alignment center
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

    #functions to toggle text alignment justify
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

    #function to change font
    def change_font(self, font: QFont):
        current_font_size = self.text_edit.currentFont().pointSize()
        font.setPointSize(current_font_size)
        self.text_edit.setCurrentFont(font)

    #function to change font size
    def change_font_size(self, size: str):
        font = self.text_edit.currentFont()
        font.setPointSize(int(size))
        self.text_edit.setCurrentFont(font)

    #function to toggle spell check
    def toggle_spell_check(self):
        self.text_edit.toggle_spell_check()

    #function to copy text to clipboard
    def toggle_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.textCursor().selection().toHtml())

    #function to paste text from clipbaord
    def toggle_paste(self):
        clipboard = QApplication.clipboard()
        self.text_edit.textCursor().insertHtml(clipboard.text())

    #function to cut text to clipboard
    def toggle_cut(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.textCursor().selection().toHtml())
        self.text_edit.textCursor().removeSelectedText()

    #function to ensure consistent left-to-right text selection when applying formatting
    def left_to_right_select(self, cursor):
        if cursor.hasSelection() and not cursor.atBlockStart() and cursor.position() == cursor.selectionStart():
            text_size = len(cursor.selectedText())
            cursor.setPosition(cursor.position())
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, text_size)

    #function to toggle bold formatting
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

    #function to toggle italic formatting
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

    #function to toggle underline formatting
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

    #function to toggle strikethrough formatting
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

#extension of WordProcessor class that adds lockdown mode to eliminate distractions
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

        self.hide_toolbar_action = QAction("Hide Toolbar", self)
        self.hide_toolbar_action.triggered.connect(self.toggle_toolbar_visibility)
        tools_menu.addAction(self.hide_toolbar_action)

    def toggle_toolbar_visibility(self):
        """
        Toggle the visibility of the toolbar and update the action text.
        """
        is_visible = self.toolBar.isVisible()
        self.toolBar.setVisible(not is_visible)  # Toggle visibility

        # Update the action text based on the new state
        if is_visible:
            self.hide_toolbar_action.setText("Show Toolbar")
        else:
            self.hide_toolbar_action.setText("Hide Toolbar")

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

#create and run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    word_processor = LockdownWordProcessor()
    word_processor.show()
    sys.exit(app.exec_())
