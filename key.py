from PyQt5.QtCore import QRect


class Key :
    def __init__(self, symbol, grid_column, grid_row, grid_width, key_width, key_height, key_spacing):

        # commun entre toutes les touches
        self.key_width = key_width
        self.key_height = key_height
        self.key_spacing = key_spacing
        # position de la touche dans la grille du clavier (colonne, ligne, largeur en nombre de touches)
        self.symbol = symbol
        self.grid_column = grid_column
        self.grid_row = grid_row
        self.grid_width = grid_width
        # calculer la position et la taille en pixels en fonction de la position dans la grille et des paramètres communs
        x_pixel = grid_column * (key_width + key_spacing)
        y_pixel = grid_row * (key_height + key_spacing)
        w_pixel = grid_width * key_width + (grid_width - 1) * key_spacing
        h_pixel = key_height


        self.rect = QRect(x_pixel, y_pixel, w_pixel, h_pixel)

    def isOver(self, pos):
        return self.rect.contains(pos)