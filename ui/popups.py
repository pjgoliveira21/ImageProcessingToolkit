# small helpers to create popups used by transformation and aruco modules
import tkinter as tk
from PIL import Image, ImageTk
import cv2

def show_image_popup(parent, title, bgr_image, bg="#1e1e1e", size=None):
    if bgr_image is None:
        return None
    popup = tk.Toplevel(parent)
    popup.title(title)
    popup.configure(bg=bg)
    rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    if size is not None:
        img = img.resize(size)
    imgtk = ImageTk.PhotoImage(img)
    lbl = tk.Label(popup, image=imgtk, bg=bg)
    lbl.image = imgtk
    lbl.pack(padx=10, pady=10)
    return popup
