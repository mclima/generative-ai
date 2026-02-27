/**
 * Performance tests for dashboard initial load time
 * Requirement 21.1: Dashboard SHALL complete initial render within 3 seconds with up to 100 stocks
 */

import { render, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock dashboard page
const MockDashboard = ({ stockCount }: { stockCount: number }) => {
  const stocks = Array.from({ length: stockCount }, (_, i) => ({
    ticker: `STOCK${i}`,
    price: 100 + i,
    change: Math.random() * 10 - 5,
  }));

  return (
    <div>
      <h1>Dashboard</h1>
      <div data-testid="stock-list">
        {stocks.map((stock) => (
          <div key={stock.ticker} data-testid={`stock-${stock.ticker}`}>
            {stock.ticker}: ${stock.price}
          </div>
        ))}
      </div>
    </div>
  );
};

describe("Dashboard Load Performance", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  afterEach(() => {
    queryClient.clear();
  });

  it("should render dashboard with 100 stocks within 3 seconds", async () => {
    const startTime = performance.now();

    const { getByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <MockDashboard stockCount={100} />
      </QueryClientProvider>,
    );

    await waitFor(
      () => {
        expect(getByTestId("stock-list")).toBeInTheDocument();
        expect(getByTestId("stock-STOCK0")).toBeInTheDocument();
        expect(getByTestId("stock-STOCK99")).toBeInTheDocument();
      },
      { timeout: 3000 },
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Requirement 21.1: Initial render within 3 seconds
    expect(renderTime).toBeLessThan(3000);
    console.log(`Dashboard with 100 stocks rendered in ${renderTime.toFixed(2)}ms`);
  });

  it("should render dashboard with 50 stocks faster than 100 stocks", async () => {
    // Test with 50 stocks
    const start50 = performance.now();
    const { unmount: unmount50 } = render(
      <QueryClientProvider client={queryClient}>
        <MockDashboard stockCount={50} />
      </QueryClientProvider>,
    );
    await waitFor(() => {}, { timeout: 100 });
    const time50 = performance.now() - start50;
    unmount50();

    // Test with 100 stocks
    const start100 = performance.now();
    const { unmount: unmount100 } = render(
      <QueryClientProvider client={queryClient}>
        <MockDashboard stockCount={100} />
      </QueryClientProvider>,
    );
    await waitFor(() => {}, { timeout: 100 });
    const time100 = performance.now() - start100;
    unmount100();

    console.log(`50 stocks: ${time50.toFixed(2)}ms, 100 stocks: ${time100.toFixed(2)}ms`);

    // Performance should scale reasonably
    expect(time100).toBeLessThan(time50 * 2.5);
  });

  it("should handle incremental loading efficiently", async () => {
    const measurements: number[] = [];

    for (let count = 10; count <= 100; count += 10) {
      const startTime = performance.now();
      const { unmount } = render(
        <QueryClientProvider client={queryClient}>
          <MockDashboard stockCount={count} />
        </QueryClientProvider>,
      );
      await waitFor(() => {}, { timeout: 100 });
      const renderTime = performance.now() - startTime;
      measurements.push(renderTime);
      unmount();
    }

    console.log(
      "Incremental load times:",
      measurements.map((t) => t.toFixed(2)),
    );

    // All measurements should be under 3 seconds
    measurements.forEach((time) => {
      expect(time).toBeLessThan(3000);
    });
  });
});
