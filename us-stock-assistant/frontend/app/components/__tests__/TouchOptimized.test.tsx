import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { TouchOptimizedButton, TouchOptimizedLink, SwipeableContainer } from "../TouchOptimized";

describe("TouchOptimizedButton", () => {
  it("should render button with children", () => {
    render(<TouchOptimizedButton>Click Me</TouchOptimizedButton>);
    expect(screen.getByText("Click Me")).toBeInTheDocument();
  });

  it("should apply primary variant styles by default", () => {
    render(<TouchOptimizedButton>Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("bg-blue-600", "text-white");
  });

  it("should apply secondary variant styles", () => {
    render(<TouchOptimizedButton variant="secondary">Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("bg-gray-200", "text-gray-800");
  });

  it("should apply danger variant styles", () => {
    render(<TouchOptimizedButton variant="danger">Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("bg-red-500", "text-white");
  });

  it("should apply ghost variant styles", () => {
    render(<TouchOptimizedButton variant="ghost">Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("bg-transparent", "text-gray-700");
  });

  it("should apply medium size by default", () => {
    render(<TouchOptimizedButton>Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("px-6", "py-3", "text-base");
  });

  it("should apply small size", () => {
    render(<TouchOptimizedButton size="sm">Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("px-4", "py-2", "text-sm");
  });

  it("should apply large size", () => {
    render(<TouchOptimizedButton size="lg">Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("px-8", "py-4", "text-lg");
  });

  it("should have touch-target class for accessibility", () => {
    render(<TouchOptimizedButton>Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("touch-target");
  });

  it("should have active scale animation", () => {
    render(<TouchOptimizedButton>Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("active:scale-95");
  });

  it("should handle click events", () => {
    const handleClick = jest.fn();
    render(<TouchOptimizedButton onClick={handleClick}>Button</TouchOptimizedButton>);

    const button = screen.getByText("Button");
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("should be disabled when disabled prop is true", () => {
    render(<TouchOptimizedButton disabled>Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toBeDisabled();
    expect(button).toHaveClass("disabled:opacity-50", "disabled:cursor-not-allowed");
  });

  it("should merge custom className", () => {
    render(<TouchOptimizedButton className="custom-class">Button</TouchOptimizedButton>);
    const button = screen.getByText("Button");
    expect(button).toHaveClass("custom-class");
  });
});

describe("TouchOptimizedLink", () => {
  it("should render link with children", () => {
    render(<TouchOptimizedLink href="/test">Link Text</TouchOptimizedLink>);
    expect(screen.getByText("Link Text")).toBeInTheDocument();
  });

  it("should have correct href attribute", () => {
    render(<TouchOptimizedLink href="/test">Link</TouchOptimizedLink>);
    const link = screen.getByText("Link");
    expect(link).toHaveAttribute("href", "/test");
  });

  it("should have link-touch class", () => {
    render(<TouchOptimizedLink href="/test">Link</TouchOptimizedLink>);
    const link = screen.getByText("Link");
    expect(link).toHaveClass("link-touch");
  });

  it("should handle click events", () => {
    const handleClick = jest.fn();
    render(
      <TouchOptimizedLink href="/test" onClick={handleClick}>
        Link
      </TouchOptimizedLink>,
    );

    const link = screen.getByText("Link");
    fireEvent.click(link);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("should merge custom className", () => {
    render(
      <TouchOptimizedLink href="/test" className="custom-class">
        Link
      </TouchOptimizedLink>,
    );
    const link = screen.getByText("Link");
    expect(link).toHaveClass("custom-class", "link-touch");
  });
});

describe("SwipeableContainer", () => {
  it("should render children", () => {
    render(
      <SwipeableContainer>
        <div>Swipeable Content</div>
      </SwipeableContainer>,
    );
    expect(screen.getByText("Swipeable Content")).toBeInTheDocument();
  });

  it("should detect left swipe", () => {
    const onSwipeLeft = jest.fn();
    const { container } = render(
      <SwipeableContainer onSwipeLeft={onSwipeLeft}>
        <div>Content</div>
      </SwipeableContainer>,
    );

    const element = container.firstChild as HTMLElement;

    // Simulate swipe left
    fireEvent.touchStart(element, {
      targetTouches: [{ clientX: 200 }],
    });
    fireEvent.touchMove(element, {
      targetTouches: [{ clientX: 100 }],
    });
    fireEvent.touchEnd(element);

    expect(onSwipeLeft).toHaveBeenCalledTimes(1);
  });

  it("should detect right swipe", () => {
    const onSwipeRight = jest.fn();
    const { container } = render(
      <SwipeableContainer onSwipeRight={onSwipeRight}>
        <div>Content</div>
      </SwipeableContainer>,
    );

    const element = container.firstChild as HTMLElement;

    // Simulate swipe right
    fireEvent.touchStart(element, {
      targetTouches: [{ clientX: 100 }],
    });
    fireEvent.touchMove(element, {
      targetTouches: [{ clientX: 200 }],
    });
    fireEvent.touchEnd(element);

    expect(onSwipeRight).toHaveBeenCalledTimes(1);
  });

  it("should not trigger swipe for small movements", () => {
    const onSwipeLeft = jest.fn();
    const onSwipeRight = jest.fn();
    const { container } = render(
      <SwipeableContainer onSwipeLeft={onSwipeLeft} onSwipeRight={onSwipeRight}>
        <div>Content</div>
      </SwipeableContainer>,
    );

    const element = container.firstChild as HTMLElement;

    // Simulate small movement (less than 50px)
    fireEvent.touchStart(element, {
      targetTouches: [{ clientX: 100 }],
    });
    fireEvent.touchMove(element, {
      targetTouches: [{ clientX: 120 }],
    });
    fireEvent.touchEnd(element);

    expect(onSwipeLeft).not.toHaveBeenCalled();
    expect(onSwipeRight).not.toHaveBeenCalled();
  });

  it("should not trigger callbacks if not provided", () => {
    const { container } = render(
      <SwipeableContainer>
        <div>Content</div>
      </SwipeableContainer>,
    );

    const element = container.firstChild as HTMLElement;

    // Simulate swipe without callbacks - should not throw
    expect(() => {
      fireEvent.touchStart(element, {
        targetTouches: [{ clientX: 200 }],
      });
      fireEvent.touchMove(element, {
        targetTouches: [{ clientX: 100 }],
      });
      fireEvent.touchEnd(element);
    }).not.toThrow();
  });

  it("should merge custom className", () => {
    const { container } = render(
      <SwipeableContainer className="custom-class">
        <div>Content</div>
      </SwipeableContainer>,
    );

    const element = container.firstChild as HTMLElement;
    expect(element).toHaveClass("custom-class");
  });
});
