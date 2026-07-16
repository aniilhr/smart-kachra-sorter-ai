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
import math
import os
import numpy as np
import gradio as gr
import tensorflow as tf
from PIL import Image

from disposal_guide import DISPOSAL_GUIDE, NOT_YET_SUPPORTED

IMG_SIZE = (224, 224)

# TODO: replace with your REAL validation accuracy from Colab (printed at the
# end of Cell 4 in train_model.py as "Final val accuracy: ..."). Do not leave
# this as a guess — you may be asked to justify it live.
VALIDATION_ACCURACY_DISPLAY = "—"  # e.g. "91.2"

# ---- Load model + labels once at startup ----
model = tf.keras.models.load_model("waste_classifier.keras")
with open("labels.json") as f:
    CLASS_NAMES = json.load(f)

# in-memory running stats for this session (resets on restart — fine for a demo)
STATS = {name: 0 for name in CLASS_NAMES}
TOTAL_SCANS = {"count": 0}

# ---- A few small original inline-SVG icons (no external icon library —
# keeps the deployment dependency-free) ----
ICON_UPLOAD = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 15V3"/><path d="M7 8l5-5 5 5"/><path d="M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/></svg>'
ICON_LEAF = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 4 13C4 9 8 4 12 2c4 2 8 7 8 11a7 7 0 0 1-7 7"/><path d="M12 2v18"/></svg>'
ICON_CHART = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="12" width="4" height="8" rx="1"/><rect x="10" y="7" width="4" height="13" rx="1"/><rect x="17" y="3" width="4" height="17" rx="1"/></svg>'


def preprocess(image: Image.Image) -> np.ndarray:
    # IMPORTANT: do NOT call mobilenet_v2.preprocess_input() here.
    # train_model.py applies preprocess_input INSIDE the model graph (on the
    # symbolic input tensor, before base_model), so it gets saved as part of
    # waste_classifier.keras itself. The model expects raw 0-255 pixel values
    # and normalizes them internally. Normalizing here too double-applies it
    # and corrupts the input (confirmed: collapses confident predictions to
    # near-uniform ~33% across classes).
    image = image.convert("RGB").resize(IMG_SIZE)
    arr = np.array(image, dtype=np.float32)
    return np.expand_dims(arr, axis=0)


def render_bar(label: str, pct: float, color: str) -> str:
    return f"""
    <div style="margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;font-size:13px;color:var(--text-secondary);margin-bottom:4px;">
            <span>{label}</span><span>{pct:.0f}%</span>
        </div>
        <div style="height:8px;border-radius:4px;background:#1F2937;overflow:hidden;">
            <div style="height:100%;width:{pct:.1f}%;background:{color};border-radius:4px;
                        transition:width 0.6s ease;"></div>
        </div>
    </div>
    """


def render_donut(size: int = 150, stroke: int = 20) -> str:
    total = TOTAL_SCANS["count"]
    r = (size - stroke) / 2
    cx = cy = size / 2
    circumference = 2 * math.pi * r
    segments = []
    cumulative = 0.0
    if total == 0:
        segments.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1F2937" stroke-width="{stroke}"/>'
        )
    else:
        for k, v in STATS.items():
            if v <= 0:
                continue
            frac = v / total
            arc = frac * circumference
            color = DISPOSAL_GUIDE.get(k, {}).get("color", "#6B7280")
            segments.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
                f'stroke-width="{stroke}" stroke-dasharray="{arc:.2f} {circumference-arc:.2f}" '
                f'stroke-dashoffset="{-cumulative:.2f}"/>'
            )
            cumulative += arc
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
        <g transform="rotate(-90 {cx} {cy})">{''.join(segments)}</g>
        <text x="{cx}" y="{cy-2}" text-anchor="middle" font-size="24" font-weight="600"
              fill="var(--text-primary)" font-family="Poppins, sans-serif">{total}</text>
        <text x="{cx}" y="{cy+18}" text-anchor="middle" font-size="11"
              fill="var(--text-secondary)">scans</text>
    </svg>
    """


def render_dashboard() -> str:
    donut = render_donut()
    cards = "".join(
        f"""
        <div class="skc-mini-card">
            <div style="font-size:20px;">{DISPOSAL_GUIDE.get(k, {}).get('icon','🗑️')}</div>
            <div style="font-size:20px;font-weight:600;color:var(--text-primary);margin-top:4px;">{v}</div>
            <div style="font-size:12px;color:var(--text-secondary);">{DISPOSAL_GUIDE.get(k, {}).get('display_name', k)}</div>
        </div>
        """
        for k, v in STATS.items() if v > 0
    )
    if not cards:
        cards = '<div style="color:var(--text-secondary);font-size:13px;">No scans yet this session.</div>'

    return f"""
    <div class="skc-card" style="display:flex;gap:28px;align-items:center;flex-wrap:wrap;">
        <div style="flex:0 0 auto;">{donut}</div>
        <div style="flex:1 1 240px;display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:12px;">
            {cards}
        </div>
    </div>
    """


def render_result(display_name: str, icon: str, color: str, confidence: float,
                   bin_label: str, top3: dict) -> str:
    pct = confidence * 100
    bars = "".join(
        render_bar(DISPOSAL_GUIDE.get(k, {}).get("display_name", k).replace("Dry Waste — ", ""),
                   v * 100, DISPOSAL_GUIDE.get(k, {}).get("color", "#6B7280"))
        for k, v in top3.items()
    )
    return f"""
    <div class="skc-card">
        <div style="font-size:13px;color:var(--text-secondary);margin-bottom:4px;">Detected category</div>
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <div style="font-size:32px;">{icon}</div>
            <div style="font-size:24px;font-weight:600;color:{color};font-family:'Poppins',sans-serif;">{display_name}</div>
        </div>
        <div style="display:flex;gap:24px;flex-wrap:wrap;margin-bottom:18px;">
            <div>
                <div style="font-size:12px;color:var(--text-secondary);">Confidence</div>
                <div style="font-size:20px;font-weight:600;color:var(--text-primary);">{pct:.1f}%</div>
            </div>
            <div>
                <div style="font-size:12px;color:var(--text-secondary);">Correct bin</div>
                <div style="font-size:20px;font-weight:600;color:var(--text-primary);">{bin_label}</div>
            </div>
        </div>
        <div style="height:1px;background:#1F2937;margin-bottom:14px;"></div>
        <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px;">Top predictions</div>
        {bars}
    </div>
    """


def render_disposal(guide: dict) -> str:
    def row(icon, label, value):
        return f"""
        <div style="display:flex;gap:12px;padding:10px 0;">
            <div style="font-size:18px;">{icon}</div>
            <div>
                <div style="font-size:13px;font-weight:600;color:var(--text-primary);">{label}</div>
                <div style="font-size:13px;color:var(--text-secondary);">{value}</div>
            </div>
        </div>
        <div style="height:1px;background:#1F2937;"></div>
        """
    return f"""
    <div class="skc-card">
        <div style="font-size:16px;font-weight:600;color:var(--text-primary);margin-bottom:8px;
                    font-family:'Poppins',sans-serif;">Disposal guide</div>
        {row("♻️", "Disposal method", guide.get('disposal_method', 'N/A'))}
        {row("💡", "Recycling tip", guide.get('recycling_tip', 'N/A'))}
        {row("⚠️", "Safety", guide.get('safety_precaution', 'N/A'))}
    </div>
    """


def render_impact(guide: dict, color: str) -> str:
    points = guide.get("impact_points", [])
    items = "".join(
        f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;">'
        f'<span style="color:{color};font-weight:700;">✓</span>'
        f'<span style="font-size:13px;color:var(--text-primary);">{p}</span></div>'
        for p in points
    )
    return f"""
    <div class="skc-card">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
            <div style="color:{color};">{ICON_LEAF}</div>
            <div style="font-size:16px;font-weight:600;color:var(--text-primary);
                        font-family:'Poppins',sans-serif;">Environmental impact</div>
        </div>
        <div style="font-size:13px;color:var(--text-secondary);margin-bottom:8px;">
            {guide.get('environmental_impact', '')}
        </div>
        {items}
    </div>
    """


EMPTY_RESULT_HTML = """
<div class="skc-card" style="text-align:center;color:var(--text-secondary);padding:48px 24px;">
    Upload or capture a photo, then press Classify.
</div>
"""
EMPTY_DISPOSAL_HTML = (
    '<div class="skc-card" style="min-height:60px;color:var(--text-secondary);'
    'font-size:13px;">Disposal guidance will appear here.</div>'
)
EMPTY_IMPACT_HTML = (
    '<div class="skc-card" style="min-height:60px;color:var(--text-secondary);'
    'font-size:13px;">Environmental impact will appear here.</div>'
)


def classify(image: Image.Image):
    if image is None:
        return EMPTY_RESULT_HTML, EMPTY_DISPOSAL_HTML, EMPTY_IMPACT_HTML, render_dashboard()

    batch = preprocess(image)
    preds = model.predict(batch, verbose=0)[0]

    top_idx = int(np.argmax(preds))
    top_class = CLASS_NAMES[top_idx]
    confidence = float(preds[top_idx])

    STATS[top_class] += 1
    TOTAL_SCANS["count"] += 1

    guide = DISPOSAL_GUIDE.get(top_class, {})
    display_name = guide.get("display_name", top_class)
    icon = guide.get("icon", "🗑️")
    color = guide.get("color", "#6B7280")
    bin_label = guide.get("bin_label", "—")

    top3_idx = np.argsort(preds)[::-1][:3]
    top3 = {CLASS_NAMES[i]: float(preds[i]) for i in top3_idx}

    result_html = render_result(display_name, icon, color, confidence, bin_label, top3)
    disposal_html = render_disposal(guide)
    impact_html = render_impact(guide, color)
    dashboard_html = render_dashboard()

    return result_html, disposal_html, impact_html, dashboard_html


CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600&family=Inter:wght@400;500&display=swap');

:root {
    --bg: #0B1220;
    --card: #111827;
    --primary: #10B981;
    --primary-hover: #059669;
    --secondary: #2563EB;
    --warning: #F59E0B;
    --error: #EF4444;
    --text-primary: #F9FAFB;
    --text-secondary: #9CA3AF;
}

.gradio-container {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
}
/* No blanket color rule here on purpose. Every custom card/text element
   below sets its own color explicitly inline. Native Gradio components
   (accordion, image toolbar) are left to their own default styling so
   their text/icons stay correctly contrasted against their own light
   background — forcing white text onto them was making them render
   white-on-white and disappear. */
.skc-accordion, .skc-accordion * {
    background: var(--card) !important;
    color: var(--text-secondary) !important;
    border-color: #1F2937 !important;
}

.skc-card {
    background: var(--card);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 12px 40px rgba(0,0,0,.18);
    animation: skcFadeIn 0.4s ease;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.skc-card:hover { box-shadow: 0 16px 48px rgba(0,0,0,.22); }

.skc-mini-card {
    background: #0F172A;
    border-radius: 12px;
    padding: 12px;
    text-align: center;
}

@keyframes skcFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

#skc-hero {
    background: linear-gradient(135deg, #0F2A22 0%, #0B1220 60%);
    border: 1px solid #1F2937;
    border-radius: 20px;
    padding: 40px 32px;
    text-align: center;
    margin-bottom: 20px;
}
#skc-hero h1 {
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    font-size: 30px;
    color: var(--text-primary);
    margin: 0 0 10px 0;
}
#skc-hero p {
    color: var(--text-secondary);
    font-size: 15px;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.6;
}
#skc-hero .skc-chips {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 20px;
    flex-wrap: wrap;
}
#skc-hero .skc-chip {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 10px 18px;
    min-width: 110px;
}
#skc-hero .skc-chip .val { font-size: 18px; font-weight: 600; color: var(--primary); font-family:'Poppins',sans-serif; }
#skc-hero .skc-chip .lbl { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }

#upload-box img { border-radius: 16px !important; }

button.primary, .gradio-container button.primary {
    height: 52px !important;
    border-radius: 14px !important;
    background: var(--primary) !important;
    border: none !important;
    font-weight: 500 !important;
    transition: background 0.2s ease !important;
}
button.primary:hover { background: var(--primary-hover) !important; }

.skc-section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-secondary);
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
    font-size: 14px;
    margin: 24px 0 10px 0;
}

#skc-footer {
    text-align: center;
    color: var(--text-secondary);
    font-size: 12px;
    padding: 24px 0 8px 0;
}
"""

with gr.Blocks(title="Smart Kachra Sorter AI") as demo:
    gr.HTML(f"""
    <div id="skc-hero">
        <h1>♻️ Smart Kachra Sorter AI</h1>
        <p>AI-powered waste segregation assistant for smarter, cleaner Indian cities.
           Upload an image to instantly identify waste, get disposal guidance,
           and contribute to a sustainable future.</p>
        <div class="skc-chips">
            <div class="skc-chip"><div class="val">{VALIDATION_ACCURACY_DISPLAY}%</div><div class="lbl">Accuracy</div></div>
            <div class="skc-chip"><div class="val">AI</div><div class="lbl">Powered</div></div>
            <div class="skc-chip"><div class="val">{len(CLASS_NAMES)}</div><div class="lbl">Waste categories</div></div>
        </div>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML(f'<div class="skc-section-title">{ICON_UPLOAD} Upload image</div>')
            image_input = gr.Image(
                type="pil", label=None, sources=["upload", "webcam"],
                height=420, width=480, elem_id="upload-box",
            )
            classify_btn = gr.Button("Classify", variant="primary", size="lg")

        with gr.Column(scale=1):
            result_output = gr.HTML(value=EMPTY_RESULT_HTML)

    with gr.Row():
        with gr.Column(scale=1):
            disposal_output = gr.HTML(value=EMPTY_DISPOSAL_HTML)
        with gr.Column(scale=1):
            impact_output = gr.HTML(value=EMPTY_IMPACT_HTML)

    gr.HTML(f'<div class="skc-section-title">{ICON_CHART} Session dashboard</div>')
    dashboard_output = gr.HTML(value=render_dashboard())

    with gr.Accordion("⚠️ Categories not yet supported by this model", open=False,
                      elem_classes=["skc-accordion"]):
        gr.Markdown("\n".join(f"- {item}" for item in NOT_YET_SUPPORTED) +
                    "\n\n*(Planned future work — see README)*")

    gr.HTML("""
    <div id="skc-footer">
        Powered by TensorFlow · MobileNetV2 · Gradio · Python — Idea2Impact Hackathon 2026
    </div>
    """)

    classify_btn.click(
        fn=classify,
        inputs=image_input,
        outputs=[result_output, disposal_output, impact_output, dashboard_output],
    )

if __name__ == "__main__":
    if os.environ.get("SPACE_ID"):
        # Hugging Face Spaces — it hosts and ports the app itself.
        demo.launch(css=CUSTOM_CSS)
    elif os.environ.get("PORT"):
        # Render (and most other generic cloud hosts) inject a PORT env var
        # and scan for a service listening on it. Gradio defaults to binding
        # only to 127.0.0.1:7860, which Render's external scanner can't see —
        # that mismatch is exactly what "No open ports detected" means.
        demo.launch(server_name="0.0.0.0", server_port=int(os.environ["PORT"]), css=CUSTOM_CSS)
    else:
        # Local development — open in browser and get a shareable public link
        demo.launch(inbrowser=True, share=True, css=CUSTOM_CSS)