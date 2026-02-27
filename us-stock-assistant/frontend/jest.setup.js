import "@testing-library/jest-dom";

// Mock ResizeObserver for Recharts
global.ResizeObserver = class ResizeObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() {
    // Mock implementation
    this.callback([{ contentRect: { width: 800, height: 600 } }], this);
  }
  unobserve() {
    // Mock implementation
  }
  disconnect() {
    // Mock implementation
  }
};
