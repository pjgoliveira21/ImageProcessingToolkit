import tkinter as tk
from tkinter import ttk

def create_paired_slider(parent, nome_esq, nome_dir, min_esq, max_esq, min_dir, max_dir, sliders, on_change):
    """Create a paired slider control (two paired sliders with labels).
    - sliders: dict to put the resulting ttk.Scale objects
    - on_change: callback triggered on change (receives no arguments)
    Returns nothing but populates `sliders`.
    """
    frame = ttk.Frame(parent)
    frame.pack(fill="x", pady=5)

    lbls = ttk.Frame(frame)
    lbls.pack(fill="x")
    ttk.Label(lbls, text=nome_esq, anchor="center").pack(side="left", expand=True, padx=5)
    ttk.Label(lbls, text=nome_dir, anchor="center").pack(side="right", expand=True, padx=5)

    sliders_frame = ttk.Frame(frame)
    sliders_frame.pack(fill="x")

    for nome, a, b in [(nome_esq, min_esq, max_esq), (nome_dir, min_dir, max_dir)]:
        sub = ttk.Frame(sliders_frame)
        sub.pack(side="left", expand=True, fill="x", padx=5)
        val = tk.DoubleVar()
        slider = ttk.Scale(sub, from_=a, to=b, orient="horizontal", variable=val)
        slider.pack(side="left", fill="x", expand=True)
        lbl = ttk.Label(sub, text="0", width=3)
        lbl.pack(side="right", padx=3)
        def _trace(var=val, lbl=lbl):
            lbl.config(text=str(int(var.get())))
            try:
                on_change()
            except Exception:
                pass
        val.trace_add("write", lambda *args, cb=_trace: cb())
        sliders[nome] = slider
        slider.set((a + b) // 2)
