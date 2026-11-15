import math

from PyQt5.QtCore import QThread, pyqtSignal as Signal


def dtw(s: list, t: list) -> float:
    n = len(s)
    m = len(t)

    DTW = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    DTW[0][0] = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = math.dist(s[i-1], t[j-1])
            DTW[i][j] = cost + min(
                DTW[i-1][j],    # insertion
                DTW[i][j-1],    # deletion
                DTW[i-1][j-1]   # match
            )

    return DTW[n][m]



class DTWWorker(QThread):
    finished = Signal(list)  # Signal pour envoyer les résultats à l'interface principale

    def __init__(self, user_stroke, candidates, nb_reco):
        super().__init__()
        self.user_stroke = user_stroke
        self.candidates = candidates
        self.nb_reco = nb_reco

    def run(self):
        distances = []
        for mot in self.candidates:
            distance = dtw(self.user_stroke, mot.stroke)
            distances.append((distance, mot.mot))
        distances.sort(key=lambda x: x[0])
        results = [word for _, word in distances[:self.nb_reco]]
        self.finished.emit(results)