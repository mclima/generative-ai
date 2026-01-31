import * as cocoSsd from '@tensorflow-models/coco-ssd';
import '@tensorflow/tfjs-backend-webgl';
import * as tf from '@tensorflow/tfjs';

let modelInstance: cocoSsd.ObjectDetection | null = null;

export async function loadModel(): Promise<cocoSsd.ObjectDetection> {
  if (modelInstance) {
    return modelInstance;
  }

  await tf.ready();
  await tf.setBackend('webgl');
  
  modelInstance = await cocoSsd.load({
    base: 'lite_mobilenet_v2'
  });
  
  return modelInstance;
}

export function getModel(): cocoSsd.ObjectDetection | null {
  return modelInstance;
}
