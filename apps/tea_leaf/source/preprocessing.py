# app/ml/preprocessing.py

import cv2
import numpy as np

from PIL import Image

from torchvision import transforms


class AdvancedPreprocessing:

    def __init__(self, gamma=1.2):

        self.gamma = gamma

    def __call__(self, img):

        # PIL → NumPy
        arr = np.array(img)

        # RGB → LAB
        lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)

        l, a, b = cv2.split(lab)

        # CLAHE contrast enhancement
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

        l = clahe.apply(l)

        lab = cv2.merge((l, a, b))

        # LAB → RGB
        rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        # Gamma correction
        table = np.array([
            ((i / 255.0) ** (1.0 / self.gamma)) * 255
            for i in range(256)
        ]).astype("uint8")

        rgb = cv2.LUT(rgb, table)

        return Image.fromarray(rgb)


# Create transform ONCE
transform = transforms.Compose([

    transforms.Resize((224, 224)),

    AdvancedPreprocessing(),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.5, 0.5, 0.5],
        std=[0.5, 0.5, 0.5]
    )
])