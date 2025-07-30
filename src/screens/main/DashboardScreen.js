/**
 * Dashboard Screen for AI Budget Tracker
 * Main overview screen with financial summary and insights
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../../contexts/AuthContext';
import { colors, typography, spacing, layout } from '../../theme';
import Button from '../ui/Button';
import Card from '../ui/Card';

const DashboardScreen = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [refreshing, setRefreshing] = useState(false);
  const [dashboardData, setDashboardData] = useState({
    totalBalance: 2547.83,
    monthlyIncome: 4200.00,
    monthlyExpenses: 1652.17,
    savingsRate: 60.6,
    recentExpenses: [
      { id: 1, description: 'Grocery Store', amount: -87.45, category: 'Food', date: '2025-07-29' },
      { id: 2, description: 'Gas Station', amount: -45.20, category: 'Transportation', date: '2025-07-28' },
      { id: 3, description: 'Coffee Shop', amount: -12.50, category: 'Food', date: '2025-07-28' },
    ],
    insights: [
      "You're spending 25% less on dining out this month! 🎉",
      "Consider setting aside $200 more for your emergency fund.",
      "Your transportation costs are 15% higher than usual.",
    ],
  });

  const onRefresh = async () => {
    setRefreshing(true);
    // TODO: Fetch real data from API
    setTimeout(() => {
      setRefreshing(false);
    }, 1000);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>
              {getGreeting()}, {user?.first_name || user?.username}! 👋
            </Text>
            <Text style={styles.subtitle}>Here's your financial overview</Text>
          </View>
          <Button
            title="Logout"
            variant="ghost"
            size="small"
            onPress={logout}
            style={styles.logoutButton}
          />
        </View>

        {/* Balance Card */}
        <Card style={styles.balanceCard} padding="large">
          <Text style={styles.balanceLabel}>Total Balance</Text>
          <Text style={styles.balanceAmount}>
            {formatCurrency(dashboardData.totalBalance)}
          </Text>
          <View style={styles.balanceDetails}>
            <View style={styles.balanceItem}>
              <Text style={styles.balanceItemLabel}>Income</Text>
              <Text style={[styles.balanceItemValue, styles.incomeText]}>
                +{formatCurrency(dashboardData.monthlyIncome)}
              </Text>
            </View>
            <View style={styles.balanceItem}>
              <Text style={styles.balanceItemLabel}>Expenses</Text>
              <Text style={[styles.balanceItemValue, styles.expenseText]}>
                -{formatCurrency(dashboardData.monthlyExpenses)}
              </Text>
            </View>
            <View style={styles.balanceItem}>
              <Text style={styles.balanceItemLabel}>Savings Rate</Text>
              <Text style={[styles.balanceItemValue, styles.savingsText]}>
                {dashboardData.savingsRate}%
              </Text>
            </View>
          </View>
        </Card>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionButtons}>
            <Button
              title="Add Expense"
              variant="primary"
              style={styles.actionButton}
              onPress={() => {
                // TODO: Navigate to add expense
                alert('Add Expense feature coming soon!');
              }}
            />
            <Button
              title="View Analytics"
              variant="secondary"
              style={styles.actionButton}
              onPress={() => {
                // TODO: Navigate to analytics
                alert('Analytics feature coming soon!');
              }}
            />
          </View>
        </View>

        {/* Recent Expenses */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Expenses</Text>
          {dashboardData.recentExpenses.map((expense) => (
            <Card key={expense.id} style={styles.expenseCard} padding="medium">
              <View style={styles.expenseItem}>
                <View style={styles.expenseInfo}>
                  <Text style={styles.expenseDescription}>
                    {expense.description}
                  </Text>
                  <Text style={styles.expenseCategory}>
                    {expense.category} • {expense.date}
                  </Text>
                </View>
                <Text style={[styles.expenseAmount, styles.expenseText]}>
                  {formatCurrency(expense.amount)}
                </Text>
              </View>
            </Card>
          ))}
          <Button
            title="View All Expenses"
            variant="outline"
            onPress={() => {
              // TODO: Navigate to expenses list
              alert('Expenses list coming soon!');
            }}
            style={styles.viewAllButton}
          />
        </View>

        {/* AI Insights */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>AI Insights 🤖</Text>
          {dashboardData.insights.map((insight, index) => (
            <Card key={index} style={styles.insightCard} padding="medium">
              <Text style={styles.insightText}>{insight}</Text>
            </Card>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background.secondary,
  },

  scrollContent: {
    flexGrow: 1,
    padding: layout.screenPadding,
  },

  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing[6],
  },

  greeting: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.text.primary,
  },

  subtitle: {
    fontSize: typography.fontSize.base,
    color: colors.text.secondary,
    marginTop: spacing[1],
  },

  logoutButton: {
    marginTop: -spacing[2],
  },

  balanceCard: {
    marginBottom: spacing[6],
    backgroundColor: colors.accent[600],
  },

  balanceLabel: {
    fontSize: typography.fontSize.base,
    color: colors.white,
    opacity: 0.9,
    marginBottom: spacing[1],
  },

  balanceAmount: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: typography.fontWeight.bold,
    color: colors.white,
    marginBottom: spacing[4],
  },

  balanceDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },

  balanceItem: {
    flex: 1,
    alignItems: 'center',
  },

  balanceItemLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.white,
    opacity: 0.8,
    marginBottom: spacing[1],
  },

  balanceItemValue: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold,
    color: colors.white,
  },

  incomeText: {
    color: colors.success[300],
  },

  expenseText: {
    color: colors.error[400],
  },

  savingsText: {
    color: colors.white,
  },

  quickActions: {
    marginBottom: spacing[6],
  },

  sectionTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.semibold,
    color: colors.text.primary,
    marginBottom: spacing[4],
  },

  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing[3],
  },

  actionButton: {
    flex: 1,
  },

  section: {
    marginBottom: spacing[6],
  },

  expenseCard: {
    marginBottom: spacing[2],
  },

  expenseItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  expenseInfo: {
    flex: 1,
  },

  expenseDescription: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium,
    color: colors.text.primary,
    marginBottom: spacing[1],
  },

  expenseCategory: {
    fontSize: typography.fontSize.sm,
    color: colors.text.secondary,
  },

  expenseAmount: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semibold,
  },

  viewAllButton: {
    marginTop: spacing[2],
  },

  insightCard: {
    marginBottom: spacing[2],
    backgroundColor: colors.accent[50],
    borderLeftWidth: 4,
    borderLeftColor: colors.accent[600],
  },

  insightText: {
    fontSize: typography.fontSize.base,
    color: colors.text.primary,
    lineHeight: typography.fontSize.base * typography.lineHeight.relaxed,
  },
});

export default DashboardScreen;
