import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from utils import globals as g

def analyze_and_show(parent):
    """Analyze g.transformed_img using a simple color-based 4x4 grid and show results in popups."""
    if g.transformed_img is None:
        print("[ERRO] Nenhuma imagem transformada disponível.")
        return
    hsv = cv2.cvtColor(g.transformed_img, cv2.COLOR_BGR2HSV)
    tamanho = 500
    blocos = 4
    passo = tamanho // blocos
    matriz = np.zeros((blocos, blocos), dtype=int)

    # color ranges tuned similarly to the original script
    vermelho1_inf = np.array([0, 80, 60])
    vermelho1_sup = np.array([15, 255, 255])
    vermelho2_inf = np.array([160, 80, 60])
    vermelho2_sup = np.array([179, 255, 255])
    branco_inf = np.array([0, 0, 160])
    branco_sup = np.array([179, 60, 255])

    for i in range(blocos):
        for j in range(blocos):
            x0, y0 = j * passo, i * passo
            x1, y1 = x0 + passo, y0 + passo
            regiao = hsv[y0:y1, x0:x1]
            mask_red1 = cv2.inRange(regiao, vermelho1_inf, vermelho1_sup)
            mask_red2 = cv2.inRange(regiao, vermelho2_inf, vermelho2_sup)
            mask_red = cv2.bitwise_or(mask_red1, mask_red2)
            mask_white = cv2.inRange(regiao, branco_inf, branco_sup)
            count_red = cv2.countNonZero(mask_red)
            count_white = cv2.countNonZero(mask_white)
            total = regiao.shape[0] * regiao.shape[1]
            frac_red = count_red / total
            frac_white = count_white / total
            if frac_red > 0.2 and frac_red > frac_white:
                matriz[i, j] = 1
            elif frac_white > 0.2 and frac_white > frac_red:
                matriz[i, j] = 0
            else:
                matriz[i, j] = -1

    # draw annotations on a copy for visual feedback
    img_grade = g.transformed_img.copy()
    for k in range(1, blocos):
        cv2.line(img_grade, (0, k*passo), (tamanho, k*passo), (255, 255, 0), 1)
        cv2.line(img_grade, (k*passo, 0), (k*passo, tamanho), (255, 255, 0), 1)
    for i in range(blocos):
        for j in range(blocos):
            x = j * passo + passo // 2
            y = i * passo + passo // 2
            val = matriz[i, j]
            cor = (0, 255, 0) if val == 1 else (255, 255, 255) if val == 0 else (0, 0, 255)
            cv2.putText(img_grade, str(val), (x - 15, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)

    # small popup with annotated grid and text
    popup = tk.Toplevel(parent)
    popup.title("Análise do Puzzle 4x4")
    rgb = cv2.cvtColor(img_grade, cv2.COLOR_BGR2RGB)
    imgtk = ImageTk.PhotoImage(Image.fromarray(rgb))
    label = tk.Label(popup, image=imgtk, bg="#1e1e1e")
    label.image = imgtk
    label.pack(padx=10, pady=10)
    texto = "\n".join([" ".join([f"{x:2d}" for x in linha]) for linha in matriz])
    lbl = tk.Label(popup, text=texto, font=("Consolas", 12), bg="#1e1e1e", fg="white")
    lbl.pack(pady=10)

    # create a second popup with a generated aruco-like image (black/white)
    bloco_size = 175
    img_size = bloco_size * blocos
    aruco_img = np.zeros((img_size, img_size), dtype=np.uint8)
    for i in range(blocos):
        for j in range(blocos):
            y0, y1 = i * bloco_size, (i + 1) * bloco_size
            x0, x1 = j * bloco_size, (j + 1) * bloco_size
            if matriz[i, j] == 1:
                aruco_img[y0:y1, x0:x1] = 0
            else:
                aruco_img[y0:y1, x0:x1] = 255
    aruco_bgr = cv2.cvtColor(aruco_img, cv2.COLOR_GRAY2BGR)
    popup2 = tk.Toplevel(parent)
    popup2.title("Aruco 1000x1000")
    rgb_aruco = cv2.cvtColor(aruco_bgr, cv2.COLOR_BGR2RGB)
    imgtk_aruco = ImageTk.PhotoImage(Image.fromarray(rgb_aruco))
    label2 = tk.Label(popup2, image=imgtk_aruco, bg="#1e1e1e")
    label2.image = imgtk_aruco
    label2.pack(padx=10, pady=10)
    return matriz
