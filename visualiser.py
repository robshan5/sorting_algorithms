#!/usr/bin/env python3
"""
Sorting Algorithm Visualiser
=============================
Visualises 6 classic sorting algorithms with real-time bar chart animation.

Algorithms:  Bubble Sort, Selection Sort, Insertion Sort,
             Merge Sort, Quick Sort, Heap Sort

Controls:
  - Choose algorithm and array size from the toolbar
  - Click Generate to create a new random array
  - Click Sort   to run the visualisation
  - Click Stop   to interrupt mid-sort
  - Speed slider controls animation delay

Requirements: Python 3.6+  (tkinter — included with most Python installs)
Run with:     python sorting_visualiser.py

Linux tip: sudo apt install python3-tk   (if tkinter is missing)
"""

import random
import threading
import time
import tkinter as tk
from tkinter import ttk

# ── Palette ─────────────────────────────────────────────────────────────────
BG          = "#0d0d0d"
BAR_DEFAULT = "#00c8ff"
BAR_COMPARE = "#ff4d6d"
BAR_SORTED  = "#39ff14"
BAR_PIVOT   = "#f9a620"
BAR_SWAP    = "#c77dff"
PANEL_BG    = "#141414"
TEXT_COLOR  = "#e0e0e0"
ACCENT      = "#00c8ff"

CANVAS_W = 900
CANVAS_H = 480
PAD_L    = 20
PAD_R    = 20
PAD_T    = 20
PAD_B    = 40


# ── Sorting generators (yield draw-state after each step) ────────────────────

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            yield arr[:], [j, j + 1], [], [], []
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                yield arr[:], [], [j, j + 1], [], []
        yield arr[:], [], [], list(range(n - i - 1, n)), []
    yield arr[:], [], [], list(range(n)), []


def selection_sort(arr):
    n = len(arr)
    sorted_idx = []
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            yield arr[:], [min_idx, j], [], sorted_idx, []
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        sorted_idx.append(i)
        yield arr[:], [], [i, min_idx], sorted_idx, []
    yield arr[:], [], [], list(range(n)), []


def insertion_sort(arr):
    n = len(arr)
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            yield arr[:], [j, j + 1], [], list(range(i + 1, n)), []
            arr[j + 1] = arr[j]
            yield arr[:], [], [j, j + 1], list(range(i + 1, n)), []
            j -= 1
        arr[j + 1] = key
    yield arr[:], [], [], list(range(n)), []


def merge_sort(arr):
    def _merge(arr, l, m, r):
        left  = arr[l:m + 1]
        right = arr[m + 1:r + 1]
        i = j = 0
        k = l
        while i < len(left) and j < len(right):
            yield arr[:], [l + i, m + 1 + j], [], [], []
            if left[i] <= right[j]:
                arr[k] = left[i]; i += 1
            else:
                arr[k] = right[j]; j += 1
            yield arr[:], [], [k], [], []
            k += 1
        while i < len(left):
            arr[k] = left[i]; i += 1; k += 1
            yield arr[:], [], [k - 1], [], []
        while j < len(right):
            arr[k] = right[j]; j += 1; k += 1
            yield arr[:], [], [k - 1], [], []

    def _merge_sort(arr, l, r):
        if l < r:
            m = (l + r) // 2
            yield from _merge_sort(arr, l, m)
            yield from _merge_sort(arr, m + 1, r)
            yield from _merge(arr, l, m, r)

    yield from _merge_sort(arr, 0, len(arr) - 1)
    yield arr[:], [], [], list(range(len(arr))), []


def quick_sort(arr):
    def _qs(arr, lo, hi):
        if lo >= hi:
            return
        pivot_idx = hi
        i = lo - 1
        for j in range(lo, hi):
            yield arr[:], [j], [], [], [pivot_idx]
            if arr[j] <= arr[pivot_idx]:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                yield arr[:], [], [i, j], [], [pivot_idx]
        arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
        pi = i + 1
        yield arr[:], [], [pi], [], []
        yield from _qs(arr, lo, pi - 1)
        yield from _qs(arr, pi + 1, hi)

    yield from _qs(arr, 0, len(arr) - 1)
    yield arr[:], [], [], list(range(len(arr))), []


def heap_sort(arr):
    n = len(arr)

    def heapify(arr, n, i):
        largest = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n:
            yield arr[:], [largest, l], [], [], []
            if arr[l] > arr[largest]:
                largest = l
        if r < n:
            yield arr[:], [largest, r], [], [], []
            if arr[r] > arr[largest]:
                largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            yield arr[:], [], [i, largest], [], []
            yield from heapify(arr, n, largest)

    for i in range(n // 2 - 1, -1, -1):
        yield from heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        yield arr[:], [], [0, i], [], []
        yield from heapify(arr, i, 0)
    yield arr[:], [], [], list(range(n)), []


ALGORITHMS = {
    "Bubble Sort":    bubble_sort,
    "Selection Sort": selection_sort,
    "Insertion Sort": insertion_sort,
    "Merge Sort":     merge_sort,
    "Quick Sort":     quick_sort,
    "Heap Sort":      heap_sort,
}


# ── Main App ─────────────────────────────────────────────────────────────────

class SortingVisualiser:
    def __init__(self, root):
        self.root = root
        self.root.title("Sorting Visualiser")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self._array      = []
        self._running    = False
        self._stop_flag  = False
        self._comparisons = 0
        self._swaps       = 0
        self._start_time  = 0

        self._build_ui()
        self._generate()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top toolbar ──
        toolbar = tk.Frame(self.root, bg=PANEL_BG, pady=10)
        toolbar.pack(fill=tk.X)

        tk.Label(toolbar, text="SORT", fg=ACCENT, bg=PANEL_BG,
                 font=("Courier", 16, "bold")).pack(side=tk.LEFT, padx=16)

        tk.Label(toolbar, text="Algorithm:", fg="#666", bg=PANEL_BG,
                 font=("Courier", 10)).pack(side=tk.LEFT, padx=(12, 4))
        self.algo_var = tk.StringVar(value="Bubble Sort")
        algo_cb = ttk.Combobox(toolbar, textvariable=self.algo_var,
                               values=list(ALGORITHMS.keys()),
                               state="readonly", width=16,
                               font=("Courier", 10))
        algo_cb.pack(side=tk.LEFT)

        tk.Label(toolbar, text="Size:", fg="#666", bg=PANEL_BG,
                 font=("Courier", 10)).pack(side=tk.LEFT, padx=(16, 4))
        self.size_var = tk.IntVar(value=60)
        size_spin = tk.Spinbox(toolbar, from_=10, to=200, increment=10,
                               textvariable=self.size_var, width=5,
                               font=("Courier", 10),
                               bg="#1e1e1e", fg=TEXT_COLOR,
                               buttonbackground="#222")
        size_spin.pack(side=tk.LEFT)

        tk.Label(toolbar, text="Speed:", fg="#666", bg=PANEL_BG,
                 font=("Courier", 10)).pack(side=tk.LEFT, padx=(16, 4))
        self.speed_var = tk.DoubleVar(value=0.5)
        speed_sl = tk.Scale(toolbar, variable=self.speed_var,
                            from_=0.0, to=1.0, resolution=0.05,
                            orient=tk.HORIZONTAL, length=100,
                            bg=PANEL_BG, fg=TEXT_COLOR,
                            troughcolor="#222", highlightthickness=0,
                            showvalue=False)
        speed_sl.pack(side=tk.LEFT)

        self.gen_btn = tk.Button(toolbar, text="Generate", command=self._generate,
                                 bg="#1e1e1e", fg=TEXT_COLOR, relief=tk.FLAT,
                                 font=("Courier", 10), padx=10, cursor="hand2")
        self.gen_btn.pack(side=tk.LEFT, padx=(16, 4))

        self.sort_btn = tk.Button(toolbar, text="Sort ▶", command=self._start_sort,
                                  bg=ACCENT, fg="#000", relief=tk.FLAT,
                                  font=("Courier", 10, "bold"), padx=10, cursor="hand2")
        self.sort_btn.pack(side=tk.LEFT, padx=4)

        self.stop_btn = tk.Button(toolbar, text="Stop ■", command=self._stop,
                                  bg="#ff4d6d", fg="#fff", relief=tk.FLAT,
                                  font=("Courier", 10, "bold"), padx=10,
                                  cursor="hand2", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        # ── Canvas ──
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0,
                                width=CANVAS_W, height=CANVAS_H)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 0))

        # ── Status bar ──
        status = tk.Frame(self.root, bg=PANEL_BG, pady=5)
        status.pack(fill=tk.X)

        self.cmp_var  = tk.StringVar(value="Comparisons: 0")
        self.swp_var  = tk.StringVar(value="Swaps: 0")
        self.time_var = tk.StringVar(value="Time: 0.000 s")
        self.info_var = tk.StringVar(value="")

        for var, anchor in [(self.cmp_var, tk.W), (self.swp_var, tk.W),
                            (self.time_var, tk.W), (self.info_var, tk.E)]:
            tk.Label(status, textvariable=var, fg="#555", bg=PANEL_BG,
                     font=("Courier", 9), anchor=anchor).pack(
                side=tk.LEFT if anchor == tk.W else tk.RIGHT, padx=16)

        # Complexity info per algorithm
        self._complexity = {
            "Bubble Sort":    "O(n²) time · O(1) space",
            "Selection Sort": "O(n²) time · O(1) space",
            "Insertion Sort": "O(n²) time · O(1) space",
            "Merge Sort":     "O(n log n) time · O(n) space",
            "Quick Sort":     "O(n log n) avg · O(log n) space",
            "Heap Sort":      "O(n log n) time · O(1) space",
        }
        self.algo_var.trace_add("write", self._on_algo_change)
        self._on_algo_change()

    def _on_algo_change(self, *_):
        self.info_var.set(self._complexity.get(self.algo_var.get(), ""))

    # ── Array ─────────────────────────────────────────────────────────────

    def _generate(self):
        if self._running:
            return
        n = max(10, min(200, self.size_var.get()))
        self._array = random.sample(range(1, 1001), n)
        self._comparisons = 0
        self._swaps = 0
        self.cmp_var.set("Comparisons: 0")
        self.swp_var.set("Swaps: 0")
        self.time_var.set("Time: 0.000 s")
        self._draw(self._array, [], [], [])

    # ── Drawing ───────────────────────────────────────────────────────────

    def _draw(self, arr, compare, swap, sorted_idx, pivot=None):
        self.canvas.delete("all")
        cw = self.canvas.winfo_width()  or CANVAS_W
        ch = self.canvas.winfo_height() or CANVAS_H
        n  = len(arr)
        if n == 0:
            return

        usable_w = cw - PAD_L - PAD_R
        usable_h = ch - PAD_T - PAD_B
        bar_w    = usable_w / n
        max_val  = max(arr) if arr else 1

        compare_s = set(compare)
        swap_s    = set(swap)
        sorted_s  = set(sorted_idx)
        pivot_s   = set(pivot or [])

        for i, val in enumerate(arr):
            x0 = PAD_L + i * bar_w
            x1 = x0 + bar_w - 1
            bar_h = int(val / max_val * usable_h)
            y0 = ch - PAD_B - bar_h
            y1 = ch - PAD_B

            if i in pivot_s:
                color = BAR_PIVOT
            elif i in swap_s:
                color = BAR_SWAP
            elif i in compare_s:
                color = BAR_COMPARE
            elif i in sorted_s:
                color = BAR_SORTED
            else:
                color = BAR_DEFAULT

            self.canvas.create_rectangle(x0, y0, x1, y1,
                                         fill=color, outline="",
                                         tags="bar")

        # Bottom axis line
        self.canvas.create_line(PAD_L, ch - PAD_B,
                                cw - PAD_R, ch - PAD_B,
                                fill="#222", width=1)

    # ── Sort control ──────────────────────────────────────────────────────

    def _start_sort(self):
        if self._running or not self._array:
            return
        self._running   = True
        self._stop_flag = False
        self._comparisons = 0
        self._swaps       = 0
        self._start_time  = time.perf_counter()

        self.sort_btn.config(state=tk.DISABLED)
        self.gen_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        arr = self._array[:]
        algo_fn = ALGORITHMS[self.algo_var.get()]
        thread = threading.Thread(target=self._run_sort,
                                  args=(arr, algo_fn), daemon=True)
        thread.start()

    def _run_sort(self, arr, algo_fn):
        gen = algo_fn(arr)
        for state in gen:
            if self._stop_flag:
                break
            data, compare, swap, sorted_idx, *_piv = state
            pivot = _piv[0] if _piv else []
            if compare:
                self._comparisons += 1
            if swap:
                self._swaps += 1

            elapsed = time.perf_counter() - self._start_time

            # Schedule draw on main thread
            self.canvas.after(0, self._draw, data, compare, swap, sorted_idx, pivot)
            self.canvas.after(0, self.cmp_var.set,
                              f"Comparisons: {self._comparisons:,}")
            self.canvas.after(0, self.swp_var.set,
                              f"Swaps: {self._swaps:,}")
            self.canvas.after(0, self.time_var.set,
                              f"Time: {elapsed:.3f} s")

            # Delay — speed 1.0 = instant, 0.0 = 100 ms per step
            delay = (1.0 - self.speed_var.get()) * 0.1
            if delay > 0:
                time.sleep(delay)

        self.canvas.after(0, self._on_sort_done)

    def _on_sort_done(self):
        self._running = False
        self.sort_btn.config(state=tk.NORMAL)
        self.gen_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def _stop(self):
        self._stop_flag = True


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.geometry(f"{CANVAS_W + 16}x{CANVAS_H + 120}")
    app = SortingVisualiser(root)
    root.mainloop()


if __name__ == "__main__":
    main()
