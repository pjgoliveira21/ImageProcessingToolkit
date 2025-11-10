"""Shared global state for the application.
Keep this module small: it's used to share the current images and popup windows
between UI code and core processing without scattering many globals across files.
"""
from typing import Optional
import numpy as np

# Images and processing state
img: Optional[np.ndarray] = None
approx: Optional[np.ndarray] = None
transformed_img: Optional[np.ndarray] = None

# UI helpers/state
scale_ratio: float = 1.0
popup_window = None
contours_list = []
root = None
