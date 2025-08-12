import React from 'react';
import styled from 'styled-components';
import { theme } from '../../theme';

/**
 * Professional Button Component for Web
 * Fintech-styled button with multiple variants and states
 */

const StyledButton = styled.button`
  /* Base styles */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.size === 'large' ? '16px 24px' : props.size === 'small' ? '8px 16px' : '12px 20px'};
  border-radius: ${theme.borderRadius.md};
  font-family: ${theme.typography.fontFamily};
  font-size: ${props => props.size === 'large' ? '16px' : props.size === 'small' ? '14px' : '15px'};
  font-weight: ${theme.typography.fontWeight.semiBold};
  letter-spacing: -0.01em;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  position: relative;
  overflow: hidden;
  min-height: ${props => props.size === 'large' ? '48px' : props.size === 'small' ? '36px' : '42px'};
  width: ${props => props.fullWidth ? '100%' : 'auto'};

  /* Focus styles */
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px ${theme.colors.accent.opacity[100]};
  }

  /* Disabled state */
  &:disabled {
    cursor: not-allowed;
    opacity: 0.5;
    transform: none !important;
  }

  /* Hover animation */
  &:not(:disabled):hover {
    transform: translateY(-1px);
    box-shadow: ${theme.shadows.md};
  }

  /* Active state */
  &:not(:disabled):active {
    transform: translateY(0);
  }

  /* Loading state */
  ${props => props.loading && `
    color: transparent !important;
    pointer-events: none;
  `}

  /* Primary variant */
  ${props => props.variant === 'primary' && `
    background: linear-gradient(135deg, ${theme.colors.accent[600]}, ${theme.colors.accent[500]});
    color: white;
    
    &:not(:disabled):hover {
      background: linear-gradient(135deg, ${theme.colors.accent[700]}, ${theme.colors.accent[600]});
    }
  `}

  /* Secondary variant */
  ${props => props.variant === 'secondary' && `
    background: ${theme.colors.gray[100]};
    color: ${theme.colors.primary[700]};
    border: 1px solid ${theme.colors.gray[200]};
    
    &:not(:disabled):hover {
      background: ${theme.colors.gray[50]};
      border-color: ${theme.colors.accent[300]};
      color: ${theme.colors.accent[600]};
    }
  `}

  /* Outline variant */
  ${props => props.variant === 'outline' && `
    background: transparent;
    color: ${theme.colors.accent[600]};
    border: 2px solid ${theme.colors.accent[600]};
    
    &:not(:disabled):hover {
      background: ${theme.colors.accent[600]};
      color: white;
    }
  `}

  /* Ghost variant */
  ${props => props.variant === 'ghost' && `
    background: transparent;
    color: ${theme.colors.primary[700]};
    
    &:not(:disabled):hover {
      background: ${theme.colors.gray[100]};
      color: ${theme.colors.accent[600]};
    }
  `}

  /* Danger variant */
  ${props => props.variant === 'danger' && `
    background: ${theme.colors.error[600]};
    color: white;
    
    &:not(:disabled):hover {
      background: ${theme.colors.error[700]};
    }
  `}

  /* Success variant */
  ${props => props.variant === 'success' && `
    background: ${theme.colors.success[600]};
    color: white;
    
    &:not(:disabled):hover {
      background: ${theme.colors.success[700]};
    }
  `}
`;

const LoadingSpinner = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
  }
`;

const ButtonText = styled.span`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

export const Button = ({
  children,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  loading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  onClick,
  type = 'button',
  className,
  style,
  ...props
}) => {
  return (
    <StyledButton
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      loading={loading}
      disabled={disabled || loading}
      onClick={onClick}
      type={type}
      className={className}
      style={style}
      {...props}
    >
      {loading && <LoadingSpinner />}
      <ButtonText style={{ opacity: loading ? 0 : 1 }}>
        {leftIcon && <span>{leftIcon}</span>}
        {children}
        {rightIcon && <span>{rightIcon}</span>}
      </ButtonText>
    </StyledButton>
  );
};

export default Button;
