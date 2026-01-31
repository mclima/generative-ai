# VisionAssist

Real-time object detection web app running entirely in the browser using TensorFlow.js. Designed to assist visually impaired users by identifying nearby objects with privacy-first, client-side processing.

## Features

- 🎯 **Real-time Object Detection** - Detects 90 common objects using COCO-SSD model
- 🔒 **Privacy-First** - All processing happens locally in your browser
- ♿ **Accessible** - Audio announcements with smart debouncing (every 5 seconds or on object change)
- 📊 **Performance Metrics** - Live FPS and inference time tracking
- 🎨 **Modern UI** - Dark theme with Next.js, React, and Tailwind CSS
- 📱 **Responsive** - Optimized for desktop (M3 Pro: 50-60 FPS) and mobile (iPhone SE: 15-20 FPS)
- 🎙️ **Audio Feedback** - Text-to-speech announcements of detected objects

## Tech Stack

- **Framework**: Next.js 14+ with App Router
- **ML/AI**: TensorFlow.js, COCO-SSD
- **UI**: React, TypeScript, Tailwind CSS, shadcn/ui
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18+ (recommended: Node 20+)
- Webcam access

### Installation

```bash
# Install dependencies
npm install

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

### Expected Performance

- **MacBook Pro M3**: 50-60 FPS, 15-25ms inference
- **MacBook Pro Intel**: 20-30 FPS, 40-60ms inference
- **iPhone SE 2020**: 15-20 FPS, 60-100ms inference

### Optimization

The app uses:
- WebGL backend for GPU acceleration
- Lite MobileNet v2 model for faster inference
- Efficient frame processing with requestAnimationFrame
- Browser caching for model files

## Accessibility Features

- **Audio Feedback**: Text-to-speech announcements of detected objects (announces on change or every 5 seconds)
- **Smart Announcements**: Says "Detected person and chair and cup" instead of listing separately
- **Keyboard Navigation**: Full keyboard support for all controls
- **Screen Reader Support**: ARIA labels and semantic HTML
- **High Contrast**: Dark theme with black background optimized for visibility

## Deployment to Vercel

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

### Performance Optimization

The app is already optimized for Vercel:
- ✅ Static generation where possible
- ✅ Automatic code splitting
- ✅ CDN distribution for global performance
- ✅ WebGL backend for GPU acceleration
- ✅ Browser caching for model files

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

## Troubleshooting

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

## License

MIT

## Author

Maria Lima

## Acknowledgments

- TensorFlow.js team for browser-based ML
- COCO-SSD model for object detection
- shadcn/ui for accessible components
- Next.js and Vercel for deployment platform
