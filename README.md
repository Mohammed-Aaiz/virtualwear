# 🛍️ VirtualWear — AI Virtual Try-On Platform

An intelligent e-commerce platform that allows users to **virtually try on clothes** based on their identity and preferences.

---

## ✨ Overview

VirtualWear is a next-generation shopping experience where users can:

* 👤 Upload their photo
* 👕 Select clothing from a curated catalog
* 🤖 Instantly visualize how the outfit looks on them

The platform combines **computer vision + AI + personalization** to simulate real-world try-on.

---

## 🎯 Key Features

### 🧥 AI Virtual Try-On

* Upload your image and apply garments
* Real-time cloth alignment and overlay
* Side-by-side comparison (Before vs After)

### 🛍️ Smart Product Catalog

* Dynamically loaded clothing dataset
* Organized by categories (Ethnic, Western, Religious, etc.)
* Clean product grid UI

### 🧠 Recommendation System

* Uses **TF-IDF (scikit-learn)**
* Suggests relevant products based on similarity

### ⚡ Interactive UI

* Built using **Streamlit + Custom HTML UI**
* Wide layout with modern ecommerce feel
* Smooth user interaction

---

## 🧱 Tech Stack

| Layer         | Technology                       |
| ------------- | -------------------------------- |
| Frontend      | Streamlit + HTML/CSS             |
| Backend       | Python                           |
| AI / ML       | OpenCV, PIL, scikit-learn        |
| Try-On Engine | Custom pipeline (pose + overlay) |

---

## 📁 Project Structure

```
ai-virtual-tryon-assessment/
├── ui/
│   └── app.py              # Main Streamlit app
│
├── src/
│   ├── tryon/
│   │   └── pipeline.py     # Try-on engine
│   ├── recommendation/
│   │   └── engine.py       # Recommendation system
│   └── data/
│       └── products.py     # Product dataset
│
├── public/
│   └── image/              # Clothing images dataset
│
├── temp/                   # Generated outputs
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/virtualwear.git
cd virtualwear
```

### 2️⃣ Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4️⃣ Run the app

```bash
streamlit run ui/app.py
```

---

## 🧪 How It Works

1. User uploads an image
2. Selects a clothing product
3. The system:

   * Detects body alignment
   * Resizes garment
   * Applies overlay
4. Final try-on image is generated

---

## ⚠️ Limitations

* Works best with **front-facing images**
* Non-standard garments (e.g., turbans, dhoti) may not align perfectly
* Current system is a **proof-of-concept (not production-level AI)**

---

## 🚀 Future Improvements

* 🔥 Integration with VITON-HD for realistic results
* 🧍 Better body segmentation
* 🛒 Full ecommerce backend (cart, checkout)
* 📱 Mobile-friendly UI

---

## 📸 Demo (Add screenshots here)

> Add screenshots of:
>
> * Product grid
> * Try-on result
> * UI

---

## 👨‍💻 Author

**Aaiz Moh**

---

## ⭐ Final Note

This project demonstrates how AI can transform online shopping into a **personalized and immersive experience**.

---

✨ *From static shopping → to interactive virtual experience*
