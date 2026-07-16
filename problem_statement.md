# Problem Statement — Smart Kachra Sorter AI

> ⚠️ This is a starting draft. Personalize it — add any local detail you know
> (your city/area's segregation rules, a story about a mis-sorted bin, etc.)
> and make sure you can talk through every sentence live, since judges may ask.

## Theme
Clean & Green Technology

## The Problem

Indian municipalities require households to segregate waste into wet and dry
streams at source — this is central to Swachh Bharat Mission guidelines. In
practice, most residents don't reliably know which bin an item belongs in,
especially for ambiguous materials (broken glass, mixed plastics, soiled
paper). This isn't a knowledge problem that a poster or pamphlet fixes well —
people need an answer in the moment, standing over their bin.

**Who it affects:** Households, RWAs (Resident Welfare Associations), and
municipal waste workers who have to manually re-sort improperly segregated
waste — a slow, unhygienic, and avoidable task.

**Why existing solutions fall short:** Most publicly available waste
classifiers are trained on Western recycling categories (single-stream
"recyclable vs. trash") that don't match how Indian civic bodies actually
ask citizens to segregate waste (wet/dry + material type). They also tend to
be a single generic model with no disposal guidance attached — a
classification label alone doesn't tell someone what to actually do with the
item.

## Our Approach

Smart Kachra Sorter AI is a computer-vision classifier, fine-tuned via
transfer learning on waste imagery and explicitly remapped to Indian
municipal categories (wet waste + 5 dry-waste material types). A photo goes
in; a category, confidence score, and concrete disposal instruction (method,
recycling tip, environmental impact, safety note) come out — instantly, and
without needing to know the classification rules yourself.

The model is the product's core, not a decorative add-on: predictions come
directly from a trained MobileNetV2-based classifier, and we surface the
top-3 predictions and confidence score so the tool is honest about its own
uncertainty rather than presenting a single answer as gospel.

## Scope & Honesty About Limitations

The current model covers 6 categories (wet waste + paper/plastic/glass/metal/
other dry waste), built from two publicly available datasets in the time
available. E-waste, hazardous, and biomedical waste are **not** yet
supported — we chose not to fake coverage of categories we don't have
reliable training data for, and instead documented this as future work. We'd
rather ship something narrow that works than something broad that guesses
wrong on safety-relevant categories.
