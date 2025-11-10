import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import cv2

from utils import globals as g
from core import image_processing as iproc
from core import transformation as trans
from core import aruco_analysis as aruco_module
from ui.sliders_panel import create_paired_slider

def start_app():
    root = tk.Tk()
    root.title("Image Processing Toolkit")
    root.geometry("1150x650")
    root.configure(bg="#1e1e1e")
    g.root = root

    selected_contour_idx = tk.IntVar(value=0)
    sliders = {}

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#1e1e1e")
    style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 9))
    style.configure("TButton", font=("Segoe UI", 9, "bold"))

    toolbar = ttk.Frame(root, width=320)
    toolbar.pack(side="left", fill="y", padx=10, pady=10)

    ttk.Label(toolbar, text="HSV Range", font=("Segoe UI", 11, "bold")).pack(pady=(0,10))

    def update_display():
        # call core processing to get a PIL preview, vertex text and contours
        pil, text, contours = iproc.draw_contours_and_prepare_preview(sliders, selected_contour_idx)
        # update combo values
        options = [f"Contour {i+1} (area={int(cv2.contourArea(c))})" for i,c in enumerate(contours)] if contours else []
        if options:
            combo_contours["values"] = options
            # ensure selected index is in range
            if selected_contour_idx.get() >= len(contours):
                selected_contour_idx.set(0)
            combo_contours.current(selected_contour_idx.get())
        else:
            combo_contours["values"] = ["None"]
            combo_contours.set("None")
        label_vertices.config(text=text)
        # update image label
        if pil is not None:
            imgtk = ImageTk.PhotoImage(pil)
            label_img.imgtk = imgtk
            label_img.configure(image=imgtk)

    def on_sliders_change(): update_display()

    create_paired_slider(toolbar, "Min H", "Max H", 0, 179, 0, 179, sliders, on_sliders_change)
    create_paired_slider(toolbar, "Min S", "Max S", 0, 255, 0, 255, sliders, on_sliders_change)
    create_paired_slider(toolbar, "Min V", "Max V", 0, 255, 0, 255, sliders, on_sliders_change)

    ttk.Label(toolbar, text="Kernel Size").pack(anchor="center", pady=(8, 2))
    frame_kernel = ttk.Frame(toolbar)
    frame_kernel.pack(pady=2)
    val = tk.DoubleVar()
    slider_kernel = ttk.Scale(frame_kernel, from_=1, to=30, orient="horizontal", variable=val)
    slider_kernel.pack(side="left", fill="x", expand=True)
    lbl_k = ttk.Label(frame_kernel, text="0", width=4)
    lbl_k.pack(side="right", padx=3)
    def _k_trace(var=val, lbl=lbl_k):
        lbl.config(text=str(int(var.get())))
        on_sliders_change()
    val.trace_add("write", lambda *args: _k_trace())
    sliders["Kernel"] = slider_kernel

    ttk.Label(toolbar, text="Epsilon (%)").pack(anchor="center", pady=(8, 2))
    frame_epsilon = ttk.Frame(toolbar)
    frame_epsilon.pack(pady=2)
    val_eps = tk.DoubleVar()
    slider_eps = ttk.Scale(frame_epsilon, from_=0.1, to=10.0, orient="horizontal", variable=val_eps)
    slider_eps.pack(side="left", fill="x", expand=True)
    lbl_eps = ttk.Label(frame_epsilon, text="1.0", width=4)
    lbl_eps.pack(side="right", padx=3)
    def _eps_trace(var=val_eps, lbl=lbl_eps):
        lbl.config(text=f"{var.get():.1f}")
        on_sliders_change()
    val_eps.trace_add("write", lambda *args: _eps_trace())
    sliders["Epsilon"] = slider_eps
    slider_eps.set(1.0)
    slider_kernel.set(5)

    ttk.Label(toolbar, text="Select Countour", font=("Segoe UI", 10, "bold")).pack(anchor="center", pady=(10, 2))
    combo_contours = ttk.Combobox(toolbar, state="readonly", width=25)
    combo_contours.pack(anchor="center", pady=(0, 10))
    combo_contours.bind("<<ComboboxSelected>>", lambda e: (selected_contour_idx.set(combo_contours.current()), update_display()))
    combo_contours["values"] = ["None"]
    combo_contours.set("None")

    ttk.Separator(toolbar).pack(fill="x", pady=10)
    ttk.Label(toolbar, text="Vertices", font=("Segoe UI", 10, "bold")).pack(anchor="center")
    label_vertices = ttk.Label(toolbar, text="Detected Count: 0")
    label_vertices.pack(anchor="center", pady=(5, 10))

    ttk.Button(toolbar, text="Input Image", command=lambda: img_selector()).pack(fill="x", pady=5)
    ttk.Button(toolbar, text="Transform", command=lambda: do_transform()).pack(fill="x", pady=5)
    ttk.Button(toolbar, text="Aruco", command=lambda: do_aruco()).pack(fill="x", pady=5)

    content = ttk.Frame(root)
    content.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    label_img = tk.Label(content, bg="#1e1e1e")
    label_img.pack(side="top", pady=10)
    # label for vertices info (on toolbar)

    def img_selector():
        path = filedialog.askopenfilename(title="Input Image", filetypes=[("Non-cloud Images", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        if not path:
            return
        new_img = cv2.imread(path)
        if new_img is None:
            print("[Error] Could not open input image provided.")
            return
        g.img = new_img
        g.transformed_img = None
        # auto update
        update_display()

    def color_picker(event):
        if g.img is None:
            return
        x = int(event.x / g.scale_ratio)
        y = int(event.y / g.scale_ratio)
        if y >= g.img.shape[0] or x >= g.img.shape[1] or x < 0 or y < 0:
            return
        bgr_color = g.img[y, x].reshape(1, 1, 3)
        hsv_color = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = map(int, hsv_color)
        delta_h, delta_s, delta_v = 20, 40, 40
        sliders["Min H"].set(max(0, h - delta_h))
        sliders["Min S"].set(max(0, s - delta_s))
        sliders["Min V"].set(max(0, v - delta_v))
        sliders["Max H"].set(min(179, h + delta_h))
        sliders["Max S"].set(min(255, s + delta_s))
        sliders["Max V"].set(min(255, v + delta_v))
        update_display()

    def do_transform():
        ok = trans.apply_transformation()
        if ok:
            trans.show_transformation(root)

    def do_aruco():
        aruco_module.analyze_and_show(root)

    # bind color picker
    label_img.bind("<Button-1>", color_picker)

    root.mainloop()
