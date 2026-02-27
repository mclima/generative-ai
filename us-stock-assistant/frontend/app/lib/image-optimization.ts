/**
 * Image optimization utilities for Next.js Image component
 */

// Responsive image sizes for different breakpoints
export const IMAGE_SIZES = {
  thumbnail: 64,
  small: 128,
  medium: 256,
  large: 512,
  xlarge: 1024,
};

// Device sizes for responsive images
export const DEVICE_SIZES = [640, 750, 828, 1080, 1200, 1920];

/**
 * Generate srcset for responsive images
 */
export function generateSrcSet(src: string, sizes: number[]): string {
  return sizes.map((size) => `${src}?w=${size} ${size}w`).join(", ");
}

/**
 * Get optimized image props for Next.js Image component
 */
export function getOptimizedImageProps(src: string, alt: string, size: keyof typeof IMAGE_SIZES = "medium") {
  return {
    src,
    alt,
    width: IMAGE_SIZES[size],
    height: IMAGE_SIZES[size],
    loading: "lazy" as const,
    quality: 75, // Good balance between quality and file size
  };
}

/**
 * Preload critical images
 */
export function preloadImage(src: string, as: "image" = "image") {
  if (typeof window !== "undefined") {
    const link = document.createElement("link");
    link.rel = "preload";
    link.as = as;
    link.href = src;
    document.head.appendChild(link);
  }
}
