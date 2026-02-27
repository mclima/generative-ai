import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import NewsFeed from "../NewsFeed";
import { newsApi } from "@/app/lib/api/news";
import type { NewsArticle } from "@/app/types/news";

// Mock the news API
jest.mock("@/app/lib/api/news", () => ({
  newsApi: {
    getStockNews: jest.fn(),
    getMarketNews: jest.fn(),
  },
}));

const mockNewsArticles: NewsArticle[] = [
  {
    id: "1",
    headline: "Apple announces new iPhone",
    source: "TechCrunch",
    url: "https://example.com/article1",
    published_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    summary: "Apple unveils latest iPhone with new features",
    sentiment: {
      label: "positive",
      score: 0.8,
      confidence: 0.9,
    },
  },
  {
    id: "2",
    headline: "Market volatility concerns investors",
    source: "Bloomberg",
    url: "https://example.com/article2",
    published_at: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
    summary: "Stock market shows signs of volatility",
    sentiment: {
      label: "negative",
      score: -0.6,
      confidence: 0.85,
    },
  },
  {
    id: "3",
    headline: "Tech sector remains stable",
    source: "Reuters",
    url: "https://example.com/article3",
    published_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
    summary: "Technology stocks maintain steady performance",
    sentiment: {
      label: "neutral",
      score: 0.1,
      confidence: 0.7,
    },
  },
];

describe("NewsFeed Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("News Rendering", () => {
    it("renders market news when no filter is provided", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue(mockNewsArticles);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(newsApi.getMarketNews).toHaveBeenCalledWith(20);
        expect(screen.getByText("Apple announces new iPhone")).toBeInTheDocument();
        expect(screen.getByText("Market volatility concerns investors")).toBeInTheDocument();
      });
    });

    it("renders stock-specific news when filter is provided", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue([mockNewsArticles[0]]);

      render(<NewsFeed filterTicker="AAPL" />);

      await waitFor(() => {
        expect(newsApi.getStockNews).toHaveBeenCalledWith("AAPL", 20);
        expect(screen.getByText("Apple announces new iPhone")).toBeInTheDocument();
      });
    });

    it("displays all article details correctly", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue([mockNewsArticles[0]]);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText("Apple announces new iPhone")).toBeInTheDocument();
        expect(screen.getByText("TechCrunch")).toBeInTheDocument();
        expect(screen.getByText("Apple unveils latest iPhone with new features")).toBeInTheDocument();
      });
    });

    it("renders article links with correct attributes", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue([mockNewsArticles[0]]);

      render(<NewsFeed />);

      await waitFor(() => {
        const link = screen.getByText("Apple announces new iPhone").closest("a");
        expect(link).toHaveAttribute("href", "https://example.com/article1");
        expect(link).toHaveAttribute("target", "_blank");
        expect(link).toHaveAttribute("rel", "noopener noreferrer");
      });
    });
  });

  describe("Sentiment Display", () => {
    it("displays positive sentiment with correct styling", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue([mockNewsArticles[0]]);

      render(<NewsFeed />);

      await waitFor(() => {
        const sentimentBadge = screen.getByText(/positive/i);
        expect(sentimentBadge).toBeInTheDocument();
        expect(sentimentBadge.parentElement).toHaveClass("text-green-600", "bg-green-50");
      });
    });

    it("displays negative sentiment with correct styling", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue([mockNewsArticles[1]]);

      render(<NewsFeed />);

      await waitFor(() => {
        const sentimentBadge = screen.getByText(/negative/i);
        expect(sentimentBadge).toBeInTheDocument();
        expect(sentimentBadge.parentElement).toHaveClass("text-red-600", "bg-red-50");
      });
    });

    it("displays neutral sentiment with correct styling", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue([mockNewsArticles[2]]);

      render(<NewsFeed />);

      await waitFor(() => {
        const sentimentBadge = screen.getByText(/neutral/i);
        expect(sentimentBadge).toBeInTheDocument();
        expect(sentimentBadge.parentElement).toHaveClass("text-gray-600", "bg-gray-50");
      });
    });

    it("displays sentiment icons correctly", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue(mockNewsArticles);

      render(<NewsFeed />);

      await waitFor(() => {
        const badges = screen.getAllByText(/positive|negative|neutral/i);
        expect(badges.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Loading States", () => {
    it("displays loading spinner while fetching news", async () => {
      let resolveNews: (value: NewsArticle[]) => void;
      const newsPromise = new Promise<NewsArticle[]>((resolve) => {
        resolveNews = resolve;
      });
      (newsApi.getMarketNews as jest.Mock).mockReturnValue(newsPromise);

      render(<NewsFeed />);

      const spinner = document.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();

      resolveNews!(mockNewsArticles);
    });

    it("hides loading spinner after news loads", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue(mockNewsArticles);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText("Apple announces new iPhone")).toBeInTheDocument();
      });

      const spinner = document.querySelector(".animate-spin");
      expect(spinner).not.toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("displays error message when news fetch fails", async () => {
      (newsApi.getMarketNews as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText("Failed to load news. Please try again.")).toBeInTheDocument();
      });
    });

    it("shows retry button on error", async () => {
      (newsApi.getMarketNews as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText("Retry")).toBeInTheDocument();
      });
    });

    it("retries loading news when retry button is clicked", async () => {
      (newsApi.getMarketNews as jest.Mock).mockRejectedValueOnce(new Error("API Error")).mockResolvedValueOnce(mockNewsArticles);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText("Retry")).toBeInTheDocument();
      });

      const retryButton = screen.getByText("Retry");
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText("Apple announces new iPhone")).toBeInTheDocument();
      });
    });
  });

  describe("Empty State", () => {
    it("displays empty state when no articles are available", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue([]);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText("No news articles available.")).toBeInTheDocument();
      });
    });
  });

  describe("Pagination", () => {
    it("displays load more button when there are more articles", async () => {
      const manyArticles = Array.from({ length: 15 }, (_, i) => ({
        ...mockNewsArticles[0],
        id: `article-${i}`,
        headline: `Article ${i}`,
      }));

      (newsApi.getMarketNews as jest.Mock).mockResolvedValue(manyArticles);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText("Load More")).toBeInTheDocument();
      });
    });

    it("loads more articles when load more button is clicked", async () => {
      const manyArticles = Array.from({ length: 15 }, (_, i) => ({
        ...mockNewsArticles[0],
        id: `article-${i}`,
        headline: `Article ${i}`,
      }));

      (newsApi.getMarketNews as jest.Mock).mockResolvedValue(manyArticles);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText("Article 0")).toBeInTheDocument();
      });

      const initialArticleCount = screen.getAllByRole("link").length;

      const loadMoreButton = screen.getByText("Load More");
      fireEvent.click(loadMoreButton);

      await waitFor(() => {
        const newArticleCount = screen.getAllByRole("link").length;
        expect(newArticleCount).toBeGreaterThan(initialArticleCount);
      });
    });

    it("hides load more button when all articles are displayed", async () => {
      const articles = Array.from({ length: 8 }, (_, i) => ({
        ...mockNewsArticles[0],
        id: `article-${i}`,
        headline: `Article ${i}`,
      }));

      (newsApi.getMarketNews as jest.Mock).mockResolvedValue(articles);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.queryByText("Load More")).not.toBeInTheDocument();
      });
    });
  });

  describe("Filtering", () => {
    it("reloads news when filter changes", async () => {
      (newsApi.getMarketNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockNews as jest.Mock).mockResolvedValue([mockNewsArticles[0]]);

      const { rerender } = render(<NewsFeed />);

      await waitFor(() => {
        expect(newsApi.getMarketNews).toHaveBeenCalled();
      });

      rerender(<NewsFeed filterTicker="AAPL" />);

      await waitFor(() => {
        expect(newsApi.getStockNews).toHaveBeenCalledWith("AAPL", 20);
      });
    });
  });

  describe("Timestamp Formatting", () => {
    it("formats recent timestamps correctly", async () => {
      const recentArticle = {
        ...mockNewsArticles[0],
        published_at: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
      };

      (newsApi.getMarketNews as jest.Mock).mockResolvedValue([recentArticle]);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText(/\d+m ago/)).toBeInTheDocument();
      });
    });

    it("formats hour-old timestamps correctly", async () => {
      const hourOldArticle = {
        ...mockNewsArticles[0],
        published_at: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
      };

      (newsApi.getMarketNews as jest.Mock).mockResolvedValue([hourOldArticle]);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText(/\d+h ago/)).toBeInTheDocument();
      });
    });

    it("formats day-old timestamps correctly", async () => {
      const dayOldArticle = {
        ...mockNewsArticles[0],
        published_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
      };

      (newsApi.getMarketNews as jest.Mock).mockResolvedValue([dayOldArticle]);

      render(<NewsFeed />);

      await waitFor(() => {
        expect(screen.getByText(/\d+d ago/)).toBeInTheDocument();
      });
    });
  });
});
