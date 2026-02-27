import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import StockNewsSection from "../StockNewsSection";
import { newsApi } from "@/app/lib/api/news";
import type { NewsArticle, StockSentiment } from "@/app/types/news";

// Mock the news API
jest.mock("@/app/lib/api/news", () => ({
  newsApi: {
    getStockNews: jest.fn(),
    getStockSentiment: jest.fn(),
  },
}));

const mockNewsArticles: NewsArticle[] = [
  {
    id: "1",
    headline: "Apple announces record earnings",
    source: "CNBC",
    url: "https://example.com/article1",
    published_at: new Date(Date.now() - 3600000).toISOString(),
    summary: "Apple reports strong quarterly results",
    sentiment: {
      label: "positive",
      score: 0.85,
      confidence: 0.92,
    },
  },
  {
    id: "2",
    headline: "Apple faces supply chain challenges",
    source: "Bloomberg",
    url: "https://example.com/article2",
    published_at: new Date(Date.now() - 7200000).toISOString(),
    summary: "Supply chain issues impact production",
    sentiment: {
      label: "negative",
      score: -0.5,
      confidence: 0.8,
    },
  },
];

const mockSentiment: StockSentiment = {
  ticker: "AAPL",
  overall_sentiment: {
    label: "positive",
    score: 0.65,
    confidence: 0.88,
  },
  article_count: 15,
  recent_articles: mockNewsArticles,
};

describe("StockNewsSection Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Component Rendering", () => {
    it("renders the component with title", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("News & Sentiment")).toBeInTheDocument();
      });
    });

    it("fetches news and sentiment on mount", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(newsApi.getStockNews).toHaveBeenCalledWith("AAPL", 5);
        expect(newsApi.getStockSentiment).toHaveBeenCalledWith("AAPL");
      });
    });

    it("respects custom limit prop", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" limit={10} />);

      await waitFor(() => {
        expect(newsApi.getStockNews).toHaveBeenCalledWith("AAPL", 10);
      });
    });
  });

  describe("Sentiment Summary Display", () => {
    it("displays overall sentiment summary", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText(/positive.*sentiment/i)).toBeInTheDocument();
        expect(screen.getByText("Based on 15 recent articles")).toBeInTheDocument();
      });
    });

    it("displays sentiment score", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("65")).toBeInTheDocument();
        expect(screen.getByText("Sentiment Score")).toBeInTheDocument();
      });
    });

    it("applies correct styling for positive sentiment", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        const sentimentText = screen.getByText(/positive.*sentiment/i);
        const sentimentBox = sentimentText.closest(".mb-6");
        expect(sentimentBox).toHaveClass("text-green-600", "bg-green-50");
      });
    });

    it("applies correct styling for negative sentiment", async () => {
      const negativeSentiment = {
        ...mockSentiment,
        overall_sentiment: {
          label: "negative" as const,
          score: -0.4,
          confidence: 0.85,
        },
      };

      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(negativeSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        const sentimentText = screen.getByText(/negative.*sentiment/i);
        const sentimentBox = sentimentText.closest(".mb-6");
        expect(sentimentBox).toHaveClass("text-red-600", "bg-red-50");
      });
    });

    it("applies correct styling for neutral sentiment", async () => {
      const neutralSentiment = {
        ...mockSentiment,
        overall_sentiment: {
          label: "neutral" as const,
          score: 0.05,
          confidence: 0.7,
        },
      };

      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(neutralSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        const sentimentText = screen.getByText(/neutral.*sentiment/i);
        const sentimentBox = sentimentText.closest(".mb-6");
        expect(sentimentBox).toHaveClass("text-gray-600", "bg-gray-50");
      });
    });
  });

  describe("News Articles Display", () => {
    it("displays recent news articles", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("Apple announces record earnings")).toBeInTheDocument();
        expect(screen.getByText("Apple faces supply chain challenges")).toBeInTheDocument();
      });
    });

    it("displays article metadata", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("CNBC")).toBeInTheDocument();
        expect(screen.getByText("Bloomberg")).toBeInTheDocument();
      });
    });

    it("displays article summaries", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("Apple reports strong quarterly results")).toBeInTheDocument();
        expect(screen.getByText("Supply chain issues impact production")).toBeInTheDocument();
      });
    });

    it("renders article links correctly", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        const link = screen.getByText("Apple announces record earnings").closest("a");
        expect(link).toHaveAttribute("href", "https://example.com/article1");
        expect(link).toHaveAttribute("target", "_blank");
        expect(link).toHaveAttribute("rel", "noopener noreferrer");
      });
    });

    it("displays sentiment badges for articles", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        const sentimentBadges = screen.getAllByText(/positive|negative/i);
        expect(sentimentBadges.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Loading States", () => {
    it("displays loading spinner while fetching data", async () => {
      let resolveNews: (value: NewsArticle[]) => void;
      const newsPromise = new Promise<NewsArticle[]>((resolve) => {
        resolveNews = resolve;
      });
      (newsApi.getStockNews as jest.Mock).mockReturnValue(newsPromise);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      const spinner = document.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();

      resolveNews!(mockNewsArticles);
    });

    it("hides loading spinner after data loads", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("Apple announces record earnings")).toBeInTheDocument();
      });

      const spinner = document.querySelector(".animate-spin");
      expect(spinner).not.toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("displays error message when both requests fail", async () => {
      (newsApi.getStockNews as jest.Mock).mockRejectedValue(new Error("API Error"));
      (newsApi.getStockSentiment as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("Failed to load news data. Please try again.")).toBeInTheDocument();
      });
    });

    it("shows retry button on error", async () => {
      (newsApi.getStockNews as jest.Mock).mockRejectedValue(new Error("API Error"));
      (newsApi.getStockSentiment as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("Retry")).toBeInTheDocument();
      });
    });

    it("retries loading data when retry button is clicked", async () => {
      (newsApi.getStockNews as jest.Mock).mockRejectedValueOnce(new Error("API Error")).mockResolvedValueOnce(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockRejectedValueOnce(new Error("API Error")).mockResolvedValueOnce(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("Retry")).toBeInTheDocument();
      });

      const retryButton = screen.getByText("Retry");
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText("Apple announces record earnings")).toBeInTheDocument();
      });
    });

    it("displays partial data when only one request fails", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockRejectedValue(new Error("API Error"));

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("Apple announces record earnings")).toBeInTheDocument();
      });

      expect(screen.queryByText("Positive Sentiment")).not.toBeInTheDocument();
    });
  });

  describe("Empty State", () => {
    it("displays empty state when no articles are available", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue([]);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(screen.getByText("No recent news available for AAPL")).toBeInTheDocument();
      });
    });
  });

  describe("Ticker Changes", () => {
    it("reloads data when ticker changes", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      const { rerender } = render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        expect(newsApi.getStockNews).toHaveBeenCalledWith("AAPL", 5);
      });

      jest.clearAllMocks();

      rerender(<StockNewsSection ticker="MSFT" />);

      await waitFor(() => {
        expect(newsApi.getStockNews).toHaveBeenCalledWith("MSFT", 5);
        expect(newsApi.getStockSentiment).toHaveBeenCalledWith("MSFT");
      });
    });
  });

  describe("Timestamp Formatting", () => {
    it("formats timestamps correctly", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        const timestamps = screen.getAllByText(/\d+h ago/);
        expect(timestamps.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Sentiment Icons", () => {
    it("displays appropriate icons for different sentiments", async () => {
      (newsApi.getStockNews as jest.Mock).mockResolvedValue(mockNewsArticles);
      (newsApi.getStockSentiment as jest.Mock).mockResolvedValue(mockSentiment);

      render(<StockNewsSection ticker="AAPL" />);

      await waitFor(() => {
        const svgs = document.querySelectorAll("svg");
        expect(svgs.length).toBeGreaterThan(0);
      });
    });
  });
});
