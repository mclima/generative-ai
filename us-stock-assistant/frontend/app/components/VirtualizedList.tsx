"use client";

import { FixedSizeList as List } from "react-window";
import { useEffect, useState } from "react";

interface VirtualizedListProps<T> {
  items: T[];
  itemHeight: number;
  height: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  className?: string;
}

/**
 * Virtualized list component for rendering large lists efficiently
 * Only renders visible items + buffer, improving performance for large datasets
 */
export default function VirtualizedList<T>({ items, itemHeight, height, renderItem, className = "" }: VirtualizedListProps<T>) {
  const [listWidth, setListWidth] = useState(0);

  useEffect(() => {
    // Get container width for responsive sizing
    const updateWidth = () => {
      const container = document.getElementById("virtualized-list-container");
      if (container) {
        setListWidth(container.offsetWidth);
      }
    };

    updateWidth();
    window.addEventListener("resize", updateWidth);
    return () => window.removeEventListener("resize", updateWidth);
  }, []);

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => <div style={style}>{renderItem(items[index], index)}</div>;

  return (
    <div id="virtualized-list-container" className={className}>
      {listWidth > 0 && (
        <List
          height={height}
          itemCount={items.length}
          itemSize={itemHeight}
          width={listWidth}
          overscanCount={5} // Render 5 extra items above/below viewport
        >
          {Row}
        </List>
      )}
    </div>
  );
}
