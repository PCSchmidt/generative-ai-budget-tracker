/**
 * Navigation setup for AI Budget Tracker
 * Handles authentication flow and main app navigation
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text, View, StyleSheet } from 'react-native';

import { useAuth } from '../contexts/AuthContext';
import { colors, typography } from '../theme';

// Screens
import LoginScreen from '../screens/auth/LoginScreen';
import SignupScreen from '../screens/auth/SignupScreen';
import DashboardScreen from '../screens/main/DashboardScreen';
import LoadingScreen from '../screens/LoadingScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Placeholder screens for main tabs
const ExpensesScreen = () => (
  <View style={placeholderStyles.container}>
    <Text style={placeholderStyles.title}>Expenses</Text>
    <Text style={placeholderStyles.subtitle}>Track and manage your expenses</Text>
    <Text style={placeholderStyles.status}>🚧 Coming Soon</Text>
  </View>
);

const InsightsScreen = () => (
  <View style={placeholderStyles.container}>
    <Text style={placeholderStyles.title}>AI Insights</Text>
    <Text style={placeholderStyles.subtitle}>Smart financial analysis</Text>
    <Text style={placeholderStyles.status}>🤖 Coming Soon</Text>
  </View>
);

const SettingsScreen = () => (
  <View style={placeholderStyles.container}>
    <Text style={placeholderStyles.title}>Settings</Text>
    <Text style={placeholderStyles.subtitle}>Manage your account and preferences</Text>
    <Text style={placeholderStyles.status}>⚙️ Coming Soon</Text>
  </View>
);

// Auth Stack Navigator
const AuthStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerShown: false,
      cardStyle: { backgroundColor: colors.background.secondary },
    }}
  >
    <Stack.Screen name="Login" component={LoginScreen} />
    <Stack.Screen name="Signup" component={SignupScreen} />
  </Stack.Navigator>
);

// Main Tab Navigator
const MainTabs = () => (
  <Tab.Navigator
    screenOptions={{
      headerShown: false,
      tabBarActiveTintColor: colors.accent[600],
      tabBarInactiveTintColor: colors.text.secondary,
      tabBarStyle: {
        backgroundColor: colors.white,
        borderTopColor: colors.border.light,
        borderTopWidth: 1,
        paddingTop: 8,
        paddingBottom: 8,
        height: 60,
      },
      tabBarLabelStyle: {
        fontSize: 12,
        fontWeight: typography.fontWeight.medium,
        marginTop: 4,
      },
    }}
  >
    <Tab.Screen
      name="Dashboard"
      component={DashboardScreen}
      options={{
        tabBarIcon: ({ color }) => (
          <Text style={[tabIconStyles.icon, { color }]}>📊</Text>
        ),
      }}
    />
    <Tab.Screen
      name="Expenses"
      component={ExpensesScreen}
      options={{
        tabBarIcon: ({ color }) => (
          <Text style={[tabIconStyles.icon, { color }]}>💳</Text>
        ),
      }}
    />
    <Tab.Screen
      name="Insights"
      component={InsightsScreen}
      options={{
        tabBarIcon: ({ color }) => (
          <Text style={[tabIconStyles.icon, { color }]}>🤖</Text>
        ),
      }}
    />
    <Tab.Screen
      name="Settings"
      component={SettingsScreen}
      options={{
        tabBarIcon: ({ color }) => (
          <Text style={[tabIconStyles.icon, { color }]}>⚙️</Text>
        ),
      }}
    />
  </Tab.Navigator>
);

// Main App Navigator
const AppNavigator = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainTabs /> : <AuthStack />}
    </NavigationContainer>
  );
};

const placeholderStyles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background.secondary,
    padding: 20,
  },
  title: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.text.primary,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    color: colors.text.secondary,
    textAlign: 'center',
    marginBottom: 16,
  },
  status: {
    fontSize: typography.fontSize.lg,
    color: colors.accent[600],
    fontWeight: typography.fontWeight.semibold,
  },
});

const tabIconStyles = StyleSheet.create({
  icon: {
    fontSize: 24,
  },
});

export default AppNavigator;
