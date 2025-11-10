import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from utils import globals as g

def apply_transformation():
    """Apply perspective transform using g.approx and set g.transformed_img."""
    if g.approx is None or len(g.approx) < 4 or g.img is None:
        print("[ERRO] Nenhum contorno válido encontrado.")
        return False

    pts = np.array([p[0] for p in g.approx], dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    ordered = np.array([
        pts[np.argmin(s)],
        pts[np.argmin(diff)],
        pts[np.argmax(diff)],
        pts[np.argmax(s)]
    ], dtype=np.float32)

    dest = np.float32([[0, 0], [500, 0], [0, 500], [500, 500]])
    M = cv2.getPerspectiveTransform(ordered, dest)
    g.transformed_img = cv2.warpPerspective(g.img, M, (500, 500))
    return True

def show_transformation(parent):
    """Display transformed image (g.transformed_img) in a popup window (parent=root)."""
    if g.transformed_img is None:
        return None
    # Destroy previous popup if exists
    if g.popup_window is not None and getattr(g.popup_window, 'winfo_exists', lambda: False)():
        try:
            g.popup_window.destroy()
        except Exception:
            pass

    popup = tk.Toplevel(parent)
    popup.title("Transformação Final")
    popup.configure(bg="#1e1e1e")

    rgb = cv2.cvtColor(g.transformed_img, cv2.COLOR_BGR2RGB)
    imgtk = ImageTk.PhotoImage(Image.fromarray(rgb))
    lbl = tk.Label(popup, image=imgtk, bg="#1e1e1e")
    lbl.image = imgtk
    lbl.pack(padx=10, pady=10)
    g.popup_window = popup
    return popup
