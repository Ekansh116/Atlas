# ATLAS — Lunar Image Correspondence

ATLAS (Automated Feature Matching and Registration for Lunar Remote Sensing) is an ongoing research-oriented framework designed for feature matching, geometric registration, and spatial correspondence across lunar surface imagery.

> **Project Status Notice:** ATLAS is an ongoing research project. The current implementation establishes a classical SIFT-based correspondence and geometric-registration baseline, while multimodal Chandrayaan-2 correspondence remains an active research direction.

---

## Research Problem

Lunar image correspondence is a fundamental computer vision challenge in planetary remote sensing, essential for topographic mapping, landing site selection, change detection, and orbital SLAM. The project addresses the **Smart India Hackathon (SIH) 2026** problem statement:

> *"Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS)."*

### Key Technical Challenges in Lunar Remote Sensing

1. **Extreme Illumination & Sun-Angle Variation:** High solar zenith angles create long, non-linear shadows and dramatic albedo reversals across different orbital passes.
2. **Scale & Resolution Disparities:** Images acquired at varying orbital altitudes exhibit distinct spatial resolutions (ground sampling distances).
3. **Viewpoint & Relief Distortions:** Non-nadir viewing angles combined with high lunar terrain relief cause severe perspective distortion and local parallax errors.
4. **Cross-Modal Imaging (OHRC / TMC / IIRS):**
   - **OHRC (Optical High Resolution Camera):** Ultra-high spatial resolution (~0.25 m/pixel) Panchromatic imagery.
   - **TMC (Terrain Mapping Camera-2):** Stereo Panchromatic imagery (~5 m/pixel) for 3D DEM generation.
   - **IIRS (Imaging Infra-Red Spectrometer):** Hyperspectral imagery (0.8–5.0 µm) with lower spatial resolution (~80 m/pixel) but rich mineralogical data.
   Corresponding features across optical, stereo, and hyperspectral modalities requires bridging large spectral and structural domain gaps.

---

## Current Status

ATLAS is being developed incrementally. To avoid conflating future research goals with functional code, repository capabilities are explicitly categorized below:

| Feature / Component | Status Tag | Description |
| :--- | :--- | :--- |
| **Classical SIFT Correspondence** | `[Implemented]` | SIFT keypoint detection, descriptor extraction, FLANN KD-tree matching, ratio testing, and mutual consistency filtering. |
| **Geometric Verification & Alignment** | `[Implemented]` | RANSAC homography estimation ($H$), point transformation, spatial warping, and diagnostic output generation. |
| **In-Sample Residual Analysis** | `[Implemented]` | Mean, Median, Max reprojection error, and RMSE metric calculations on RANSAC inlier keypoints. |
| **Illumination-Adaptive Preprocessing** | `[In Progress]` | Contrast enhancement (CLAHE) and multi-scale normalization for shadowed crater regions. |
| **Lunar Ground-Truth Evaluation Benchmark** | `[Planned / Research Direction]` | Evaluation framework using synthetic lunar renders and DEM-derived ground-truth control points (GCPs). |
| **Cross-Modal (OHRC / TMC / IIRS) Matching** | `[Planned / Research Direction]` | Modality-invariant joint descriptors and dense feature transformers for cross-sensor registration. |
| **Learned Feature Extraction & Matching** | `[Planned / Research Direction]` | Deep self-supervised models (e.g., SuperPoint/LoFTR adaptions) trained on planetary surface datasets. |

---

## Implemented Correspondence Pipeline

The current baseline is a deterministic computer vision pipeline implemented in [`sift_match.py`](file:///C:/Users/ekansh/Desktop/sift-feature-matching/sift_match.py).

```text
Input Image Pair (image1.jpg, image2.jpg)
         ↓
Grayscale Conversion (cv2.cvtColor)
         ↓
SIFT Feature Extraction (nfeatures=5000, nOctaveLayers=4, contrastThreshold=0.025, edgeThreshold=10, sigma=1.6)
         ↓
FLANN KD-Tree Matching (10 trees, 500 checks, k=2, forward & backward)
         ↓
Lowe Ratio Test (distance threshold ratio = 0.65)
         ↓
Mutual / Bidirectional Consistency Filtering (Cross-check verification)
         ↓
Candidate Selection (Top 500 mutual matches sorted by descriptor distance)
         ↓
RANSAC Homography Estimation (reprojThreshold=3.0px, maxIters=5000, confidence=0.995)
         ↓
Inlier Extraction & Reprojection Residual Calculation (Mean, Median, Max, RMSE)
         ↓
Perspective Warping & Spatial Alignment (cv2.warpPerspective)
         ↓
Visual Diagnostic Generation (Keypoints, Inlier Match Lines, 50/50 Overlay, Normalized Difference Map, Matrix Export)
```

### Exact Pipeline Parameters (Verified from Source Code)

- **SIFT Detector Configuration:**
  - Max Features (`nfeatures`): `5000`
  - Octave Layers (`nOctaveLayers`): `4`
  - Contrast Threshold (`contrastThreshold`): `0.025`
  - Edge Threshold (`edgeThreshold`): `10`
  - Sigma (`sigma`): `1.6`
- **FLANN Matcher Configuration:**
  - Index Algorithm: `FLANN_INDEX_KDTREE` (1)
  - Number of KD-Trees (`trees`): `10`
  - Search Checks (`checks`): `500`
  - Nearest Neighbors (`k`): `2`
- **Filtering & Verification Parameters:**
  - Lowe Distance Ratio Threshold (`ratio`): `0.65`
  - Mutual Consistency Check: Bidirectional validation ($\text{trainIdx} \leftrightarrow \text{queryIdx}$)
  - Max Geometric Candidates (`MAX_CANDIDATES`): Top `500` mutual matches
  - Minimum Match Threshold: Requires $\ge 4$ candidates for homography estimation
- **RANSAC Homography Parameters:**
  - Reprojection Error Threshold: `3.0` pixels
  - Max Iterations (`maxIters`): `5000`
  - Confidence Level (`confidence`): `0.995`

---

## Scientific Wording & Technical Scope

To maintain academic and scientific precision:
- **What SIFT provides:** Scale-space local feature detection and descriptor orientation normalization, offering local scale and rotational invariance under moderate appearance shifts.
- **What the current baseline does NOT claim:** The current baseline script is **not** fully invariant to extreme Sun-angle changes (where shadow orientation flips feature gradients), large perspective distortions across high lunar terrain relief, or multi-sensor modality differences.
- **Research Goal:** The broader mission of ATLAS is to develop novel algorithms, hybrid classical/deep descriptors, and multi-sensor alignment pipelines capable of true invariance across Chandrayaan-2 OHRC, TMC, and IIRS datasets.

---

## Baseline Results & Visual Diagnostics

Executing [`sift_match.py`](file:///C:/Users/ekansh/Desktop/sift-feature-matching/sift_match.py) produces visual and numerical diagnostics in the [`outputs/`](file:///C:/Users/ekansh/Desktop/sift-feature-matching/outputs) directory.

### Visual Diagnostics

- **Keypoint Detection Maps (`outputs/keypoints_image1.jpg`, `outputs/keypoints_image2.jpg`):** Visualizes rich SIFT keypoints with size and orientation indicators across both input frames.
- **Verified Inlier Matches (`outputs/final_matches.jpg`):** Displays keypoint correspondences validated by bidirectional ratio testing and RANSAC homography filtering.
- **Aligned Image (`outputs/aligned_image.jpg`):** Perspective transformation of Image 1 warped into the coordinate space of Image 2 using matrix $H$.
- **Alignment Overlay (`outputs/alignment_overlay.jpg`):** 50/50 alpha-blended composition of the warped image and reference image to evaluate visual alignment.
- **Normalized Difference Image (`outputs/difference.jpg`):** Pixel-wise absolute intensity difference ($\vert I_{\text{aligned}} - I_2 \vert$) normalized for diagnostic inspection of local residual disparities and illumination variations.
- **Homography Matrix (`outputs/homography.txt`):** Formatted $3 \times 3$ transformation matrix stored for downstream geospatial mapping.

### Sample Baseline Metrics (Single Pair Execution)

```text
================ MATCH RESULTS ================
Keypoints image 1    : 5001
Keypoints image 2    : 5001
Ratio-test matches   : 4688
Mutual matches       : 4677
RANSAC candidates    : 500
Final valid matches   : 500
Inlier ratio         : 100.00%

================ GEOMETRIC ACCURACY ================
Mean reprojection error   : 0.00 pixels
Median reprojection error : 0.00 pixels
Maximum reprojection error: 0.00 pixels
RMSE                      : 0.00 pixels
```

---

## Evaluation Metrics & Methodological Nuance

### Terminology & Metric Definitions

1. **RANSAC Inliers:** Keypoint pairs satisfying the homography constraint within the $3.0\text{ px}$ threshold. *Note: RANSAC inliers are geometrically consistent match candidates under the estimated model, not independently verified ground-truth matches.*
2. **Inlier Ratio:** Ratio of RANSAC inliers to candidate matches ($\frac{N_{\text{inliers}}}{N_{\text{candidates}}}$).
3. **Reprojection Residual (Mean, Median, Max, RMSE):** Euclidean distance between transformed source points ($H \cdot p_{\text{src}}$) and target points ($p_{\text{dst}}$).

> [!NOTE]
> **In-Sample Residual Distinction:** Reprojection errors calculated on RANSAC-selected inliers reflect the internal geometric residual of the fitted $3 \times 3$ homography matrix. They quantify model fitting consistency on selected points rather than absolute registration accuracy against independent ground-truth Control Points (GCPs) or Digital Elevation Models (DEMs). An explicit ground-truth evaluation benchmark is a planned research direction.

---

## Limitations of Current Implementation

- **Planar Homography Approximation:** Homography modeling ($H \in \mathbb{R}^{3 \times 3}$) assumes a planar surface or zero-parallax camera rotation. High-relief lunar structures (crater rims, central peaks) introduce local parallax errors that a global 2D homography cannot resolve.
- **Illumination Sensitivity:** SIFT relies on image intensity gradients. Extreme Sun angle shifts induce moving shadows and gradient reversals, reducing descriptor repeatability.
- **Monocular / Monomodal Limitation:** The current pipeline operates on single-channel grayscale optical images and does not yet handle cross-modal spectral differences (e.g., registering optical OHRC to infrared IIRS).
- **Difference Map Interpretation:** The normalized difference image is a qualitative visual diagnostic reflecting both geometric misalignments and intrinsic radiometry/lighting variations.

---

## Project Structure

```text
Atlas/
├── images/
│   ├── image1.jpg             # Input image 1 (Reference or Search image)
│   └── image2.jpg             # Input image 2 (Target image)
├── outputs/                   # Generated diagnostic outputs
│   ├── aligned_image.jpg      # Warped Image 1 aligned to Image 2 space
│   ├── alignment_overlay.jpg  # 50/50 alpha blend of aligned and target image
│   ├── difference.jpg         # Normalized absolute pixel difference map
│   ├── final_matches.jpg      # RANSAC-verified match line visualization
│   ├── homography.txt         # Saved 3x3 homography matrix (ASCII text)
│   ├── keypoints_image1.jpg   # Keypoints overlay on image 1
│   └── keypoints_image2.jpg   # Keypoints overlay on image 2
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
├── requirements.txt           # Python package dependencies
└── sift_match.py              # Main classical SIFT correspondence & registration pipeline
```

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- `opencv-python` $\ge 4.5.0$
- `numpy` $\ge 1.20.0$

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/Ekansh116/Atlas.git
cd Atlas

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

Place input images in the `images/` directory as `image1.jpg` and `image2.jpg`, then run:

```bash
python sift_match.py
```

All diagnostic visual outputs and the transformation matrix will be automatically generated in the `outputs/` directory.

---

## Research Roadmap

The development of ATLAS follows a structured, multi-phase research progression:

```text
Phase 1: Classical Baseline [Implemented]
  └── SIFT + FLANN + Mutual Consistency + RANSAC Homography
         ↓
Phase 2: Illumination & Contrast Enhancements [In Progress]
  ├── CLAHE & adaptive illumination normalization
  └── ASIFT / Affine-robust feature evaluation
         ↓
Phase 3: Lunar-Specific Ground-Truth Evaluation Framework [Planned]
  ├── DEM-synthesized ground-truth validation pairs
  └── Independent GCP residual & RMSE evaluation metrics
         ↓
Phase 4: Cross-Modal Correspondence (OHRC / TMC / IIRS) [Planned]
  ├── Edge-oriented gradient and phase congruency structural descriptors
  └── Co-registration across optical, stereo DEM, and hyperspectral bands
         ↓
Phase 5: Learned Feature Extraction & Transformer Matchers [Planned]
  ├── Self-supervised planetary feature representation learning
  └── Dense semi-dense transformer matchers (e.g., LoFTR / LightGlue adaptions)
```

---

## Contributing

Contributions from researchers and developers in planetary remote sensing, computer vision, and photogrammetry are welcome. Please open an issue to discuss proposed feature additions, bug reports, or algorithmic improvements before submitting pull requests.

---

## License

This project currently does not contain an explicit open-source license file. All rights are reserved by the original author ([@Ekansh116](https://github.com/Ekansh116)). Licensing terms for open-source research distribution will be added in future releases.

---

## References

1. **Lowe, D. G. (2004).** Distinctive image features from scale-invariant keypoints. *International Journal of Computer Vision*, 60(2), 91-110.
2. **Fischler, M. A., & Bolles, R. C. (1981).** Random sample consensus: a paradigm for model fitting with applications to image analysis and automated cartography. *Communications of the ACM*, 24(6), 381-395.
3. **Muja, M., & Lowe, D. G. (2009).** Fast Approximate Nearest Neighbors with Automatic Algorithm Configuration. *VISAPP (1)*, 2(331-340), 2.
4. **ISRO (2019).** Chandrayaan-2 Mission and Payloads (OHRC, TMC-2, IIRS). *Indian Space Research Organisation*.
