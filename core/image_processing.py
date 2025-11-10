import cv2
import numpy as np
from PIL import Image, ImageTk
from utils import globals as g

def apply_hsv_mask_and_find_contours(sliders):
    """Return mask (BGR) and contours list computed from g.img using slider values."""
    if g.img is None:
        return None, []

    # read slider values
    h_min, s_min, v_min = [int(sliders[x].get()) for x in ("Min H", "Min S", "Min V")]
    h_max, s_max, v_max = [int(sliders[x].get()) for x in ("Max H", "Max S", "Max V")]
    kernel_size = int(sliders["Kernel"].get())

    hsv = cv2.cvtColor(g.img, cv2.COLOR_BGR2HSV)
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower, upper)

    # Morphology (ensure odd kernel)
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    kernel = np.ones((k, k), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)

    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    return mask_bgr, contours_sorted

def draw_contours_and_prepare_preview(sliders, selected_idx):
    """Create combined preview image (mask | contoured image), update g.approx and return PIL Image."""
    mask_bgr, contours_list = apply_hsv_mask_and_find_contours(sliders)
    g.contours_list = contours_list
    img_contours = g.img.copy() if g.img is not None else None
    g.approx = None

    if contours_list:
        idx = int(selected_idx.get())
        if idx < 0 or idx >= len(contours_list):
            idx = 0
            selected_idx.set(0)
        largest = contours_list[idx]
        if cv2.contourArea(largest) > 300:
            epsilon_percent = float(sliders["Epsilon"].get())
            epsilon = (epsilon_percent / 100.0) * cv2.arcLength(largest, True)
            approx = cv2.approxPolyDP(largest, epsilon, True)
            g.approx = approx
            cv2.drawContours(img_contours, [approx], -1, (0, 0, 255), 2)
            for p in approx:
                x, y = p[0]
                cv2.circle(img_contours, (x, y), 6, (0, 255, 0), -1)

    # build text for vertices
    if g.approx is not None:
        num_vertices = len(g.approx)
        text = f"Detected Vertices: {num_vertices}\n"                       + ("Coords:\n" + "\n".join([f"{i+1}: [{int(p[0][0])}, {int(p[0][1])}]" for i,p in enumerate(g.approx)]) if num_vertices <= 100 else "")
    else:
        text = "No vertice detected"

    # preview combine mask and contoured image
    if mask_bgr is None or img_contours is None:
        return None, text, []

    h, w = g.img.shape[:2]
    max_dim = 400
    g.scale_ratio = max_dim / max(h, w)
    new_w, new_h = int(w * g.scale_ratio), int(h * g.scale_ratio)
    mask_small = cv2.resize(mask_bgr, (new_w, new_h))
    cont_small = cv2.resize(img_contours, (new_w, new_h))
    combined = np.hstack((mask_small, cont_small))
    # Convert BGR->RGB for PIL
    combined_rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(combined_rgb)
    return pil, text, contours_list
