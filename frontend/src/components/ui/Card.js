/**
 * Modern Card Component for AI Budget Tracker
 * Professional card container with shadows and responsive design
 */

import React from 'react';

const Card = ({
  children,
  style,
  onClick,
  variant = 'default', // default, elevated, outlined
  padding = 'medium', // none, small, medium, large
  className,
  ...props
}) => {
  const baseStyles = {
    backgroundColor: 'white',
    borderRadius: 'var(--border-radius-lg)',
    transition: 'all 0.2s ease',
    position: 'relative',
    overflow: 'hidden',
  };

  const variantStyles = {
    default: {
      border: '1px solid var(--gray-200)',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    },
    elevated: {
      border: 'none',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    },
    outlined: {
      border: '2px solid var(--gray-200)',
      boxShadow: 'none',
    },
  };

  const paddingStyles = {
    none: { padding: 0 },
    small: { padding: 'var(--spacing-md)' },
    medium: { padding: 'var(--spacing-lg)' },
    large: { padding: 'var(--spacing-xl)' },
  };

  const hoverStyles = onClick ? {
    cursor: 'pointer',
    transform: 'translateY(-1px)',
    boxShadow: variant === 'elevated' 
      ? '0 8px 20px rgba(0, 0, 0, 0.2)' 
      : '0 4px 12px rgba(0, 0, 0, 0.15)',
  } : {};

  const cardStyles = {
    ...baseStyles,
    ...variantStyles[variant],
    ...paddingStyles[padding],
    ...style,
  };

  const [isHovered, setIsHovered] = React.useState(false);

  if (onClick) {
    return (
      <div
        style={isHovered ? { ...cardStyles, ...hoverStyles } : cardStyles}
        onClick={onClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={className}
        {...props}
      >
        {children}
      </div>
    );
  }

  return (
    <div
      style={cardStyles}
      className={className}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
