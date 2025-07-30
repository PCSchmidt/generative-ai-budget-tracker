/**
 * Modern Card Component for AI Budget Tracker
 * Professional card container with shadows and responsive design
 */

import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { colors, spacing, borderRadius, shadows } from '../../theme';

const Card = ({
  children,
  style,
  onPress,
  variant = 'default', // default, elevated, outlined
  padding = 'medium', // none, small, medium, large
  ...props
}) => {
  const cardStyles = [
    styles.base,
    styles[variant],
    styles[`padding_${padding}`],
    style,
  ];

  if (onPress) {
    return (
      <TouchableOpacity
        style={cardStyles}
        onPress={onPress}
        activeOpacity={0.95}
        {...props}
      >
        {children}
      </TouchableOpacity>
    );
  }

  return (
    <View style={cardStyles} {...props}>
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  base: {
    borderRadius: borderRadius.xl,
    backgroundColor: colors.white,
  },

  // Variants
  default: {
    ...shadows.md,
  },
  elevated: {
    ...shadows.lg,
  },
  outlined: {
    borderWidth: 1,
    borderColor: colors.border.light,
    ...shadows.sm,
  },

  // Padding variants
  padding_none: {
    padding: 0,
  },
  padding_small: {
    padding: spacing[3],
  },
  padding_medium: {
    padding: spacing[4],
  },
  padding_large: {
    padding: spacing[6],
  },
});

export default Card;
