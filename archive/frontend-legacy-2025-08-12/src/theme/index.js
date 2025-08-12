/**
 * Modern Fintech Design System for AI Budget Tracker
 * Professional color palette, typography, and spacing tokens
 */

export const colors = {
  // Primary Brand Colors - Professional Dark Theme
  primary: {
    900: '#0f172a', // Dark slate - headers, primary text
    800: '#1e293b', // Medium slate - navigation, cards
    700: '#334155', // Light slate - secondary text
    600: '#475569', // Border colors
    500: '#64748b', // Disabled text
    400: '#94a3b8', // Placeholder text
    300: '#cbd5e1', // Light borders
    200: '#e2e8f0', // Background accents
    100: '#f1f5f9', // Light backgrounds
    50: '#f8fafc',  // Very light backgrounds
  },

  // Accent Colors - Professional Blue
  accent: {
    700: '#1d4ed8', // Darker blue for hovers
    600: '#2563eb', // Primary CTA buttons
    500: '#3b82f6', // Links and interactive elements
    400: '#60a5fa', // Hover states
    300: '#93c5fd', // Light accents
    200: '#dbeafe', // Background highlights
    100: '#eff6ff', // Very light accents
    opacity: {
      100: 'rgba(37, 99, 235, 0.1)', // 10% opacity for focus rings
    },
  },

  // Financial Status Colors
  success: {
    700: '#047857', // Darker green for hovers
    600: '#059669', // Positive amounts, success states
    500: '#10b981', // Success indicators
    400: '#34d399', // Light success
    100: '#d1fae5', // Success backgrounds
    opacity: {
      100: 'rgba(5, 150, 105, 0.1)', // 10% opacity for focus rings
    },
  },

  error: {
    700: '#b91c1c', // Darker red for hovers
    600: '#dc2626', // Negative amounts, errors
    500: '#ef4444', // Error indicators
    400: '#f87171', // Light errors
    100: '#fee2e2', // Error backgrounds
    opacity: {
      100: 'rgba(220, 38, 38, 0.1)', // 10% opacity for focus rings
    },
  },

  warning: {
    600: '#d97706', // Warnings, alerts
    500: '#f59e0b', // Warning indicators
    400: '#fbbf24', // Light warnings
    100: '#fef3c7', // Warning backgrounds
  },

  // Neutral Colors
  white: '#ffffff',
  black: '#000000',
  transparent: 'transparent',
  
  // Semantic Colors
  background: {
    primary: '#ffffff',
    secondary: '#f8fafc',
    dark: '#0f172a',
  },
  
  text: {
    primary: '#0f172a',
    secondary: '#475569',
    tertiary: '#64748b',
    inverse: '#ffffff',
  },

  border: {
    light: '#e2e8f0',
    medium: '#cbd5e1',
    dark: '#94a3b8',
  }
};

export const typography = {
  // Font Families - Web optimized
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',

  // Font Sizes (in pixels for web)
  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
    '4xl': '36px',
    '5xl': '48px',
  },

  // Line Heights
  lineHeight: {
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },

  // Font Weights
  fontWeight: {
    regular: '400',
    medium: '500',
    semiBold: '600',
    bold: '700',
  },
};

export const spacing = {
  // Base spacing unit: 4px (now with px units for web)
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
  '3xl': '64px',
  '4xl': '96px',
};

export const borderRadius = {
  none: '0px',
  sm: '6px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  '2xl': '24px',
  full: '9999px',
};

export const shadows = {
  // Modern, subtle shadows for web (CSS box-shadow format)
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
};

// Component-specific styles
export const components = {
  // Button styles
  button: {
    primary: {
      backgroundColor: colors.accent[600],
      paddingVertical: spacing[3],
      paddingHorizontal: spacing[6],
      borderRadius: borderRadius.lg,
      minHeight: 48,
    },
    secondary: {
      backgroundColor: colors.primary[100],
      borderWidth: 1,
      borderColor: colors.border.light,
      paddingVertical: spacing[3],
      paddingHorizontal: spacing[6],
      borderRadius: borderRadius.lg,
      minHeight: 48,
    },
  },

  // Card styles
  card: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.xl,
    padding: spacing[4],
    ...shadows.md,
  },

  // Input styles
  input: {
    backgroundColor: colors.background.secondary,
    borderWidth: 1,
    borderColor: colors.border.light,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    fontSize: typography.fontSize.base,
    minHeight: 48,
  },
};

// Layout constants
export const layout = {
  screenPadding: spacing[4],
  sectionSpacing: spacing[6],
  componentSpacing: spacing[4],
};

// Main theme object for web components
export const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  components,
  layout,
};

export default theme;
