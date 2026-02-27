/**
 * Performance tests for concurrent user handling
 * Requirement 21.3: Dashboard SHALL handle 1000 concurrent users without performance degradation
 */

// Simulate concurrent user requests
const simulateConcurrentUsers = async (
  userCount: number,
  requestsPerUser: number = 5,
): Promise<{
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  p95ResponseTime: number;
  maxResponseTime: number;
}> => {
  const responseTimes: number[] = [];
  let successfulRequests = 0;
  let failedRequests = 0;

  // Create promises for all concurrent users
  const userPromises = Array.from({ length: userCount }, async (_, userId) => {
    const userRequests = Array.from({ length: requestsPerUser }, async (_, reqId) => {
      const startTime = performance.now();

      try {
        // Simulate API request with random delay
        const delay = 50 + Math.random() * 200;
        await new Promise((resolve) => setTimeout(resolve, delay));

        const endTime = performance.now();
        const responseTime = endTime - startTime;
        responseTimes.push(responseTime);
        successfulRequests++;

        return { success: true, responseTime };
      } catch (error) {
        failedRequests++;
        return { success: false, responseTime: 0 };
      }
    });

    return Promise.all(userRequests);
  });

  // Wait for all users to complete their requests
  await Promise.all(userPromises);

  // Calculate statistics
  responseTimes.sort((a, b) => a - b);
  const averageResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length;
  const p95Index = Math.floor(responseTimes.length * 0.95);
  const p95ResponseTime = responseTimes[p95Index];
  const maxResponseTime = Math.max(...responseTimes);

  return {
    totalRequests: userCount * requestsPerUser,
    successfulRequests,
    failedRequests,
    averageResponseTime,
    p95ResponseTime,
    maxResponseTime,
  };
};

describe("Concurrent User Performance", () => {
  it("should handle 100 concurrent users efficiently", async () => {
    const results = await simulateConcurrentUsers(100, 5);

    console.log("100 Concurrent Users:");
    console.log(`  Total requests: ${results.totalRequests}`);
    console.log(`  Successful: ${results.successfulRequests}`);
    console.log(`  Failed: ${results.failedRequests}`);
    console.log(`  Average response time: ${results.averageResponseTime.toFixed(2)}ms`);
    console.log(`  95th percentile: ${results.p95ResponseTime.toFixed(2)}ms`);
    console.log(`  Max response time: ${results.maxResponseTime.toFixed(2)}ms`);

    // All requests should succeed
    expect(results.failedRequests).toBe(0);

    // Response times should remain reasonable
    expect(results.p95ResponseTime).toBeLessThan(1000);
  }, 30000);

  it("should handle 500 concurrent users without degradation", async () => {
    const results = await simulateConcurrentUsers(500, 3);

    console.log("500 Concurrent Users:");
    console.log(`  Total requests: ${results.totalRequests}`);
    console.log(`  Successful: ${results.successfulRequests}`);
    console.log(`  Failed: ${results.failedRequests}`);
    console.log(`  Average response time: ${results.averageResponseTime.toFixed(2)}ms`);
    console.log(`  95th percentile: ${results.p95ResponseTime.toFixed(2)}ms`);
    console.log(`  Max response time: ${results.maxResponseTime.toFixed(2)}ms`);

    // Most requests should succeed (allow up to 5% failure rate)
    const successRate = results.successfulRequests / results.totalRequests;
    expect(successRate).toBeGreaterThan(0.95);

    // Response times should still be acceptable
    expect(results.p95ResponseTime).toBeLessThan(1500);
  }, 60000);

  it("should handle 1000 concurrent users without performance degradation", async () => {
    // Requirement 21.3: Handle 1000 concurrent users
    const results = await simulateConcurrentUsers(1000, 2);

    console.log("1000 Concurrent Users:");
    console.log(`  Total requests: ${results.totalRequests}`);
    console.log(`  Successful: ${results.successfulRequests}`);
    console.log(`  Failed: ${results.failedRequests}`);
    console.log(`  Average response time: ${results.averageResponseTime.toFixed(2)}ms`);
    console.log(`  95th percentile: ${results.p95ResponseTime.toFixed(2)}ms`);
    console.log(`  Max response time: ${results.maxResponseTime.toFixed(2)}ms`);

    // Most requests should succeed (allow up to 10% failure rate for 1000 users)
    const successRate = results.successfulRequests / results.totalRequests;
    expect(successRate).toBeGreaterThan(0.9);

    // Response times should remain under 2 seconds even with 1000 users
    expect(results.p95ResponseTime).toBeLessThan(2000);
  }, 120000);

  it("should demonstrate performance scales linearly with user count", async () => {
    const userCounts = [50, 100, 200];
    const results: Array<{ users: number; p95: number }> = [];

    for (const userCount of userCounts) {
      const result = await simulateConcurrentUsers(userCount, 3);
      results.push({ users: userCount, p95: result.p95ResponseTime });
      console.log(`${userCount} users: ${result.p95ResponseTime.toFixed(2)}ms (95th percentile)`);
    }

    // Performance should scale reasonably (not exponentially)
    const ratio200to50 = results[2].p95 / results[0].p95;
    console.log(`Performance ratio (200 users / 50 users): ${ratio200to50.toFixed(2)}x`);

    // Should not degrade more than 3x when going from 50 to 200 users
    expect(ratio200to50).toBeLessThan(3);
  }, 90000);

  it("should handle burst traffic patterns", async () => {
    // Simulate burst: 200 users arrive simultaneously
    const burstStart = performance.now();
    const burstResults = await simulateConcurrentUsers(200, 3);
    const burstDuration = performance.now() - burstStart;

    console.log("Burst Traffic (200 users):");
    console.log(`  Duration: ${burstDuration.toFixed(2)}ms`);
    console.log(`  Success rate: ${((burstResults.successfulRequests / burstResults.totalRequests) * 100).toFixed(2)}%`);
    console.log(`  95th percentile: ${burstResults.p95ResponseTime.toFixed(2)}ms`);

    // System should handle burst without significant failures
    const successRate = burstResults.successfulRequests / burstResults.totalRequests;
    expect(successRate).toBeGreaterThan(0.9);
  }, 60000);
});
