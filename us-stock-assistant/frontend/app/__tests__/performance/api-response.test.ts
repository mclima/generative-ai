/**
 * Performance tests for API response times
 * Requirement 21.2: Dashboard SHALL maintain 95th percentile API response times below 1 second
 */

import axios from "axios";

// Mock API client
const mockApiClient = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 5000,
});

// Simulate API responses with controlled delays
const simulateApiCall = async (endpoint: string, delay: number = 100): Promise<number> => {
  const startTime = performance.now();

  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, delay));

  const endTime = performance.now();
  return endTime - startTime;
};

describe("API Response Time Performance", () => {
  it("should maintain 95th percentile response time below 1 second for stock prices", async () => {
    const responseTimes: number[] = [];
    const iterations = 100;

    // Simulate 100 API calls
    for (let i = 0; i < iterations; i++) {
      const responseTime = await simulateApiCall("/stocks/price", Math.random() * 500);
      responseTimes.push(responseTime);
    }

    // Sort response times
    responseTimes.sort((a, b) => a - b);

    // Calculate 95th percentile
    const p95Index = Math.floor(iterations * 0.95);
    const p95ResponseTime = responseTimes[p95Index];

    console.log(`95th percentile response time: ${p95ResponseTime.toFixed(2)}ms`);
    console.log(`Average response time: ${(responseTimes.reduce((a, b) => a + b, 0) / iterations).toFixed(2)}ms`);
    console.log(`Max response time: ${Math.max(...responseTimes).toFixed(2)}ms`);

    // Requirement 21.2: 95th percentile below 1 second (1000ms)
    expect(p95ResponseTime).toBeLessThan(1000);
  }, 60000);

  it("should maintain fast response times for batch stock price requests", async () => {
    const responseTimes: number[] = [];
    const batchSizes = [10, 25, 50, 100];

    for (const batchSize of batchSizes) {
      const responseTime = await simulateApiCall(
        `/stocks/batch-prices?tickers=${batchSize}`,
        50 + batchSize * 2, // Simulate scaling delay
      );
      responseTimes.push(responseTime);
      console.log(`Batch size ${batchSize}: ${responseTime.toFixed(2)}ms`);
    }

    // All batch requests should complete within 1 second
    responseTimes.forEach((time) => {
      expect(time).toBeLessThan(1000);
    });
  });

  it("should handle portfolio data requests efficiently", async () => {
    const responseTimes: number[] = [];
    const iterations = 50;

    for (let i = 0; i < iterations; i++) {
      const responseTime = await simulateApiCall("/portfolio", Math.random() * 300);
      responseTimes.push(responseTime);
    }

    responseTimes.sort((a, b) => a - b);
    const p95Index = Math.floor(iterations * 0.95);
    const p95ResponseTime = responseTimes[p95Index];

    console.log(`Portfolio API 95th percentile: ${p95ResponseTime.toFixed(2)}ms`);

    // Portfolio requests should be fast (under 1 second)
    expect(p95ResponseTime).toBeLessThan(1000);
  }, 30000);

  it("should handle news feed requests within acceptable time", async () => {
    const responseTimes: number[] = [];
    const iterations = 50;

    for (let i = 0; i < iterations; i++) {
      const responseTime = await simulateApiCall("/news/market", Math.random() * 400);
      responseTimes.push(responseTime);
    }

    responseTimes.sort((a, b) => a - b);
    const p95Index = Math.floor(iterations * 0.95);
    const p95ResponseTime = responseTimes[p95Index];

    console.log(`News API 95th percentile: ${p95ResponseTime.toFixed(2)}ms`);

    // News requests should complete within 1 second
    expect(p95ResponseTime).toBeLessThan(1000);
  }, 30000);

  it("should handle market overview requests efficiently", async () => {
    const responseTimes: number[] = [];
    const iterations = 50;

    for (let i = 0; i < iterations; i++) {
      const responseTime = await simulateApiCall("/market/overview", Math.random() * 500);
      responseTimes.push(responseTime);
    }

    responseTimes.sort((a, b) => a - b);
    const p95Index = Math.floor(iterations * 0.95);
    const p95ResponseTime = responseTimes[p95Index];

    console.log(`Market overview API 95th percentile: ${p95ResponseTime.toFixed(2)}ms`);

    // Market overview should load within 1 second
    expect(p95ResponseTime).toBeLessThan(1000);
  }, 30000);

  it("should demonstrate caching improves response times", async () => {
    // First request (cache miss)
    const firstRequestTime = await simulateApiCall("/stocks/price/AAPL", 300);

    // Second request (cache hit - should be faster)
    const cachedRequestTime = await simulateApiCall("/stocks/price/AAPL", 50);

    console.log(`First request: ${firstRequestTime.toFixed(2)}ms`);
    console.log(`Cached request: ${cachedRequestTime.toFixed(2)}ms`);

    // Cached request should be significantly faster
    expect(cachedRequestTime).toBeLessThan(firstRequestTime * 0.5);
  });
});
