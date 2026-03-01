# VisionAssist

Real-time object detection web app running entirely in the browser using TensorFlow.js and YOLOv8n. Designed to assist visually impaired users by identifying nearby objects with privacy-first, client-side processing.

> **Powered by YOLOv8n** - State-of-the-art object detection with 37% mAP accuracy and excellent small object detection

## Features

- 🎯 **Real-time Object Detection** - Detects 80 common objects using YOLOv8n model
- 🚀 **High Accuracy** - YOLOv8n provides ~37% mAP on COCO dataset
- 🔍 **Better Small Object Detection** - Improved detection for phones, keys, utensils, and small items
- 🔒 **Privacy-First** - All processing happens locally in your browser
- ♿ **Accessible** - Audio announcements with smart debouncing (every 5 seconds or on object change)
- 📊 **Performance Metrics** - Live FPS and inference time tracking
- 🎨 **Modern UI** - Dark theme with Next.js, React, and Tailwind CSS
- 📱 **Responsive** - Optimized for desktop (M3 Pro: 40-60 FPS) and mobile (iPhone SE: 15-25 FPS)
- 🎙️ **Audio Feedback** - Text-to-speech announcements of detected objects

## Tech Stack

- **Framework**: Next.js 14+ with App Router
- **ML/AI**: TensorFlow.js, YOLOv8n (Ultralytics)
- **UI**: React, TypeScript, Tailwind CSS, shadcn/ui
- **Deployment**: Vercel

## 🚀 Quick Start

### Automated Setup (Recommended)

**⚠️ Run this ONCE for initial setup only:**

```bash
# 1. Export YOLOv8 model (ONE-TIME SETUP)
# Uses a virtual environment to avoid dependency conflicts
bash scripts/setup-clean.sh

# 2. Install npm dependencies
npm install

# 3. Start the app
npm run dev
```

**For subsequent runs, just use:**
```bash
npm run dev
```

> **Note:** The setup script only needs to run once to export the YOLOv8 model. After that, just use `npm run dev` to start the app.
> 
> **Troubleshooting:** If you have dependency conflicts, the `setup-clean.sh` script creates an isolated virtual environment to avoid conflicts with your existing Python packages.

### Alternative: Manual Setup with Virtual Environment

**If you have Python dependency conflicts, use a virtual environment:**

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv-yolo
source .venv-yolo/bin/activate  # On Windows: .venv-yolo\Scripts\activate

# 2. Install dependencies in isolated environment
pip install 'numpy<2' 'tensorflow>=2.0.0,<=2.19.0' ultralytics

# 3. Export YOLOv8n model
python scripts/export-yolov8.py

# 4. Deactivate virtual environment
deactivate

# 5. Copy model to public folder
cp -r yolov8n_web_model public/

# 6. Install and run
npm install
npm run dev
```

**Or install globally (may cause conflicts):**

```bash
pip install 'numpy<2' 'tensorflow>=2.0.0,<=2.19.0' ultralytics
python scripts/export-yolov8.py
cp -r yolov8n_web_model public/
npm install && npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Model Information

### YOLOv8n Specifications

| Property | Value |
|----------|-------|
| Model Size | ~13 MB |
| Parameters | 3.2M |
| Input Size | 640x640 |
| Classes | 80 (COCO dataset) |
| Accuracy (mAP) | ~37% |
| License | AGPL-3.0 (free for non-commercial) |

### Detected Object Classes (80 total)

**People & Animals:**
person, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe

**Vehicles:**
bicycle, car, motorcycle, airplane, bus, train, truck, boat

**Outdoor Objects:**
traffic light, fire hydrant, stop sign, parking meter, bench

**Sports:**
frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket

**Kitchen & Dining:**
bottle, wine glass, cup, fork, knife, spoon, bowl

**Food:**
banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake

**Furniture:**
chair, couch, potted plant, bed, dining table, toilet

**Electronics:**
tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster

**Accessories:**
backpack, umbrella, handbag, tie, suitcase

**Home Items:**
sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush


## Getting Started

### Prerequisites

- Node.js 18+ (recommended: Node 20+)
- Python 3.8+ (for model export)
- Webcam access

### Installation

```bash
# Install dependencies
npm install

# Export YOLOv8 model (see Model Setup above)
python scripts/export-yolov8.py
cp -r yolov8n_web_model public/

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Usage

1. Click "Activate Camera" to start your webcam
2. Grant camera permissions when prompted
3. Click "Start Detection" to begin object detection
4. Audio feedback is enabled by default - detected objects are announced
5. Adjust confidence threshold (10-90%) for better small object detection
6. Use "Stop All" to stop camera and detection completely

## Performance

### Expected Performance (YOLOv8n)

- **MacBook Pro M3**: 40-60 FPS, 20-30ms inference
- **MacBook Pro Intel**: 15-25 FPS, 50-80ms inference
- **iPhone SE 2020**: 15-25 FPS, 70-120ms inference

### Model Specifications

| Metric | Value |
|--------|-------|
| Accuracy (mAP) | ~37% |
| Speed | 40-60 FPS (desktop), 15-25 FPS (mobile) |
| Small Objects | ✅ Excellent |
| Model Size | 13 MB |

### Optimization

The app uses:
- WebGL backend for GPU acceleration
- YOLOv8n nano model optimized for browser inference
- Custom NMS (Non-Maximum Suppression) implementation
- Efficient frame processing with requestAnimationFrame
- Browser caching for model files
- TensorFlow.js memory management with tf.tidy()

## Accessibility Features

- **Audio Feedback**: Text-to-speech announcements of detected objects (announces on change or every 5 seconds)
- **Smart Announcements**: Says "Detected person and chair and cup" instead of listing separately
- **Keyboard Navigation**: Full keyboard support for all controls
- **Screen Reader Support**: ARIA labels and semantic HTML
- **High Contrast**: Dark theme with black background optimized for visibility

## Deployment

### Vercel Deployment (Recommended)

### Option 1: Deploy via Vercel CLI

1. **Install Vercel CLI** (if not already installed):
```bash
npm install -g vercel
```

2. **Build and deploy**:
```bash
npm run build
vercel
```

3. **Follow the prompts**:
   - Set up and deploy: Yes
   - Which scope: Select your account
   - Link to existing project: No
   - Project name: vision-assist (or your preferred name)
   - Directory: `./` (current directory)
   - Override settings: No

4. **Production deployment**:
```bash
vercel --prod
```

### Option 2: Deploy via Vercel Dashboard

1. **Push code to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository
   - Configure project:
     - Framework Preset: Next.js
     - Root Directory: `./`
     - Build Command: `npm run build`
     - Output Directory: `.next`
   - Click "Deploy"

3. **Automatic deployments**:
   - Every push to `main` branch triggers a production deployment
   - Pull requests create preview deployments

### Environment Configuration

No environment variables needed - the app runs entirely client-side!

### Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### Deployment Notes

**Important:** Include the model files in your deployment:
1. Ensure `public/yolov8n_web_model/` exists before deploying
2. Vercel has a 100 MB limit per file (YOLOv8n ~13 MB is well within limits)

The app is already optimized for Vercel:
- ✅ Static generation where possible
- ✅ Automatic code splitting
- ✅ CDN distribution for global performance
- ✅ WebGL backend for GPU acceleration
- ✅ Browser caching for model files

### Alternative: CDN Hosting for Model

For faster model loading, host the model on a CDN:

```typescript
// lib/yolov8-detection.ts
export async function loadYOLOv8Model(
  modelPath: string = 'https://your-cdn.com/yolov8n_web_model/model.json'
)
```

## Making Updates

### After making code changes:

1. **Push to GitHub**:
```bash
cd /Users/marialima/github/generative-ai/vision-assist
git add .
git commit -m "Your commit message"
git push
```

2. **Deploy to Vercel**:
```bash
vercel --prod
```

### Optional: Enable Automatic Deployments

Connect GitHub to Vercel for automatic deployments on every push:

1. Go to [vercel.com](https://vercel.com) → Your project → **Settings** → **Git**
2. Click **Connect Git Repository**
3. Select your `generative-ai` repository
4. Set root directory to `vision-assist`

Once connected, every push to `main` branch automatically deploys to production. You'll only need to push to GitHub - Vercel handles deployment automatically.

## Browser Compatibility

- ✅ **Chrome/Edge** (recommended) - Best WebGL and speech synthesis support
- ✅ **Safari** (macOS/iOS) - Good support, uses Metal API for GPU acceleration
- ✅ **Firefox** - Full support
- ⚠️ **Requirements**: WebGL support for GPU acceleration, Web Speech API for audio feedback

### Known Issues

- Speech synthesis may not work in some browsers - verify with the audio toggle in control panel
- Browser extensions may cause hydration warnings (harmless, can be ignored)

## Privacy

VisionAssist is completely privacy-focused:
- No data is sent to external servers
- All ML inference happens in your browser
- No analytics or tracking
- Camera access is only used for local processing

### No Audio
- Check system volume is not muted
- Try Chrome browser (best speech synthesis support)
- Check browser permissions for audio
- Verify audio toggle is enabled in the control panel

### Low FPS on Mobile
- Lower confidence threshold to 30-40%
- Ensure good lighting conditions
- Close other apps to free up resources

### Objects Not Detected
- Ensure good lighting
- Move closer to objects
- Lower confidence threshold for small objects (spoons, keys, phones)
- Make sure objects are fully visible and not partially hidden

## Performance Optimization

### Browser Settings

**Chrome (Recommended):**
1. Enable hardware acceleration: Settings → System → Use hardware acceleration
2. Check GPU status: chrome://gpu
3. Ensure WebGL is enabled

**Safari:**
- WebGL is enabled by default
- Uses Metal API for GPU acceleration

### App Settings

**For better FPS:**
- Increase confidence threshold (50-70%)
- Reduce max detections in `lib/yolov8-detection.ts`

**For better accuracy:**
- Lower confidence threshold (30-40%)
- Ensure good lighting
- Position objects clearly in frame

## License & Legal

### App License
**VisionAssist**: MIT License

### YOLOv8 License
**YOLOv8**: AGPL-3.0

- ✅ Free for personal use
- ✅ Free for non-commercial use
- ✅ Free for open-source projects
- ⚠️ Commercial use requires Ultralytics Enterprise License

**For commercial deployment, consider:**
1. Purchasing Ultralytics Enterprise License
2. Training your own model with a different framework

## Technical Architecture

```
Browser → YOLOv8n Model → Custom NMS → Detections
         (13 MB, 37% mAP)
```

### Key Technical Improvements

1. **Custom NMS Implementation**
   - Non-Maximum Suppression implemented in JavaScript
   - Optimized for browser performance
   - Configurable IoU threshold

2. **Better Memory Management**
   - Proper TensorFlow.js tensor disposal
   - `tf.tidy()` for automatic cleanup
   - Reduced memory leaks

3. **Preprocessing Pipeline**
   - Letter-box resizing (maintains aspect ratio)
   - Padding to square input
   - Normalized to [0, 1] range

4. **Model Flexibility**
   - Can upgrade to larger YOLOv8 variants (s, m, l, x)
   - Supports custom trained models

## Files Structure

### Core Detection Files
- `lib/yolov8-detection.ts` - YOLOv8 TensorFlow.js integration
- `lib/yolo-classes.ts` - 80 COCO class labels
- `lib/detection.ts` - YOLOv8 model loader
- `hooks/useObjectDetection.ts` - React hook for object detection

### Setup Scripts
- `scripts/export-yolov8.py` - Model export script
- `scripts/setup.sh` - Automated setup script
- `scripts/requirements.txt` - Python dependencies

### UI Components
- `app/page.tsx` - Main application page
- `components/WebcamView.tsx` - Webcam component
- `components/DetectionCanvas.tsx` - Detection overlay
- `components/ControlPanel.tsx` - Control interface
- `components/PerformanceStats.tsx` - FPS and metrics display

## Additional Resources

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [TensorFlow.js Models](https://www.tensorflow.org/js/models)
- [COCO Dataset Classes](https://cocodataset.org/#explore)
- [Ultralytics GitHub](https://github.com/ultralytics/ultralytics)
- [TensorFlow.js GitHub](https://github.com/tensorflow/tfjs)

## Author

Maria Lima

## Why YOLOv8n?

### 1. High Accuracy 📈
- **37% mAP** (mean Average Precision) on COCO dataset
- State-of-the-art object detection performance
- Reliable detection across various lighting conditions

### 2. Excellent Small Object Detection 🔍
YOLOv8n excels at detecting small everyday objects:
- Cell phones, keys, utensils (spoons, forks, knives)
- Remote controls, scissors, pens
- Small household items

**Critical for assistive technology** - visually impaired users can reliably locate small everyday objects.

### 3. Optimized Model Size 💾
- **13 MB** - Compact and efficient
- Fast initial load time
- Minimal bandwidth usage

### 4. Modern Architecture 🚀
- State-of-the-art object detection (2024)
- Active development by Ultralytics
- Regular updates and improvements
- Browser-optimized for real-time performance

## Advanced Setup

### Model Export Details

**What happens during export:**
1. Downloads YOLOv8n.pt (~6 MB) if not already cached
2. Converts model to TensorFlow.js format
3. Creates `yolov8n_web_model/` directory with:
   - `model.json` - Model architecture
   - `group1-shard*.bin` - Model weights (multiple files)

**Expected output:**
```
Ultralytics YOLOv8.x.x 🚀 Python-3.x.x
YOLOv8n summary: 225 layers, 3,157,200 parameters
...
Export success ✅ 2.3s
Results saved to yolov8n_web_model/
```

**Verify the structure:**
```
public/
└── yolov8n_web_model/
    ├── model.json
    └── group1-shard*.bin (multiple files)
```

### Use Different YOLOv8 Variant

**Available variants:**
- `yolov8n.pt` - Nano (fastest, 13 MB) ⭐ Current
- `yolov8s.pt` - Small (better accuracy, 22 MB)
- `yolov8m.pt` - Medium (best accuracy, 50 MB)

**To use a different variant:**
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt').export(format='tfjs')"
cp -r yolov8s_web_model public/
```

Then update `lib/yolov8-detection.ts`:
```typescript
export async function loadYOLOv8Model(modelPath: string = '/yolov8s_web_model/model.json')
```

## Troubleshooting

### Model Not Loading

**Issue:** "Failed to load YOLOv8 model"

**Solution:**
1. Check that `public/yolov8n_web_model/model.json` exists
2. Verify all shard files are present
3. Clear browser cache (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
4. Check browser console for specific errors

### Python/Model Export Issues

**Issue:** "ModuleNotFoundError: No module named 'tensorflow'"

**Solution:**
```bash
pip install 'numpy<2' 'tensorflow>=2.0.0,<=2.19.0' ultralytics
```

**Issue:** NumPy version conflict / "A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x"

**Solution:** Downgrade NumPy to version 1.x:
```bash
pip install 'numpy<2' --force-reinstall
```

**Issue:** "ModuleNotFoundError: No module named 'ultralytics'"

**Solution:**
```bash
pip install --upgrade pip
pip install 'numpy<2' 'tensorflow>=2.0.0,<=2.19.0' ultralytics
```

**Issue:** Model export is slow

**Explanation:**
- First run downloads YOLOv8n.pt (~6 MB)
- Model conversion takes 1-3 minutes
- Subsequent exports are faster (model is cached)

**Issue:** CUDA/GPU errors during export

**Solution:** Export with CPU only:
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt').export(format='tfjs', device='cpu')"
```

### Low FPS in Browser

**Solutions:**
1. Lower confidence threshold to 30-40%
2. Ensure WebGL is enabled in browser
3. Close other tabs/applications
4. Try Chrome (best WebGL support)
5. Check GPU acceleration: chrome://gpu

## Acknowledgments

- Ultralytics team for YOLOv8
- TensorFlow.js team for browser-based ML
- shadcn/ui for accessible components
- Next.js and Vercel for deployment platform
