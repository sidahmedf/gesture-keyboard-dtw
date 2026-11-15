# Gesture Keyboard DTW — Shape-Writing Virtual Keyboard in PyQt5

**Gesture Keyboard DTW** is an interactive shape-writing (swipe-to-type) virtual keyboard built in **Python** and **PyQt5**. Users draw continuous gestures across keys to input words, while a real-time recognition engine matches the trajectory against a French lexicon using spatial resampling and **Dynamic Time Warping (DTW)**.

---

## Features & Usage

* **Continuous Gesture Typing (Shape Writing):** Hold the left mouse button, drag across the letters of a word, and release—top word candidates appear immediately in the suggestion bar above the keyboard.
* **Single-Tap Input:** Click and release any individual key to type a single character directly.
* **Candidate Selection:** Click any suggested word in the recommendation bar to insert it into the text editor.

---

## Architecture & File Structure

| File | Responsibility |
| :--- | :--- |
| `main.py` | Application entry point launching the text editor and virtual keyboard widget |
| `keyboard_widget.py` | Main PyQt5 widget handling rendering, mouse events, Bézier smoothing, and candidate display |
| `key.py` | `Key` model storing pixel coordinates, dimensions, and character symbol |
| `reconnaisseur.py` | Trajectory spatial resampling (`resample`, `interpolate`) for speed-invariant matching |
| `dtw.py` | Dynamic Time Warping distance algorithm comparing user gestures against ideal templates |
| `dictionnaire.py` | Lexicon loader, first-letter indexing, and startup pre-computation of ideal word paths |
| `layout.json` | Keyboard layout definition (key coordinates, widths, and symbols) |
| `mots.txt` | French dictionary used for gesture matching |

---

## Recognition Pipeline & Performance Optimizations

### 1. Spatial Trajectory Resampling
Raw pointer coordinates vary in density depending on swipe speed. `resample()` interpolates the raw trajectory at a fixed spatial step $d$, producing uniformly spaced points for speed-invariant comparison.

### 2. Ideal Reference Templates & $O(1)$ Key Lookup
At startup, `Dictionnaire` maps every key symbol in a hash map (`key_map`) for $O(1)$ coordinate lookup, constructs ideal polyline paths connecting key centers for every dictionary word, and caches their resampled templates inside `Mot` objects—eliminating redundant path generation during user input.

### 3. First-Letter Candidate Pruning
Words are indexed by initial character (`words_by_letter`). When a gesture finishes, only dictionary entries starting with the first touched key are evaluated by DTW, drastically cutting search space and latency.

### 4. Non-Blocking Background DTW (`QThread`)
Candidate distance calculations are offloaded to a background `DTWWorker(QThread)` thread that emits a `finished` signal once top-$k$ (`nbReco`) matches are ranked—keeping the PyQt5 UI responsive at all times.

### 5. Quadratic Bézier Stroke Smoothing
Rather than rendering jagged line segments, pointer trails are drawn using quadratic Bézier curves (`QPainterPath.quadTo`) where each raw point acts as a control point toward the midpoint of consecutive samples.

---

## Getting Started

### Prerequisites
* **Python:** 3.8+
* **PyQt5**

### Installation & Execution
```bash
pip install PyQt5
python main.py
```