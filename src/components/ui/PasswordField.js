import React, { useState, useId } from 'react';
import styled from 'styled-components';
import { theme } from '../../theme';

/**
 * Accessible reusable PasswordField component
 * Features:
 * - Internal show/hide toggle with aria-pressed & dynamic aria-label
 * - Helper text + error message support (with aria-describedby)
 * - Light / Dark variants for seamless use across auth screens
 * - Focus ring & keyboard accessibility
 */

const FieldWrapper = styled.div`
  width: 100%;
`;

const LabelRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 6px;
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: ${props => props.$variant === 'dark' ? theme.colors.primary[200] : theme.colors.primary[700]};
`;

const InputWrapper = styled.div`
  position: relative;
`;

const BaseInput = styled.input`
  width: 100%;
  padding: 12px 52px 12px 16px;
  border: 2px solid ${props => props.$variant === 'dark' ? '#374151' : theme.colors.border.light};
  border-radius: ${theme.borderRadius.lg};
  font-size: 16px;
  background: ${props => props.$variant === 'dark' ? 'rgba(15, 23, 42, 0.5)' : theme.colors.white};
  color: ${props => props.$variant === 'dark' ? theme.colors.primary[50] : theme.colors.text.primary};
  transition: all .2s ease;
  outline: none;

  &::placeholder { color: ${props => props.$variant === 'dark' ? theme.colors.primary[400] : theme.colors.primary[400]}; }

  &:focus {
    border-color: ${theme.colors.accent[600]};
    box-shadow: 0 0 0 3px ${theme.colors.accent.opacity[100]};
    background: ${props => props.$variant === 'dark' ? 'rgba(15,23,42,0.75)' : theme.colors.white};
  }

  ${props => props.$error && `
    border-color: ${theme.colors.error[600]};
    &:focus { box-shadow: 0 0 0 3px ${theme.colors.error.opacity[100]}; }
  `}
`;

const ToggleButton = styled.button`
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .05em;
  cursor: pointer;
  border: 1px solid ${theme.colors.accent[600]};
  background: ${props => props.$variant === 'dark' ? 'rgba(59,130,246,0.18)' : theme.colors.accent[100]};
  color: ${theme.colors.accent[600]};
  transition: all .15s ease;

  &:hover { background: ${props => props.$variant === 'dark' ? 'rgba(59,130,246,0.28)' : theme.colors.accent[200]}; }
  &:focus { outline: none; box-shadow: 0 0 0 3px ${theme.colors.accent.opacity[100]}; }
  &:active { transform: translateY(calc(-50% + 1px)); }
`;

const HelperText = styled.div`
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.4;
  color: ${props => props.$error ? theme.colors.error[600] : (props.$variant === 'dark' ? theme.colors.primary[400] : theme.colors.primary[600])};
`;

export const PasswordField = ({
  id,
  name,
  label = 'Password',
  value,
  onChange,
  placeholder = 'Enter your password',
  required = false,
  autoComplete = 'current-password',
  helperText,
  error,
  variant = 'light', // 'light' | 'dark'
  confirm = false,
  ...rest
}) => {
  const [show, setShow] = useState(false);
  const internalId = useId();
  const fieldId = id || `pwd-${internalId}`;
  const describedById = helperText || error ? `${fieldId}-desc` : undefined;

  return (
    <FieldWrapper>
      <LabelRow>
        <Label htmlFor={fieldId} $variant={variant}>{label}{required && ' *'}</Label>
      </LabelRow>
      <InputWrapper>
        <BaseInput
          id={fieldId}
          name={name}
          type={show ? 'text' : 'password'}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          autoComplete={autoComplete}
            aria-invalid={!!error}
            aria-describedby={describedById}
          $variant={variant}
          $error={!!error}
          {...rest}
        />
        <ToggleButton
          type="button"
          onClick={() => setShow(s => !s)}
          aria-pressed={show}
          aria-label={`${show ? 'Hide' : 'Show'} ${confirm ? 'confirmation ' : ''}password`}
          $variant={variant}
        >
          {show ? 'HIDE' : 'SHOW'}
        </ToggleButton>
      </InputWrapper>
      {(helperText || error) && (
        <HelperText id={describedById} $error={!!error} $variant={variant}>
          {error || helperText}
        </HelperText>
      )}
    </FieldWrapper>
  );
};

export default PasswordField;
