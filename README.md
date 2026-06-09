# Sorting Algorithm Visualiser

An interactive visualiser for 6 classic sorting algorithms, built in Python with tkinter. Watch each algorithm work through an array in real time, with colour-coded bars showing comparisons, swaps, and sorted elements as they happen.

---

## Algorithms

### Bubble Sort
Repeatedly steps through the array, compares adjacent elements, and swaps them if they're in the wrong order. Simple but slow — each pass bubbles the largest unseen value to its final position.

[![Bubble Sort]](https://youtu.be/vfoMPg9zGKc)

**Complexity:** O(n²) time · O(1) space

---

### Selection Sort
Scans the unsorted portion of the array to find the minimum element, then swaps it into place. Makes the fewest swaps of any O(n²) algorithm.

demonstrations/selection_sort.mkv

**Complexity:** O(n²) time · O(1) space

---

### Insertion Sort
Builds a sorted sub-array one element at a time by shifting each new element left until it's in the right position. Efficient on small or nearly-sorted arrays.

[Insertion Sort](https://youtu.be/avZRYe--QOM)

**Complexity:** O(n²) time · O(1) space

---

### Merge Sort
Recursively divides the array in half, sorts each half, then merges them back together. Consistently fast and stable — the divide-and-conquer approach guarantees O(n log n) in all cases.

[![Merge Sort]](https://youtu.be/aJzO_YmD06A)

**Complexity:** O(n log n) time · O(n) space

---

### Quick Sort
Picks a pivot element and partitions the array so that everything smaller is to its left and everything larger is to its right, then recurses on each side. Fast in practice despite a worst-case of O(n²).

demonstrations/quick_sort.mkv

**Complexity:** O(n log n) average · O(log n) space

---

### Heap Sort
Turns the array into a max-heap, then repeatedly extracts the largest element and places it at the end. Guaranteed O(n log n) with no extra memory.

[Heap Sort](https://youtu.be/FjU0Ea_Zy4o)

**Complexity:** O(n log n) time · O(1) space

---

## Colour key

| Colour | Meaning |
|--------|---------|
| 🔵 Blue | Unsorted |
| 🔴 Red | Being compared |
| 🟣 Purple | Being swapped |
| 🟢 Green | Sorted |
| 🟡 Yellow | Pivot element |

---

## Requirements

- Python 3.6+
- tkinter (included with most Python distributions)

```bash
# Linux — if tkinter is missing
sudo apt install python3-tk      # Debian / Ubuntu
sudo dnf install python3-tkinter # Fedora
```

---

## Running

```bash
python sorting_visualiser.py
```

---

## Controls

| Control | Description |
|---------|-------------|
| Algorithm dropdown | Choose which algorithm to run |
| Array Size slider | Set the number of elements (10–200) |
| Speed slider | Slow down or speed up the animation |
| Generate | Create a new random array |
| Sort ▶ | Start the visualisation |
| Stop ■ | Interrupt mid-sort |

---

## License

MIT
