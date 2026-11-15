from PyQt5.QtCore import QSize, Qt, pyqtSignal, QTimer, QRect, QPoint
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QFont
from key import Key
from reconnaisseur import resample
import os
import json
from dtw import dtw, DTWWorker

JSON_FILE_PATH = 'layout.json'

class KeyboardWidget(QWidget):

    newletter = pyqtSignal(str)
    newword = pyqtSignal(str)

    def __init__(self, dictionnaire=None):
        super().__init__()
        self.keys = [] # sécurité
        self.scale = 2
        self.pressed_key = None
        self.hovered_key = None
        self.trace =[]
        self.load_keyboard_layout(JSON_FILE_PATH)
        self.key_map = {key.symbol: key for key in self.keys}  # pour un accès rapide aux touches par symbole o(1)
        self.recommendations = []  # liste des recommandations de mots basées sur la tracé de l'utilisateur
        self.dictionnaire = dictionnaire
        self.initUI()


    def initUI(self):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.updateGeometry()
        self.setMouseTracking(True) # Active le suivi de la souris pour détecter les mouvements même lorsque aucun bouton n'est pressé




    def load_keyboard_layout(self, file_path):

    #securité : vérifiez que le fichier existe et est un fichier JSON valide avant de tenter de le charger.
        if not os.path.isfile(file_path):
           raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")

        if not file_path.endswith('.json'):
            raise ValueError(f"Le fichier {file_path} n'est pas un fichier JSON.")

    #utilisez le package json et enregistrez les paramètres dans votre KeyboardWidget pour pouvoir les réutiliser plus tard.
        with open(file_path, 'r', encoding="utf-8") as f:
            layout = json.load(f)
        # Enregistrez les paramètres du clavier dans votre KeyboardWidget
        self.key_width = int(layout.get("keyWidth") * self.scale)
        self.key_height = int(layout.get("keyHeight") * self.scale)
        self.key_spacing = int(layout.get("keySpacing") * self.scale)
        self.nb_reco = layout.get("nbReco", 1)

        #Les touches doivent être enregistrées dans une nouvelle classe Key
        keys_data = layout.get("keys")
        for key_data in keys_data:
            key = Key(
                symbol=key_data.get("symbol"),
                grid_column=key_data.get("x"),
                grid_row=key_data.get("y"),
                grid_width=key_data.get("width"),
                key_width=self.key_width,
                key_height=self.key_height,
                key_spacing=self.key_spacing
            )
            self.keys.append(key)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        font = QFont()
        font.setPointSize(int(self.key_height // 4))
        font.setBold(False)

        painter.setFont(font)
        for key in self.keys:
            if key == self.hovered_key :
                painter.setBrush(QColor(150, 150, 255))
            else :
                painter.setBrush(QColor(200, 200, 200))


            painter.drawRoundedRect(key.rect, 3, 3)
            painter.drawText(key.rect, Qt.AlignCenter, key.symbol)  # Affiche le symbole de la touche au centre

        # Dessiner la tracé
        if len(self.trace)>2 :
            pen = QPen()
            pen.setColor(QColor(50, 150, 255,100))  # Couleur bleue avec une transparence (100 pour la transparence)
            pen.setWidth(8)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)

            painter.setBrush(Qt.NoBrush)  # Pas de remplissage pour la tracé
            path = QPainterPath()
            x, y = self.trace[0]
            path.moveTo(x, y)

            for i in range(len(self.trace) - 1):
                x1,y1 = self.trace[i]
                x2,y2 = self.trace[i + 1]
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                path.quadTo(x1, y1, mid_x, mid_y)

            x,y = self.trace[-1]
            path.lineTo(x, y)
            painter.drawPath(path)

        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.drawLine(0, self.key_height, self.sizeHint().width(), self.key_height)


        painter.setPen(QPen(Qt.black))
        for i in range(self.nb_reco):
            reco_width = self.sizeHint().width() // self.nb_reco
            x = i * reco_width
            rect = QRect(x, 0, reco_width, self.key_height)
            painter.setBrush(QColor(220, 220, 220))  # same grey always
            painter.drawRect(rect)
            if i < len(self.recommendations):
                painter.drawText(rect, Qt.AlignCenter, self.recommendations[i])



    def sizeHint(self):

        #nombre des touches en x
        nb_keys_x = max(key.grid_column + key.grid_width for key in self.keys)
        #nombre des touches en y
        nb_keys_y = max(key.grid_row + 1 for key in self.keys)
        #calcul de la taille totale du clavier en pixels
        total_width = nb_keys_x * self.key_width + (nb_keys_x - 1) * self.key_spacing
        #calcul de la taille totale du clavier en pixels
        total_height = nb_keys_y * self.key_height + (nb_keys_y - 1) * self.key_spacing


        return QSize(total_width, total_height)

    def mousePressEvent(self, event):
        self.trace = [] # Réinitialise la trace à chaque clic
        if event.button() == Qt.LeftButton:
            self.pressed_key = self.getKeyAtPosition(event.pos())


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Vérifiez si une recommandation a été cliquée
            for i, word in enumerate(self.recommendations):
                reco_width = self.sizeHint().width() // self.nb_reco
                x = i * reco_width
                rect = QRect(x, 0, reco_width, self.key_height)
                if rect.contains(event.pos()):
                    self.newword.emit(word)
                    self.recommendations = []
                    self.update()
                    return  # stop

            #traitement normal de la relâchement d'une touche
            released_key = self.getKeyAtPosition(event.pos())
            if released_key is not None and released_key == self.pressed_key:
                self.newletter.emit(released_key.symbol) #émet un signal avec le symbole de la touche relâchée
            self.pressed_key = None

        # resample la tracé de l'utilisateur et calculer les recommandations de mots basées sur la tracé resampled
        if len(self.trace) >= 2:
            resampled = resample(self.trace, d=20)
            self.computeRecommendations(resampled)


        QTimer.singleShot(500, self.clear_trace) # Efface la trace après un court délai pour permettre à l'utilisateur de voir la tracé avant qu'elle ne disparaisse

    def mouseMoveEvent(self, event):
        current_pos = event.pos()
        if not self.rect().contains(current_pos):
            return # Ignore les mouvements de souris en dehors du widget

        self.hovered_key = self.getKeyAtPosition(event.pos())
        if event.buttons() & Qt.LeftButton and self.pressed_key is not None:
            self.trace.append((event.pos().x(), event.pos().y()))
        self.update()  # Redessine le widget pour mettre à jour l'affichage des touches survolées

    def getKeyAtPosition(self, pos):
        for key in self.keys:
            if key.isOver(pos):
                return key
        return None

    def clear_trace(self):
        self.trace = []
        self.update()  # Redessine le widget pour effacer la tracé

    def wordToStroke(self, word: str, d: int) -> list:
        stroke = []
        for char in word:
            key = self.key_map.get(char)
            if key :
                center_x = key.rect.x() + key.rect.width() // 2
                center_y = key.rect.y() + key.rect.height() // 2
                stroke.append((center_x, center_y))

        return resample(stroke, d)

    def computeRecommendations(self, user_stroke: list):
        first_key = self.getKeyAtPosition(
            QPoint(int(user_stroke[0][0]), int(user_stroke[0][1]))
        )
        if first_key is None:
            return

        candidates = self.dictionnaire.words_by_letter.get(first_key.symbol, [])

        # Lancez le calcul des recommandations dans un thread séparé pour éviter de bloquer l'interface utilisateur
        self.worker = DTWWorker(user_stroke, candidates, self.nb_reco)
        self.worker.finished.connect(self.onRecommendationsReady)
        self.worker.start()

    def onRecommendationsReady(self, results):
        self.recommendations = results
        self.update()