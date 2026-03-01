import * as cocoSsd from '@tensorflow-models/coco-ssd';
import '@tensorflow/tfjs-backend-webgl';
import * as tf from '@tensorflow/tfjs';
import { loadYOLOv8Model, getYOLOv8Model, detectYOLOv8 } from './yolov8-detection';

export type ModelType = 'coco-ssd' | 'yolov8';

let cocoSsdInstance: cocoSsd.ObjectDetection | null = null;
let currentModelType: ModelType = 'yolov8';

export function setModelType(type: ModelType): void {
  currentModelType = type;
}

export function getModelType(): ModelType {
  return currentModelType;
}

export async function loadModel(): Promise<cocoSsd.ObjectDetection | tf.GraphModel> {
  try {
    if (currentModelType === 'yolov8') {
      return await loadYOLOv8Model();
    }
    
    if (cocoSsdInstance) {
      return cocoSsdInstance;
    }

    await tf.ready();
    
    try {
      await tf.setBackend('webgl');
    } catch (error) {
      console.warn('Failed to set WebGL backend, using default:', error);
    }
    
    cocoSsdInstance = await cocoSsd.load({
      base: 'lite_mobilenet_v2'
    });
    
    return cocoSsdInstance;
  } catch (error) {
    console.error('Failed to load detection model:', error);
    throw new Error(
      error instanceof Error 
        ? `Model loading failed: ${error.message}` 
        : 'Failed to load detection model. Please check your internet connection and try again.'
    );
  }
}

export function getModel(): cocoSsd.ObjectDetection | tf.GraphModel | null {
  if (currentModelType === 'yolov8') {
    return getYOLOv8Model();
  }
  return cocoSsdInstance;
}

export { detectYOLOv8 };
