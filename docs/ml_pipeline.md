# Machine Learning Pipeline & Architectural Analysis

## 1. Overview

AgrivisionAI / PlantMD deploys deep convolutional neural network (CNN) classifiers to detect, diagnose, and prescribe treatments for agricultural plant pathologies. This document formalizes the ML pipeline, analyzes preprocessing requirements, documents known architecture specifications, and outlines production guidelines for model consistency.

---

## 2. Model Specifications & Output Signatures

| Plant Disease Model | Target Input Shape | Architecture Base | Output Classes | Activation | Artifact Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hibiscus** | `(1, 224, 224, 3)` | ResNet50 (Transfer Learning) | 8 | Softmax | `apps/hibiscus/source/model.h5` |
| **Zucchini** | `(1, 224, 224, 3)` | ResNet50 / DenseNet | 9 | Softmax | `apps/zucchini/source/Zucchini.h5` |
| **Tea Leaf** | `(1, 224, 224, 3)` | ResNet50 / DenseNet-ViT Fusion | 8 | Softmax | `apps/tea_leaf/source/Tea leaf.h5` |
| **Papaya** | `(1, 224, 224, 3)` | ResNet50 / MobileNetV2 | 8 | Softmax | `apps/papaya/source/Papaya.h5` |

---

## 3. Preprocessing Analysis & Training/Deployment Alignment

### 3.1 Standard ResNet50 Preprocessing (Current Deployment Pipeline)
The active production pipeline preprocesses uploaded images via:
1. **RGB Conversion:** Converts uploaded images from arbitrary channels (RGBA, Grayscale, CMYK) to standard 3-channel RGB.
2. **Resizing:** Bilinear interpolation to target resolution `(224, 224)`.
3. **ResNet Preprocessing (`tf.keras.applications.resnet50.preprocess_input`):**
   - Zero-centers RGB channels with respect to the ImageNet dataset (subtracting ImageNet mean `[103.939, 116.779, 123.68]`).
   - Converts RGB channel ordering to BGR.

### 3.2 Advanced Preprocessing Pipeline (Discovered in `apps/tea_leaf/source/preprocessing.py`)
The repository contains an advanced computer-vision preprocessing pipeline for tea leaves:
- **RGB to LAB Color Space Conversion:** Separates lightness from chromatic channels.
- **CLAHE (Contrast Limited Adaptive Histogram Equalization):**
  - `clipLimit=2.0`, `tileGridSize=(8, 8)` applied on the L-channel to highlight subtle leaf fungal spots under varying lighting conditions.
- **Gamma Correction:**
  - Nonlinear brightness adjustment with $\gamma = 1.2$ applied via Look-Up Table (LUT).
- **PyTorch Normalization:**
  - Standardized to `mean=[0.5, 0.5, 0.5]`, `std=[0.5, 0.5, 0.5]`.

> [!IMPORTANT]
> **Production Recommendation:** If tea leaf weights were trained using CLAHE and gamma correction, using standard ResNet preprocessing causes feature drift and degrades accuracy. If deploying the PyTorch `DenseNet201_FusionViT_Advanced` checkpoint, use `apps/tea_leaf/source/preprocessing.py`. If deploying the Keras `.h5` model, ensure the preprocessing matches the Keras training script.

---

## 4. Softmax vs. Logits Safeguard

In production deep learning, models might export raw unnormalized logits or normalized probabilities. If a model exports logits, computing `confidence = max(preds) * 100` produces invalid percentages.

The shared `BasePredictor` in `apps/common/predictor.py` implements a mathematically verified softmax safeguard:

```python
def apply_softmax_if_needed(preds: np.ndarray) -> np.ndarray:
    total_prob = float(np.sum(preds))
    # If the output does not sum to ~1.0, it represents raw logits
    if not (0.95 <= total_prob <= 1.05):
        shifted = preds - np.max(preds, axis=-1, keepdims=True)
        exp_preds = np.exp(shifted)
        preds = exp_preds / np.sum(exp_preds, axis=-1, keepdims=True)
    return preds
```

This guarantees:
1. Numerical stability against overflow ($e^x$).
2. Valid probability distributions summing strictly to 1.0 ($100\%$).
3. Zero risk of crashing if the training export format changes.

---

## 5. Model File Naming & Directory Standardization

Previously, models used inconsistent naming conventions:
- `apps/hibiscus/source/model.h5`
- `apps/zucchini/source/Zucchini.h5`
- `apps/tea_leaf/source/Tea leaf.h5` (with space)
- `apps/papaya/source/Papaya.h5`

### Standard Resolution Order
The `BasePredictor` now resolves model paths dynamically using a standardized resolution chain:
1. `apps/<plant_key>/source/<plant_key>_model.h5` (Standard convention)
2. `apps/<plant_key>/source/<PlantKey>.h5`
3. `apps/<plant_key>/source/model.h5`
4. `apps/<plant_key>/source/<Plant Key with spaces>.h5`

This ensures full backwards compatibility while establishing a clean standard for future model additions.

---

## 6. Hybrid PyTorch & Keras Architecture (`apps/tea_leaf`)

The tea leaf module includes `apps/tea_leaf/source/architecture.py`, defining a dual-branch Attention Fusion network:
- **CNN Branch:** `DenseNet201` for localized fine-grained texture extraction.
- **Vision Transformer Branch:** `vit_base_patch16_224` for global spatial relationship encoding.
- **Attention Fusion:** Learnable multi-layer perceptron generating adaptive weighting between CNN and Transformer feature representations.

For production deployment of this architecture:
1. Export trained PyTorch weights to ONNX (`torch.onnx.export`).
2. Run via ONNX Runtime for CPU acceleration or compile to TensorRT for GPU serving.

---

## 7. Model Monitoring & Logging

All debug `print()` statements across predictors have been replaced with standard structured Python logging:
- `logger.info()` logs inference metadata, predicted class, and confidence score.
- `logger.debug()` logs full class score distributions.
- `logger.error()` captures stack traces without causing 500 server errors.
- Logs rotate automatically at 5MB in `logs/django.log` (5 backups retained).
