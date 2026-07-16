"""
SMART KACHRA SORTER — AI Waste Classifier
==========================================
Gradio app. Deploy target: Hugging Face Spaces (SDK: Gradio).

Files needed alongside this one:
  - waste_classifier.keras   (from train_model.py, downloaded from Colab)
  - labels.json              (from train_model.py, downloaded from Colab)
  - disposal_guide.py        (included in this repo)
  - requirements.txt         (included in this repo)
"""

import json
import numpy as np
import gradio as gr
import tensorflow as tf
from PIL import Image

from disposal_guide import DISPOSAL_GUIDE, NOT_YET_SUPPORTED

IMG_SIZE = (224, 224)

# ---- Load model + labels once at startup ----
model = tf.keras.models.load_model("waste_classifier.keras")
with open("labels.json") as f:
    CLASS_NAMES = json.load(f)

# in-memory running stats for this session (resets on restart — fine for a demo)
STATS = {name: 0 for name in CLASS_NAMES}
TOTAL_SCANS = {"count": 0}


def preprocess(image: Image.Image) -> np.ndarray:
    image = image.convert("RGB").resize(IMG_SIZE)
    arr = np.array(image, dtype=np.float32)
    arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)
    return np.expand_dims(arr, axis=0)


def classify(image: Image.Image):
    if image is None:
        return "Please upload or capture an image.", "", "", {}

    batch = preprocess(image)
    preds = model.predict(batch, verbose=0)[0]

    top_idx = int(np.argmax(preds))
    top_class = CLASS_NAMES[top_idx]
    confidence = float(preds[top_idx])

    # update running dashboard stats
    STATS[top_class] += 1
    TOTAL_SCANS["count"] += 1

    guide = DISPOSAL_GUIDE.get(top_class, {})
    display_name = guide.get("display_name", top_class)

    result_md = f"## 🗑️ {display_name}\n**Confidence: {confidence*100:.1f}%**"

    disposal_md = (
        f"**Disposal method:** {guide.get('disposal_method', 'N/A')}\n\n"
        f"**Recycling tip:** {guide.get('recycling_tip', 'N/A')}\n\n"
        f"**Environmental impact:** {guide.get('environmental_impact', 'N/A')}\n\n"
        f"**Safety precaution:** {guide.get('safety_precaution', 'N/A')}"
    )

    # top-3 predictions for basic interpretability
    top3_idx = np.argsort(preds)[::-1][:3]
    top3 = {CLASS_NAMES[i]: float(preds[i]) for i in top3_idx}

    stats_md = f"**Total scans this session:** {TOTAL_SCANS['count']}\n\n" + "\n".join(
        f"- {DISPOSAL_GUIDE.get(k, {}).get('display_name', k)}: {v}"
        for k, v in STATS.items() if v > 0
    )

    return result_md, disposal_md, stats_md, top3


with gr.Blocks(title="Smart Kachra Sorter AI") as demo:
    gr.Markdown("# ♻️ Smart Kachra Sorter AI")
    gr.Markdown(
        "AI-powered waste classification for Indian municipal waste categories. "
        "Upload a photo or use your camera to identify the correct disposal bin."
    )

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Upload or capture waste image", sources=["upload", "webcam"])
            classify_btn = gr.Button("Classify", variant="primary")
        with gr.Column():
            result_output = gr.Markdown(label="Prediction")
            top3_output = gr.Label(label="Top 3 predictions", num_top_classes=3)

    disposal_output = gr.Markdown(label="Disposal Guide")

    with gr.Accordion("📊 Session Dashboard", open=False):
        stats_output = gr.Markdown()

    with gr.Accordion("⚠️ Categories not yet supported by this model", open=False):
        gr.Markdown("\n".join(f"- {item}" for item in NOT_YET_SUPPORTED) +
                    "\n\n*(Planned future work — see README)*")

    classify_btn.click(
        fn=classify,
        inputs=image_input,
        outputs=[result_output, disposal_output, stats_output, top3_output],
    )

if __name__ == "__main__":
    demo.launch(
        inbrowser=True,
        share=True
    )