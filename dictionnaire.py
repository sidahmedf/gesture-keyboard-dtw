from keyboard_widget import KeyboardWidget

class Mot :
    def __init__(self, mot, stroke):
        self.mot = mot
        self.stroke = stroke

class Dictionnaire:
    def __init__(self, file_path: str, keyboard: KeyboardWidget, d: int):
        self.words = []
        self.words_by_letter = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:
                    stroke = keyboard.wordToStroke(word, d)
                    mot = Mot(word, stroke)
                    self.words.append(mot)

                    first_letter = word[0]
                    if first_letter not in self.words_by_letter:
                        self.words_by_letter[first_letter] = []
                    self.words_by_letter[first_letter].append(mot)

