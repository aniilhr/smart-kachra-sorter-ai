# ♻️ Smart Kachra Sorter AI

**AI-powered waste segregation assistant for smarter, cleaner Indian cities.**

Upload a photo of an item and instantly get its Indian municipal waste category, a confidence score, the correct disposal bin, recycling guidance, and its environmental impact — powered by a computer-vision model, not a chatbot wrapper.

Built for **Idea2Impact 2026** · Theme 2: Clean & Green Technology

[![Live Demo](https://img.shields.io/badge/demo-live-10B981?style=for-the-badge)](https://smart-kachra-sorter-ai.onrender.com/)
[![GitHub](https://img.shields.io/badge/github-repo-2563EB?style=for-the-badge&logo=github)](https://github.com/aniilhr/smart-kachra-sorter-ai)

🔗 **Live app:** https://smart-kachra-sorter-ai.onrender.com/
📦 **Repository:** https://github.com/aniilhr/smart-kachra-sorter-ai

> ⏳ First load may take ~30–50 seconds — the free hosting tier spins down when idle and needs a moment to wake up.

---

## 📖 Table of Contents

- [Problem](#-problem)
- [Solution](#-solution)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Dataset](#-dataset)
- [AI Model](#-ai-model)
- [Waste Categories & Disposal Guide](#-waste-categories--disposal-guide)
- [Project Structure](#-project-structure)
- [Run Locally](#-run-locally)
- [Deployment](#-deployment)
- [Known Limitations & Future Work](#-known-limitations--future-work)
- [Engineering Notes](#-engineering-notes)
- [License](#-license)

---

## 🧩 Problem

India's municipal waste rules (Swachh Bharat Mission) require households to segregate waste into **wet** and **dry** streams at source, but most people don't reliably know which bin an item belongs in — especially for ambiguous materials like broken glass, mixed plastics, or soiled paper.

Wrongly-mixed waste is a leading cause of landfill methane emissions and makes downstream recycling far less effective. Most existing waste-classification tools are also trained on **Western recycling categories** (single-stream "recyclable vs. trash") that don't match how Indian civic bodies actually ask citizens to segregate waste.

## 💡 Solution

Smart Kachra Sorter lets you **upload or capture a photo** of an item and get, in seconds:

- The correct **Indian waste category** (wet waste, or dry waste by material type)
- A **confidence score** plus top-3 alternative predictions, for basic interpretability
- The **correct bin color**, disposal method, recycling tip, safety precaution, and environmental impact

The AI model is the core of the product — classification runs through a real, trained computer-vision model. Disposal guidance is deterministic reference data rather than an LLM guessing at safety-relevant instructions.

## ✨ Features

- 📤 **Image upload & camera capture** — drag-and-drop or snap a photo directly
- 🧠 **Real-time AI classification** into 6 waste categories with confidence scoring
- 📊 **Top-3 predictions** shown as progress bars for basic model transparency
- ♻️ **Disposal guide** — method, recycling tip, and safety precaution per category
- 🌱 **Environmental impact card** — why segregating this item actually matters
- 📈 **Session dashboard** — live donut chart + per-category scan counts
- 🎨 Clean, dark, dashboard-style UI (no default Gradio look)

## ⚙️ How It Works

```
User uploads/captures a photo
            │
            ▼
   Preprocess (resize to 224×224)
            │
            ▼
  MobileNetV2 (frozen, ImageNet weights)
     + custom classification head
            │
            ▼
   Softmax prediction over 6 classes
            │
            ▼
  disposal_guide.py (deterministic lookup)
            │
            ▼
 Result: category, confidence, top-3,
 bin color, disposal + impact info
```

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Model | TensorFlow / Keras, MobileNetV2 (transfer learning) |
| App / UI | Gradio (custom dark theme, HTML/CSS cards) |
| Training | Google Colab (free GPU) |
| Deployment | Render (Web Service) |
| Language | Python |

## 📊 Dataset

Two public datasets merged and remapped to Indian waste categories:

1. [Garbage Classification](https://www.kaggle.com/datasets/asdasdasasdas/garbage-classification) — cardboard, glass, metal, paper, plastic, trash
2. [Waste Classification Data](https://www.kaggle.com/datasets/techsash/waste-classification-data) — organic subset used to build the wet-waste class

See [`train_model.py`](train_model.py) for the exact merge and training pipeline.

## 🧠 AI Model

- **Base:** MobileNetV2 pretrained on ImageNet, frozen (feature extractor)
- **Head:** GlobalAveragePooling → Dropout(0.3) → Dense(6, softmax)
- **Augmentation:** random flip, rotation, zoom
- **Training:** transfer learning, ~10 epochs on the merged dataset
- **Validation accuracy:** Validation accuracy: 91.6%

**Why MobileNetV2** over a larger backbone (e.g. EfficientNetB0): it trains faster on limited time/compute and is small enough to load quickly on a free hosting tier, with no meaningful accuracy tradeoff for a 6-class problem at this dataset size.

## 🗑️ Waste Categories & Disposal Guide

| Category | Bin | Icon |
|---|---|---|
| Wet Waste (Organic) | 🟩 Green Bin | 🍃 |
| Dry Waste — Paper/Cardboard | 🟦 Blue Bin | 📦 |
| Dry Waste — Plastic | 🟦 Blue Bin | 🧴 |
| Dry Waste — Glass | 🟦 Blue Bin | 🍾 |
| Dry Waste — Metal | 🟦 Blue Bin | 🥫 |
| Dry Waste — Other/Mixed | 🟦 Blue Bin | 🗑️ |

Each category includes a disposal method, recycling tip, safety precaution, and environmental impact — see [`disposal_guide.py`](disposal_guide.py).

## 📁 Project Structure

```
smart-kachra-sorter-ai/
├── app.py                # Gradio app — UI, inference, disposal guide rendering
├── disposal_guide.py      # Reference data: disposal info per waste category
├── train_model.py         # Colab training script (dataset merge + MobileNetV2 fine-tune)
├── requirements.txt        # Pinned, tested dependency versions
├── problem_statement.md    # Hackathon problem statement submission doc
├── waste_classifier.keras  # Trained model weights
├── labels.json             # Class name → index mapping
└── README.md
```

## 💻 Run Locally

```bash
git clone https://github.com/aniilhr/smart-kachra-sorter-ai.git
cd smart-kachra-sorter-ai
pip install -r requirements.txt
python app.py
```

The app opens at `http://127.0.0.1:7860` (a public share link is also generated automatically for local runs).

**To retrain the model:** open `train_model.py` in Google Colab, run the cells in order (requires a free Kaggle account + API token), then place the downloaded `waste_classifier.keras` and `labels.json` next to `app.py`.

## 🚀 Deployment

Deployed as a **Render Web Service**:

1. Connect the GitHub repo to a new Render Web Service
2. Build command: `pip install -r requirements.txt`
3. Start command: `python app.py`
4. `app.py` automatically binds to `0.0.0.0` and Render's assigned `PORT` in production, while still supporting a normal local launch during development

Live at: **https://smart-kachra-sorter-ai.onrender.com/**

## ⚠️ Known Limitations & Future Work

This project intentionally ships a **narrow, working scope** rather than faking broader coverage:

- ❌ **Not yet supported:** e-waste, hazardous waste, biomedical waste — no reliable training data was available in the build window, so these are flagged as future work rather than guessed at
- 🖼️ Trained on **single-item photos** — a busy multi-object scene (e.g. a pile of mixed trash) is out-of-distribution and may misclassify
- 📊 Session dashboard is **in-memory only** — stats reset on server restart
- 🗣️ Planned: LLM-powered Q&A assistant for edge-case disposal questions
- 🌐 Planned: multi-language UI (Hindi, Telugu, Tamil, Kannada)

## 🔧 Engineering Notes

A few real issues found and fixed during development (kept here deliberately, as evidence this wasn't AI-generated and unreviewed):

- **Double-preprocessing bug:** the saved model already normalizes pixels internally (baked into the graph during training), so an extra manual normalization step in the app was silently corrupting every prediction — found by comparing raw-vs-preprocessed model outputs, not by guessing
- **Render port binding:** `app.py` now detects Render's injected `PORT` env var and binds to `0.0.0.0` explicitly — without this, Render's port scanner never finds the running app
- **Dependency conflict:** an unpinned `huggingface_hub` resolved to a version incompatible with the pinned Gradio release, breaking the import at boot — fixed by pinning both to a tested, compatible pair

## 📄 License

MIT

---

<p align="center">Powered by TensorFlow · MobileNetV2 · Gradio · Python — Idea2Impact Hackathon 2026</p>
