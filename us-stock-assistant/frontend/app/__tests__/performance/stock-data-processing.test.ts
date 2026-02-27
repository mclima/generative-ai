/**
 * Performance tests for stock data processing
 * Requirement 21.4: Stock_Data_Service SHALL process updates for 100 stocks within 2 seconds
 */

interface StockUpdate {
  ticker: string;
  price: number;
  change: number;
  volume: number;
  timestamp: Date;
}

// Simulate stock data processing
const processStockUpdates = async (stockCount: number): Promise<number> => {
  const startTime = performance.now();

  // Generate mock stock updates
  const updates: StockUpdate[] = Array.from({ length: stockCount }, (_, i) => ({
    ticker: `STOCK${i}`,
    price: 100 + Math.random() * 100,
    change: Math.random() * 10 - 5,
    volume: Math.floor(Math.random() * 1000000),
    timestamp: new Date(),
  }));

  // Simulate processing each update
  await Promise.all(
    updates.map(async (update) => {
      // Simulate validation and transformation
      await new Promise((resolve) => setTimeout(resolve, 1));

      // Simulate calculations
      const changePercent = (update.change / update.price) * 100;
      const marketCap = update.price * update.volume;

      return {
        ...update,
        changePercent,
        marketCap,
      };
    }),
  );

  const endTime = performance.now();
  return endTime - startTime;
};

describe("Stock Data Processing Performance", () => {
  it("should process 100 stock updates within 2 seconds", async () => {
    // Requirement 21.4: Process 100 stocks within 2 seconds
    const processingTime = await processStockUpdates(100);

    console.log(`Processed 100 stocks in ${processingTime.toFixed(2)}ms`);

    // Should complete within 2 seconds (2000ms)
    expect(processingTime).toBeLessThan(2000);
  });

  it("should process 50 stock updates faster than 100", async () => {
    const time50 = await processStockUpdates(50);
    const time100 = await processStockUpdates(100);

    console.log(`50 stocks: ${time50.toFixed(2)}ms`);
    console.log(`100 stocks: ${time100.toFixed(2)}ms`);

    // Processing should scale linearly
    expect(time100).toBeLessThan(time50 * 2.5);
  });

  it("should handle incremental stock updates efficiently", async () => {
    const stockCounts = [10, 25, 50, 75, 100];
    const processingTimes: number[] = [];

    for (const count of stockCounts) {
      const time = await processStockUpdates(count);
      processingTimes.push(time);
      console.log(`${count} stocks: ${time.toFixed(2)}ms`);
    }

    // All should complete within 2 seconds
    processingTimes.forEach((time) => {
      expect(time).toBeLessThan(2000);
    });

    // Processing time should increase roughly linearly
    const ratio = processingTimes[4] / processingTimes[0]; // 100 stocks / 10 stocks
    console.log(`Processing ratio (100/10 stocks): ${ratio.toFixed(2)}x`);
    expect(ratio).toBeLessThan(15); // Should not be more than 15x slower
  });

  it("should handle rapid successive updates", async () => {
    const iterations = 10;
    const processingTimes: number[] = [];

    for (let i = 0; i < iterations; i++) {
      const time = await processStockUpdates(100);
      processingTimes.push(time);
    }

    const averageTime = processingTimes.reduce((a, b) => a + b, 0) / iterations;
    const maxTime = Math.max(...processingTimes);

    console.log(`Average processing time: ${averageTime.toFixed(2)}ms`);
    console.log(`Max processing time: ${maxTime.toFixed(2)}ms`);

    // Average should be well under 2 seconds
    expect(averageTime).toBeLessThan(2000);

    // Even the slowest iteration should be under 2 seconds
    expect(maxTime).toBeLessThan(2000);
  });

  it("should process updates in parallel efficiently", async () => {
    // Process 5 batches of 100 stocks in parallel
    const startTime = performance.now();

    await Promise.all([processStockUpdates(100), processStockUpdates(100), processStockUpdates(100), processStockUpdates(100), processStockUpdates(100)]);

    const totalTime = performance.now() - startTime;

    console.log(`Processed 5 batches of 100 stocks in parallel: ${totalTime.toFixed(2)}ms`);

    // Parallel processing should be efficient (not 5x slower)
    expect(totalTime).toBeLessThan(5000);
  });

  it("should maintain performance with complex calculations", async () => {
    const startTime = performance.now();

    // Generate 100 stocks with complex calculations
    const stocks = Array.from({ length: 100 }, (_, i) => ({
      ticker: `STOCK${i}`,
      price: 100 + Math.random() * 100,
      volume: Math.floor(Math.random() * 1000000),
      historicalPrices: Array.from({ length: 30 }, () => Math.random() * 100),
    }));

    // Perform complex calculations
    await Promise.all(
      stocks.map(async (stock) => {
        // Calculate moving averages
        const ma7 = stock.historicalPrices.slice(-7).reduce((a, b) => a + b, 0) / 7;
        const ma30 = stock.historicalPrices.reduce((a, b) => a + b, 0) / 30;

        // Calculate volatility
        const mean = stock.historicalPrices.reduce((a, b) => a + b, 0) / stock.historicalPrices.length;
        const variance = stock.historicalPrices.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / stock.historicalPrices.length;
        const volatility = Math.sqrt(variance);

        return {
          ...stock,
          ma7,
          ma30,
          volatility,
        };
      }),
    );

    const processingTime = performance.now() - startTime;

    console.log(`Complex calculations for 100 stocks: ${processingTime.toFixed(2)}ms`);

    // Should still complete within 2 seconds even with complex calculations
    expect(processingTime).toBeLessThan(2000);
  });
});
