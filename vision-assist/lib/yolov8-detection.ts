import * as tf from '@tensorflow/tfjs';
import '@tensorflow/tfjs-backend-webgl';
import { YOLO_CLASSES } from './yolo-classes';

interface YOLOv8Detection {
  bbox: [number, number, number, number];
  class: string;
  score: number;
}

let modelInstance: tf.GraphModel | null = null;
let modelConfig = {
  name: 'yolov8n',
  inputSize: 640,
  scoreThreshold: 0.25,
  iouThreshold: 0.45,
  maxDetections: 100,
};

export async function loadYOLOv8Model(modelPath: string = '/yolov8n_web_model/model.json'): Promise<tf.GraphModel> {
  if (modelInstance) {
    return modelInstance;
  }

  await tf.ready();
  await tf.setBackend('webgl');
  
  try {
    modelInstance = await tf.loadGraphModel(modelPath);
    console.log('YOLOv8 model loaded successfully');
    return modelInstance;
  } catch (error) {
    console.error('Failed to load YOLOv8 model:', error);
    throw new Error('Failed to load YOLOv8 model. Make sure the model files are in /public/yolov8n_web_model/');
  }
}

export function getYOLOv8Model(): tf.GraphModel | null {
  return modelInstance;
}

function preprocessImage(source: HTMLVideoElement | HTMLImageElement, modelWidth: number, modelHeight: number): tf.Tensor {
  const [h, w] = source instanceof HTMLVideoElement 
    ? [source.videoHeight, source.videoWidth]
    : [source.height, source.width];
  
  if (w === 0 || h === 0) {
    throw new Error('Invalid image dimensions');
  }
  
  const maxSize = Math.max(w, h);
  const xPad = maxSize - w;
  const yPad = maxSize - h;
  
  try {
    return tf.tidy(() => {
      const img = tf.browser.fromPixels(source);
      const padded = tf.pad(img, [[0, yPad], [0, xPad], [0, 0]], 114);
      const resized = tf.image.resizeBilinear(padded, [modelWidth, modelHeight]);
      const normalized = tf.div(resized, 255.0);
      const batched = tf.expandDims(normalized, 0);
      return batched;
    });
  } catch (error) {
    console.error('Error preprocessing image:', error);
    throw error;
  }
}

function nonMaxSuppression(
  boxes: number[][],
  scores: number[],
  iouThreshold: number,
  maxDetections: number
): number[] {
  const selected: number[] = [];
  const indices = scores
    .map((score, index) => ({ score, index }))
    .sort((a, b) => b.score - a.score)
    .map(item => item.index);

  while (indices.length > 0 && selected.length < maxDetections) {
    const current = indices.shift()!;
    selected.push(current);

    const currentBox = boxes[current];
    
    const remaining: number[] = [];
    for (const idx of indices) {
      const box = boxes[idx];
      const iou = calculateIoU(currentBox, box);
      if (iou < iouThreshold) {
        remaining.push(idx);
      }
    }
    
    indices.length = 0;
    indices.push(...remaining);
  }

  return selected;
}

function calculateIoU(box1: number[], box2: number[]): number {
  const [x1_min, y1_min, x1_max, y1_max] = box1;
  const [x2_min, y2_min, x2_max, y2_max] = box2;

  const intersectXMin = Math.max(x1_min, x2_min);
  const intersectYMin = Math.max(y1_min, y2_min);
  const intersectXMax = Math.min(x1_max, x2_max);
  const intersectYMax = Math.min(y1_max, y2_max);

  const intersectArea = Math.max(0, intersectXMax - intersectXMin) * Math.max(0, intersectYMax - intersectYMin);
  
  const box1Area = (x1_max - x1_min) * (y1_max - y1_min);
  const box2Area = (x2_max - x2_min) * (y2_max - y2_min);
  
  const unionArea = box1Area + box2Area - intersectArea;

  return intersectArea / unionArea;
}

export async function detectYOLOv8(
  source: HTMLVideoElement | HTMLImageElement,
  confidenceThreshold: number = 0.5
): Promise<YOLOv8Detection[]> {
  const model = getYOLOv8Model();
  if (!model) {
    throw new Error('YOLOv8 model not loaded');
  }

  if (source instanceof HTMLVideoElement && source.readyState !== 4) {
    return [];
  }

  const [h, w] = source instanceof HTMLVideoElement 
    ? [source.videoHeight, source.videoWidth]
    : [source.height, source.width];

  if (w === 0 || h === 0) {
    return [];
  }

  let outputData: number[][];
  try {
    outputData = await tf.tidy(() => {
      const input = preprocessImage(source, modelConfig.inputSize, modelConfig.inputSize);
      const output = model.predict(input) as tf.Tensor;
      const transposed = tf.transpose(output.squeeze(), [1, 0]);
      return transposed.arraySync() as number[][];
    });
  } catch (error) {
    console.error('Error during YOLOv8 inference:', error);
    return [];
  }

  const boxes: number[][] = [];
  const scores: number[] = [];
  const classIds: number[] = [];

  const maxSize = Math.max(w, h);
  const xPad = maxSize - w;
  const yPad = maxSize - h;
  const xGain = maxSize / modelConfig.inputSize;
  const yGain = maxSize / modelConfig.inputSize;

  for (let i = 0; i < outputData.length; i++) {
    const detection = outputData[i];
    const classScores = detection.slice(4);
    const maxScore = Math.max(...classScores);
    
    if (maxScore >= confidenceThreshold) {
      const classId = classScores.indexOf(maxScore);
      const [xCenter, yCenter, width, height] = detection.slice(0, 4);

      const x1 = (xCenter - width / 2) * xGain;
      const y1 = (yCenter - height / 2) * yGain;
      const x2 = (xCenter + width / 2) * xGain;
      const y2 = (yCenter + height / 2) * yGain;

      boxes.push([
        Math.max(0, x1 - xPad / 2),
        Math.max(0, y1 - yPad / 2),
        Math.min(w, x2 - xPad / 2),
        Math.min(h, y2 - yPad / 2)
      ]);
      scores.push(maxScore);
      classIds.push(classId);
    }
  }

  const selectedIndices = nonMaxSuppression(
    boxes,
    scores,
    modelConfig.iouThreshold,
    modelConfig.maxDetections
  );

  const detections: YOLOv8Detection[] = selectedIndices.map(idx => {
    const [x1, y1, x2, y2] = boxes[idx];
    return {
      bbox: [x1, y1, x2 - x1, y2 - y1],
      class: YOLO_CLASSES[classIds[idx]] || 'unknown',
      score: scores[idx],
    };
  });

  return detections;
}

export function disposeYOLOv8Model(): void {
  if (modelInstance) {
    modelInstance.dispose();
    modelInstance = null;
  }
}
