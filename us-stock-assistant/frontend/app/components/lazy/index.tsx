import dynamic from 'next/dynamic';

// Lazy load chart components (heavy due to recharts)
export const PortfolioValueChart = dynamic(
  () => import('../charts/PortfolioValueChart').then((mod) => mod.PortfolioValueChart),
  {
    loading: () => <div className="h-64 bg-gray-100 animate-pulse rounded" />,
    ssr: false, // Charts don't need SSR
  }
);

export const PortfolioCompositionChart = dynamic(
  () => import('../charts/PortfolioCompositionChart').then((mod) => mod.PortfolioCompositionChart),
  {
    loading: () => <div className="h-64 bg-gray-100 animate-pulse rounded" />,
    ssr: false,
  }
);

export const StockPriceChart = dynamic(
  () => import('../charts/StockPriceChart').then((mod) => mod.StockPriceChart),
  {
    loading: () => <div className="h-64 bg-gray-100 animate-pulse rounded" />,
    ssr: false,
  }
);

// Lazy load analysis panels (heavy due to AI processing)
export const StockAnalysisPanel = dynamic(
  () => import('../StockAnalysisPanel').then((mod) => ({ default: mod.default })),
  {
    loading: () => (
      <div className="p-4 bg-white rounded-lg shadow">
        <div className="h-8 bg-gray-200 animate-pulse rounded mb-4" />
        <div className="space-y-2">
          <div className="h-4 bg-gray-100 animate-pulse rounded" />
          <div className="h-4 bg-gray-100 animate-pulse rounded" />
          <div className="h-4 bg-gray-100 animate-pulse rounded w-3/4" />
        </div>
      </div>
    ),
  }
);

export const PortfolioAnalysisPanel = dynamic(
  () => import('../PortfolioAnalysisPanel').then((mod) => ({ default: mod.default })),
  {
    loading: () => (
      <div className="p-4 bg-white rounded-lg shadow">
        <div className="h-8 bg-gray-200 animate-pulse rounded mb-4" />
        <div className="space-y-2">
          <div className="h-4 bg-gray-100 animate-pulse rounded" />
          <div className="h-4 bg-gray-100 animate-pulse rounded" />
          <div className="h-4 bg-gray-100 animate-pulse rounded w-3/4" />
        </div>
      </div>
    ),
  }
);

// Lazy load sector heatmap (heavy visualization)
export const SectorHeatmap = dynamic(
  () => import('../SectorHeatmap').then((mod) => ({ default: mod.default })),
  {
    loading: () => <div className="h-96 bg-gray-100 animate-pulse rounded" />,
    ssr: false,
  }
);

// Lazy load modals (not needed on initial load)
export const AddStockModal = dynamic(
  () => import('../AddStockModal').then((mod) => ({ default: mod.default })),
  {
    loading: () => null,
  }
);

export const AlertModal = dynamic(
  () => import('../AlertModal').then((mod) => ({ default: mod.default })),
  {
    loading: () => null,
  }
);

export const ImportPortfolioModal = dynamic(
  () => import('../ImportPortfolioModal').then((mod) => ({ default: mod.default })),
  {
    loading: () => null,
  }
);
