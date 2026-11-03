# AgriVision AI 2.0 — Single-Window Studio & Remediation Progress Report

> **Comprehensive remediation of all audit items, Single-Window Studio console redesign, modern typography, async Ajax image submission, analyzed specimen showcase, Zucchini pipeline fix, and Hibiscus prediction system ground truth alignment.**  
> **Status:** ✅ 100% Resolved & Verified | **Automated Tests:** 23/23 Passing  

---

## 🌺 Hibiscus Prediction System: Ground Truth Alignment via `hibiscus.ipynb`

### 1. File Located
- Located training notebook at [`apps/hibiscus/hibiscus.ipynb`](file:///d:/ModelRun/apps/hibiscus/hibiscus.ipynb).

### 2. Discovered Ground Truth & Root Cause
- **Scrambled Class Mapping in Web App:**
  - In `apps/hibiscus/hibiscus.ipynb` (Cell 6 & Cell 12), the dataset was partitioned and trained using `class_names = sorted(os.listdir(data_dir))`.
  - The alphabetical sorting established the exact model output indices:
    - `0`: **Citruspot** (`Citrus Spot`)
    - `1`: **Early_Mild_Spotting** (`Early Mild Spotting`)
    - `2`: **Fungal_Infected** (`Fungal Infected`)
    - `3`: **Healthy** (`Healthy`)
    - `4`: **Mild_Edge_Damage** (`Mild Edge Damage`)
    - `5`: **Senescent** (`Senescent`)
    - `6`: **Slightly_Diseased** (`Slightly Diseased`)
    - `7`: **Wrinkled_Leaf** (`Wrinkled Leaf`)
  - However, the legacy `apps/hibiscus/source/predictor.py` and `config/classes.yaml` had guessed the classes:
    - Index 0 was wrongly assigned to "Mild Edge Damage" (causing Citrus Spot to be labeled Edge Damage).
    - Index 3 was wrongly assigned to "Senescent" (causing healthy leaves to be diagnosed as aging/senescent).
    - Index 7 was wrongly assigned to "Healthy" (causing wrinkled leaves to be diagnosed as healthy).
- **Preprocessing Ground Truth:**
  - Notebook Cell 6 trained with `tf.keras.applications.inception_v3.preprocess_input(img)`, which normalizes RGB pixels to `[-1, 1]` via `(x / 127.5) - 1.0`.
  - This matches `tf.keras.applications.mobilenet_v2.preprocess_input(img)` identically.

### 3. Implemented Fix
1. **Synchronized [`config/classes.yaml`](file:///d:/ModelRun/config/classes.yaml#L3-L48):**
   - Corrected all 8 Hibiscus class indices to strictly match `hibiscus.ipynb` ground truth.
2. **Documented & Verified in [`apps/hibiscus/source/predictor.py`](file:///d:/ModelRun/apps/hibiscus/source/predictor.py):**
   - Configured `preprocess_mode="mobilenet_v2"` (`[-1, 1]`) and documented class index mappings.
3. **Enhanced [`apps/hibiscus/hibiscus.ipynb`](file:///d:/ModelRun/apps/hibiscus/hibiscus.ipynb):**
   - Populated previously empty Cell 16 with a reusable `predict_hibiscus_disease()` function.
4. **Automated Unit Tests in [`apps/common/tests.py`](file:///d:/ModelRun/apps/common/tests.py):**
   - Added assertions verifying the exact ground-truth order of classes loaded for Hibiscus.
   - All 23 tests passing.

---

## 🔬 Zucchini Prediction Pipeline: Root Cause Analysis & Solution

### 1. Root Cause Analysis
- **Model Architecture Mismatch:**
  - `apps/zucchini/source/Zucchini.h5` is an **EfficientNet** model (389 layers).
  - In TensorFlow/Keras, EfficientNet models embed their own preprocessing layers (`Rescaling(1/255)`, `Normalization`, `Rescaling(scale=...)`) inside the graph.
  - EfficientNet models strictly expect **raw RGB pixel values in `[0, 255]` (float32)**.
  - The legacy implementation applied `resnet50.preprocess_input(arr)`, which flips RGB to BGR and subtracts ImageNet means `[103.939, 116.779, 123.68]`, resulting in negative numbers that corrupted model activations.
- **Missing / Placeholder Class Labels:**
  - The legacy code contained raw digits `'1'`, `'4'`, `'5'`, `'7'` in `CLASSES`.

### 2. Implemented Fix
1. **Multi-Architecture Preprocessing Engine in [`apps/common/predictor.py`](file:///d:/ModelRun/apps/common/predictor.py):**
   - Added `preprocess_mode` support to `BasePredictor` (`'raw'`, `'mobilenet_v2'`, `'resnet50'`, and dynamic `'auto'`).
2. **Standardized Predictor Instances:**
   - Configured `apps/zucchini/source/predictor.py` with `preprocess_mode="raw"`.
3. **Comprehensive Zucchini Taxonomy in [`config/classes.yaml`](file:///d:/ModelRun/config/classes.yaml):**
   - Resolved all 9 Cucurbit disease classes with treatments and descriptions.

---

## 🖥️ Executive Overview: Studio Console

1. **Contained Single-Window Workspace:** The entire interaction workflow is contained in **one unified window view (`100vh`)**.
2. **Unified Navigation Topbar:** Combined brand logo, active engine indicator, and crop switcher tabs (`🌺 Hibiscus`, `🍃 Zucchini`, `🍵 Tea Leaf`, `🍈 Papaya`) into a compact 58px header.
3. **Left Console (Input & Telemetry, 410px):**
   - Compact dropzone with instant drag-and-drop.
   - Specimen preview with quick file replace.
   - Fast "Run Neural Diagnosis" action button.
   - Photography quality chips (*Even Light*, *Center Spot*, *Sharp Focus*).
   - Detectable pathologies pill cloud.
4. **Right Console (Diagnostic Monitor & Report, 1fr):**
   - **Idle State:** Sleek botanical reticle awaiting user input.
   - **Scanning State:** In-place animated radar scanner with rotating beam and progress bar.
   - **Diagnosis Report:** Top dark pathology banner, side-by-side **analyzed leaf image showcase** with verified specimen stamp, confidence score gauge, condition description, agronomic prescription card, and alternative probabilities mini-bars.
5. **23 Automated Unit Tests:** 100% pass rate in [`apps/common/tests.py`](file:///d:/ModelRun/apps/common/tests.py).

---

## 🔬 Automated Test Run (23/23 Passing)

```
$ python manage.py test
Found 23 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......................
----------------------------------------------------------------------
Ran 23 tests in 12.726s

OK
Destroying test database for alias 'default'...
```
