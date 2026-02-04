SmartWebP: WebP Image Optimizer (AI-Assisted)

A production-ready web application that converts JPG and PNG images to WebP, with an optional AI-assisted quality selection feature. This project is designed for a web portfolio and emphasizes engineering judgment, accessibility, performance, and responsible ML usage.

Overview

Converting images to WebP does not require machine learning.
ML is used only to automatically choose a good quality setting when a fixed value would not work well for all images.

Features
Core (Non-ML)

  JPG / PNG → WebP conversion

  Single or multiple file uploads

  Manual quality slider

  Lossy and lossless WebP

  Before / after file size comparison

  Fast server-side processing

Optional AI-Assisted Feature

  Smart Optimize (AI-assisted)

  Predicts an optimal WebP quality value per image

  Fully optional and transparent to the user

Tech Stack
Frontend (Vercel)

React + Next.js

JavaScript

Static pre-rendered HTML (SSG)

SEO-friendly metadata

Accessible, keyboard-navigable UI

Responsive design

Backend (Railway)

Python + FastAPI

Pillow for image processing

Lightweight ML inference

Stateless API

Accessibility & SEO

Pre-rendered pages using Next.js Static Site Generation

Semantic HTML

Accessible file inputs and buttons

Screen-reader friendly upload feedback

Keyboard navigation support

Proper meta tags (Open Graph, description, title)

Accessibility is treated as a first-class feature, not an afterthought.

Machine Learning Design
Why ML Is Used (and Why It’s Limited)

Image format conversion itself is deterministic and does not benefit from ML.
However, selecting a single compression quality that works well for photos, logos, screenshots, and UI images is inherently ambiguous.

ML is used only for this decision-making step.

Feature Set (Intentionally Minimal)

The model uses three interpretable features:

PNG vs JPG flag
Helps distinguish images that typically require higher fidelity (logos, UI, text) from photographic content.

Entropy
Measures visual complexity and detail density.

Edge density
Captures sharp transitions such as text and line art that degrade quickly under compression.

These features were chosen to keep inference fast, reduce overfitting, and ensure explainability.

Model Choice

Model: Gradient-boosted regression (e.g. XGBoost or LightGBM)

Input: Image feature vector

Output: Recommended WebP quality value (0–100)

Runtime: CPU-only

Inference cost: negligible


Training the Model
1️⃣ Collect Training Images

Create a small dataset (100–300 images is enough):

data/
├── images/
│   ├── photo_01.jpg
│   ├── logo_02.png
│   ├── screenshot_03.png
│   └── ...


Include a mix of:

Photos

Logos

UI screenshots

Text-heavy images

2️⃣ Label Optimal Quality

For each image:

Convert it to WebP at different quality levels (e.g. 50–95)

Choose the lowest quality that preserves acceptable visual quality

Record that value

Example labels file:

filename,quality
photo_01.jpg,70
logo_02.png,92
screenshot_03.png,88

Image types to include
Photos — landscapes, portraits, detailed scenes
Logos / UI — PNGs with text, icons, flat color areas
Screenshots — websites, apps, forms
Text-heavy images — PDFs saved as PNG/JPG

Your own images — best if you have personal photos, screenshots, logos

Open datasets / free images:
Unsplash — high-res photos
Pexels — free stock images
Open Logos Dataset — logos
Screenshots or UI mocks — small screenshots for testing
Generate simple test images yourself — colored boxes, text overlays, gradients (helpful for edge detection)

This reflects human perceptual judgment, which is exactly what the model learns to approximate.

3️⃣ Extract Features

For each image, compute:

PNG vs JPG flag

Entropy

Edge density

These are extracted using Pillow and basic image analysis.

4️⃣ Train the Model

Use a small regression model:

XGBoost Regressor (recommended)

Train on the feature set

Validate using a simple train/validation split

Export the trained model

Example output:

backend/app/ml/model.pkl

5️⃣ Load the Model at Runtime

The backend loads the model once at startup and uses it only when Smart Optimize is enabled.

If disabled, the app uses the manual quality value.

Project Structure
Frontend
frontend/
├── src/
│   ├── pages/
│   │   └── index.js
│   ├── components/
│   │   ├── UploadZone.js
│   │   ├── QualitySlider.js
│   │   └── SmartOptimizeToggle.js
│   └── styles/
└── public/

Backend
backend/
├── app/
│   ├── main.py                   # FastAPI entry point
│   ├── api/
│   │   └── routes.py             # Upload & convert endpoints
│   ├── services/
│   │   ├── image_processing.py   # Pillow conversion logic
│   │   ├── feature_extraction.py # Entropy, edge detection
│   │   └── quality_selector.py   # ML inference
│   ├── ml/
│   │   └── model.pkl             # Trained model (generated after training)
│   └── utils/
│       └── validators.py
├── train_quality_model.py        # Training script
├── requirements.txt
└── README.md


Deployment

Frontend: Vercel

Backend: Railway


License

MIT
