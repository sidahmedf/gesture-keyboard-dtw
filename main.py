import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit
from keyboard_widget import KeyboardWidget
from dictionnaire import Dictionnaire


class Editeur(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Editeur')
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        #un layout QVBoxLayout pour organiser les widgets
        main_layout = QVBoxLayout()

        #Qline
        self.line_edit = QLineEdit()
        scale = 1.3
        base_font_size = 14
        scaled_font = QFont("Arial", int(base_font_size * scale))
        self.line_edit.setFont(scaled_font)
        base_height = 40
        self.line_edit.setFixedHeight(int(base_height * scale))
        main_layout.addWidget(self.line_edit)

        #keyboard widget
        self.keyboard = KeyboardWidget()
        self.dictionnaire = Dictionnaire('mots.txt',self.keyboard,d=100)
        self.keyboard.dictionnaire =self.dictionnaire #injecter le dictionnaire dans le clavier pour qu'il puisse faire les recommandations de motsc
        main_layout.addWidget(self.keyboard )

        self.setLayout(main_layout)

        self.keyboard.newletter.connect(self.addLetter) #connecter le signal newletter du clavier à la méthode addLetter de l'éditeur
        self.keyboard.newword.connect(self.addWord)

        self.adjustSize() # Ajustez la taille de la fenêtre en fonction de son contenu (va int
        self.show()

    def addLetter(self, letter):
        current_text = self.line_edit.text()
        new_text = current_text + letter
        self.line_edit.setText(new_text)
        self.line_edit.setFocus()

    def addWord(self, word):
        self.line_edit.setText(self.line_edit.text() + word + " ")
        self.line_edit.setFocus()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Editeur()
    sys.exit(app.exec_())
