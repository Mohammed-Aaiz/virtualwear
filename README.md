# 🛍️ CommunityCart AI — Virtual Try-On Assessment

> AI-powered virtual try-on, body measurement estimation, and community-based product recommendation system built for a multi-community e-commerce platform.

---

## 📁 Project Structure

```
ai-virtual-tryon-assessment/
│
├── ui/                         # Streamlit frontend
│   └── app.py                  # Main UI with 3 tabs
│
├── src/                        # Backend modules
│   ├── tryon/
│   │   ├── pipeline.py         # Task 1 — Virtual Try-On
│   │   └── classifier.py       # Task 4 — Garment Classifier (Bonus)
│   ├── measurement/
│   │   └── estimator.py        # Task 2 — Body Measurement
│   └── recommendation/
│       └── engine.py           # Task 3 — Recommendation Engine
│
├── notebooks/                  # Demo notebooks
├── data/
│   └── products.csv            # 55 community products dataset
├── outputs/                    # Generated try-on results
│
├── main.py                     # CLI runner (optional)
├── requirements.txt
└── README.md
```

---

## ⚙️ How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit UI
```bash
streamlit run ui/app.py
```

### 3. Or use the CLI runner
```bash
# Virtual Try-On
python main.py --task tryon --person data/person.jpg --garment data/garment.jpg

# Body Measurements
python main.py --task measure --image data/person.jpg --height 170

# Recommendations
python main.py --task recommend --community Muslim

# Garment Classifier (Bonus)
python main.py --task classify --image data/garment.jpg
```

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|-----------|
| Pose Detection | MediaPipe (33 body landmarks) |
| Background Removal | rembg (U²-Net model) |
| Image Processing | OpenCV, Pillow, NumPy |
| Garment Classifier | CLIP (openai/clip-vit-base-patch32) |
| Recommendation Engine | TF-IDF + Cosine Similarity (scikit-learn) |
| Frontend | Streamlit |
| Data | Pandas |

---

## 📋 Tasks Completed

- ✅ Task 1 — Virtual Try-On (background removal + pose detection + garment overlay)
- ✅ Task 2 — Body Measurement Estimation (shoulder width, torso length, hip width, size)
- ✅ Task 3 — Product Recommendation Engine (community filter + TF-IDF + rating boost)
- ✅ Task 4 — Garment Classifier using CLIP (Bonus)

---

## ❓ README Questions

### 1. What approach did you take for garment overlay and why?

I used a **landmark-based affine overlay approach** with the following steps:

1. **Background removal** — `rembg` (U²-Net) removes backgrounds from both the person photo and garment image, producing clean RGBA images.
2. **Pose detection** — MediaPipe detects 33 body landmarks. I extract shoulder (left/right) and hip (left/right) keypoints.
3. **Garment sizing** — Garment width is set to 1.5× the shoulder-to-shoulder pixel distance. Garment height is set to 1.6× the shoulder-to-hip pixel distance to cover the torso naturally.
4. **Overlay positioning** — The garment is placed starting from the shoulder line using alpha compositing via PIL's `paste()` with the garment's own alpha channel as a mask.

I chose this approach because it requires no training data, works with any garment image, and produces results in seconds using only CPU. It is a solid proof-of-concept that demonstrates the full pipeline clearly.

---

### 2. What were the biggest challenges you faced?

- **Garment warping** — Simple resizing doesn't account for body contours or pose variations. The garment appears flat rather than naturally draped.
- **Sleeve alignment** — MediaPipe provides wrist/elbow landmarks but aligning sleeves accurately requires dense flow estimation, not available in this approach.
- **Background blending** — When the person image has a complex background, rembg occasionally leaves edge artifacts that affect overlay quality.
- **Scale estimation for measurements** — Body measurement accuracy depends heavily on the quality and angle of the input photo. Side-angle or tilted photos reduce accuracy significantly.

---

### 3. What does not work well in the current solution?

- The garment overlay is a **flat rectangular warp** — it does not follow the body's 3D curves or fabric physics.
- **Sleeve regions** are not handled — only the torso area is covered.
- The overlay can look unnatural when the person's arms are not at their sides.
- Body measurement estimates have **±10–20% error** due to perspective distortion in 2D photos.
- The garment classifier works best with clean product images on white backgrounds; real-world photos reduce confidence.

---

### 4. If you had 2 weeks instead of 72 hours, what would you build differently?

- **Better Try-On**: Implement a thin-plate spline (TPS) warping step to deform the garment to match body contours instead of simple affine scaling.
- **Sleeve handling**: Use elbow and wrist landmarks to separately warp sleeve regions.
- **Segmentation**: Add a segmentation model (SAM or DeepLab) to separate the torso region and blend the garment only within that mask — avoiding the rectangular cutout look.
- **Training data**: Collect paired (person, garment, result) images to fine-tune the warping model.
- **More products**: Expand the dataset to 500+ products with real images and richer tag taxonomies.
- **User accounts**: Add login so preferences and past purchases persist across sessions.
- **Mobile-optimized UI**: Build a React Native front end for the mobile app mentioned in the brief.

---

### 5. What production-grade models would you use for real deployment?

| Component | Production Model | Why |
|-----------|-----------------|-----|
| Virtual Try-On | **VITON-HD** or **DCI-VTON** | Dense flow field warping, handles fabric folds and body contours |
| Try-On (Gen AI) | **Stable Diffusion Inpainting** with ControlNet | Photorealistic results, handles complex garments |
| Background Removal | **SAM (Segment Anything Model)** by Meta | More precise segmentation than U²-Net |
| Pose Estimation | **ViTPose** or **OpenPose** | More accurate landmarks, handles occlusions |
| Garment Classifier | **CLIP ViT-L/14** or fine-tuned **ResNet-50** | Higher accuracy on fashion domain |
| Recommendation | **Two-Tower Neural CF** + **BM25** for tag matching | Handles cold-start and scales to millions of products |

For the full production pipeline, I would use **VITON-HD** for try-on quality, **SAM** for segmentation, and a **Two-Tower model** for recommendations — deployed on GPU instances with Redis caching for real-time response.

---

## 🎨 Brand Guidelines Applied

- Primary Color: Deep Navy `#0D1B2A`
- Accent / Gold: `#C9A84C`
- Background: `#F9F7F4`
- Fonts: Playfair Display (headings) + Inter (body)
- Feel: Premium, Trustworthy, Warm, Inclusive

---

## 👨‍💻 Author

**Mohammed Aaiz**
B.Tech AIML — Anjuman Institute of Technology and Management, Bengaluru
GitHub: [github.com/Mohammed-Aaiz](https://github.com/Mohammed-Aaiz)
