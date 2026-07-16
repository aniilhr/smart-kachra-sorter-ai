"""
SMART KACHRA SORTER — Model Training Script
=============================================
Run this in GOOGLE COLAB (free GPU: Runtime > Change runtime type > T4 GPU)
Copy each "Cell" block into its own Colab cell, run top to bottom.
Total time: ~15-20 minutes including training.

WHAT THIS DOES
--------------
Downloads two public Kaggle datasets and merges them into 6 classes that map
to Indian municipal waste segregation categories:
    cardboard, paper        -> dry_waste_paper
    plastic                 -> dry_waste_plastic
    glass                   -> dry_waste_glass
    metal                   -> dry_waste_metal
    trash                   -> dry_waste_other
    organic (food waste)    -> wet_waste

Datasets:
  1. "Garbage Classification" (asdasdasasdas/garbage-classification)
     https://www.kaggle.com/datasets/asdasdasasdas/garbage-classification
  2. "Waste Classification Data" (techsash/waste-classification-data)
     https://www.kaggle.com/datasets/techsash/waste-classification-data
     -> we only use the "O" (organic) folder for wet_waste

You will need a free Kaggle account + API token:
  kaggle.com -> your profile -> Settings -> API -> "Create New Token"
  This downloads a file called kaggle.json. Upload it when Cell 1 asks.
"""

# ============ CELL 1: Setup ============
# !pip install -q kaggle tensorflow
#
# from google.colab import files
# print("Upload your kaggle.json file now")
# uploaded = files.upload()
#
# import os
# os.makedirs('/root/.kaggle', exist_ok=True)
# !cp kaggle.json /root/.kaggle/
# !chmod 600 /root/.kaggle/kaggle.json


# ============ CELL 2: Download datasets ============
# !kaggle datasets download -d asdasdasasdas/garbage-classification -p /content/data1 --unzip
# !kaggle datasets download -d techsash/waste-classification-data -p /content/data2 --unzip


# ============ CELL 3: Build the unified 6-class dataset folder ============
import os
import shutil
import glob
import json

os.makedirs('/content/dataset', exist_ok=True)

# Maps original folder names -> our Indian-context class names
CATEGORY_MAP = {
    'cardboard': 'dry_waste_paper',
    'paper': 'dry_waste_paper',
    'plastic': 'dry_waste_plastic',
    'glass': 'dry_waste_glass',
    'metal': 'dry_waste_metal',
    'trash': 'dry_waste_other',
}

# dataset 1 root can vary depending on zip structure - search for it
candidates = glob.glob('/content/data1/**/cardboard', recursive=True)
src_root = os.path.dirname(candidates[0]) if candidates else None
assert src_root, "Could not find dataset 1 folder structure — check the unzip output with !find /content/data1"

for folder, target in CATEGORY_MAP.items():
    src = os.path.join(src_root, folder)
    dst = os.path.join('/content/dataset', target)
    os.makedirs(dst, exist_ok=True)
    if os.path.exists(src):
        for f in os.listdir(src):
            shutil.copy(os.path.join(src, f), dst)
    else:
        print(f"WARNING: {src} not found, skipping")

# wet waste from dataset 2's organic ("O") folder — cap at 1500 images to keep
# training fast and classes roughly balanced
organic_dirs = glob.glob('/content/data2/**/O', recursive=True)
if organic_dirs:
    dst = '/content/dataset/wet_waste'
    os.makedirs(dst, exist_ok=True)
    src_files = os.listdir(organic_dirs[0])[:1500]
    for f in src_files:
        shutil.copy(os.path.join(organic_dirs[0], f), dst)
else:
    print("WARNING: organic folder not found for dataset 2 — check with !find /content/data2 -iname 'O'")

print("Final classes and image counts:")
for cls in sorted(os.listdir('/content/dataset')):
    n = len(os.listdir(os.path.join('/content/dataset', cls)))
    print(f"  {cls}: {n} images")


# ============ CELL 4: Train (MobileNetV2 transfer learning) ============
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models

IMG_SIZE = (224, 224)
BATCH = 32
EPOCHS = 10  # increase to 15-20 if you have extra time and want higher accuracy

train_ds = tf.keras.utils.image_dataset_from_directory(
    '/content/dataset', validation_split=0.2, subset='training', seed=42,
    image_size=IMG_SIZE, batch_size=BATCH)
val_ds = tf.keras.utils.image_dataset_from_directory(
    '/content/dataset', validation_split=0.2, subset='validation', seed=42,
    image_size=IMG_SIZE, batch_size=BATCH)

class_names = train_ds.class_names
print("Class order (important - app.py must match this):", class_names)

with open('/content/labels.json', 'w') as f:
    json.dump(class_names, f)

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(AUTOTUNE)
val_ds = val_ds.prefetch(AUTOTUNE)

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip('horizontal'),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

base_model = MobileNetV2(input_shape=IMG_SIZE + (3,), include_top=False, weights='imagenet')
base_model.trainable = False  # freeze pretrained weights - only train the new head

inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
x = data_augmentation(inputs)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(len(class_names), activation='softmax')(x)
model = models.Model(inputs, outputs)

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.summary()

history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

model.save('/content/waste_classifier.keras')
print("Training done. Final val accuracy:", history.history['val_accuracy'][-1])


# ============ CELL 5: Download the trained files to your laptop ============
# from google.colab import files
# files.download('/content/waste_classifier.keras')
# files.download('/content/labels.json')
#
# Put both files in the same folder as app.py before deploying.
