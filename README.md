# ♻️ Smart Kachra Sorter AI

AI-powered waste segregation assistant for Indian municipal waste categories.
Built for Idea2Impact 2026 — Theme 2: Clean & Green Technology.

## Problem

India's municipal waste rules (Swachh Bharat) require households to segregate
waste into wet and dry streams, but most people don't know which bin an item
belongs in — especially for materials like glass, mixed plastics, or e-waste.
Wrongly-mixed waste is a leading cause of landfill methane emissions and makes
downstream recycling far less effective. Existing waste-classification tools
are mostly trained on Western trash categories and don't map cleanly onto how
Indian municipalities actually ask citizens to sort waste.

## Solution

Smart Kachra Sorter lets a user upload or capture a photo of an item and get,
in seconds:
- The correct Indian waste category (wet waste, or dry waste by material type)
- A confidence score and top-3 alternative predictions (basic interpretability)
- The specific disposal method, recycling tip, environmental impact, and
  safety precaution for that category

The AI model is the core of the product, not a wrapper around a chatbot —
classification runs through a transfer-learned computer vision model, and the
disposal guidance is deterministic reference data rather than an LLM guessing
at safety-relevant instructions.

## Architecture

```
User (browser)
   │  uploads/captures image
   ▼
Gradio UI (app.py)
   │  preprocess (resize, normalize)
   ▼
MobileNetV2 (frozen, ImageNet weights) + custom classification head
   │  softmax over 6 classes
   ▼
disposal_guide.py (lookup)
   │
   ▼
Result shown: category, confidence, top-3, disposal card, session stats
```

## Tech Stack

- **Model:** TensorFlow / Keras, MobileNetV2 (transfer learning)
- **App/UI:** Gradio
- **Deployment:** Hugging Face Spaces (Gradio SDK)
- **Training environment:** Google Colab (free GPU)

## Dataset

Two public datasets merged and remapped to Indian waste categories:
1. [Garbage Classification](https://www.kaggle.com/datasets/asdasdasasdas/garbage-classification)
   — cardboard, glass, metal, paper, plastic, trash
2. [Waste Classification Data](https://www.kaggle.com/datasets/techsash/waste-classification-data)
   — organic subset used for the wet-waste class

Final classes used: `wet_waste`, `dry_waste_paper`, `dry_waste_plastic`,
`dry_waste_glass`, `dry_waste_metal`, `dry_waste_other`.

See `train_model.py` for the exact merge and training pipeline.

## AI Model

- Base: MobileNetV2 pretrained on ImageNet, frozen (feature extractor)
- Head: GlobalAveragePooling → Dropout(0.3) → Dense(6, softmax)
- Data augmentation: random flip, rotation, zoom
- Trained for 10 epochs on the merged dataset (see `train_model.py`)
- Validation accuracy: **---**

MobileNetV2 was chosen over a larger backbone (e.g. EfficientNetB0) because it
trains faster on limited compute/time and is small enough to load quickly on
a free Hugging Face Space, without a meaningful accuracy tradeoff for a
6-class problem at this dataset size.

## Installation (local)

```bash
git clone https://github.com/aniilhr/smart-kachra-sorter-ai
cd smart-kachra-sorter
pip install -r requirements.txt
# place waste_classifier.keras and labels.json (from train_model.py) in this folder
python app.py
```

## Deployment

Deployed on Hugging Face Spaces (Gradio SDK):
1. Create a new Space at huggingface.co → New Space → SDK: Gradio
2. Push `app.py`, `disposal_guide.py`, `requirements.txt`,
   `waste_classifier.keras`, `labels.json` to the Space's git repo
3. Space auto-builds on push
4. Live link: **----**

## Screenshots

*(Add screenshots of the app here before submission)*

## Future Work

- Add e-waste, hazardous, and biomedical waste categories (need labeled data)
- Grad-CAM visual explanation of what the model "sees"
- LLM-powered Q&A assistant for edge-case disposal questions
- Multi-language UI (Hindi, Telugu, Tamil, Kannada)
- Persistent stats dashboard (currently session-only, in-memory)

## License

MIT
