import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import apiService from '../services/apiService';

export default function DashboardScreen({ navigation }) {
  const [expenses, setExpenses] = useState([]);
  const [insights, setInsights] = useState(null);
  const [apiHealth, setApiHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load all data in parallel
      const [expensesData, insightsData, healthData] = await Promise.all([
        apiService.getExpenses(),
        apiService.getInsights(),
        apiService.getHealth(),
      ]);

      setExpenses(expensesData.expenses || []);
      setInsights(insightsData.insights || {});
      setApiHealth(healthData);
      
    } catch (error) {
      console.error('Dashboard load error:', error);
      Alert.alert(
        'Connection Error',
        'Unable to load data from server. Please check your internet connection.',
        [{ text: 'Retry', onPress: loadDashboardData }]
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  const formatCurrency = (amount) => {
    return `$${Number(amount).toFixed(2)}`;
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4A90E2" />
        <Text style={styles.loadingText}>Loading your budget data...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>💰 AI Budget Tracker</Text>
        <Text style={styles.subtitle}>Smart expense management</Text>
        {apiHealth && (
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>🚀 Live on Railway</Text>
          </View>
        )}
      </View>

      {/* Summary Cards */}
      <View style={styles.summaryContainer}>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Total Expenses</Text>
          <Text style={styles.summaryAmount}>
            {formatCurrency(expenses.reduce((sum, exp) => sum + exp.amount, 0))}
          </Text>
          <Text style={styles.summarySubtext}>{expenses.length} transactions</Text>
        </View>

        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>AI Insights</Text>
          <Text style={styles.summaryAmount}>
            {insights?.top_category || 'Analyzing...'}
          </Text>
          <Text style={styles.summarySubtext}>Top spending category</Text>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('AddExpense')}
        >
          <Text style={styles.actionButtonText}>➕ Add Expense</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('Insights')}
        >
          <Text style={styles.actionButtonText}>🤖 AI Insights</Text>
        </TouchableOpacity>
      </View>

      {/* Recent Expenses */}
      <View style={styles.expensesContainer}>
        <Text style={styles.sectionTitle}>Recent Expenses</Text>
        {expenses.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No expenses yet</Text>
            <Text style={styles.emptyStateSubtext}>
              Add your first expense to get started!
            </Text>
          </View>
        ) : (
          expenses.map((expense, index) => (
            <View key={expense.id || index} style={styles.expenseItem}>
              <View style={styles.expenseInfo}>
                <Text style={styles.expenseDescription}>
                  {expense.description}
                </Text>
                <Text style={styles.expenseCategory}>
                  {expense.category}
                </Text>
              </View>
              <Text style={styles.expenseAmount}>
                {formatCurrency(expense.amount)}
              </Text>
            </View>
          ))
        )}
      </View>

      {/* AI Insights Preview */}
      {insights && (
        <View style={styles.insightsContainer}>
          <Text style={styles.sectionTitle}>🤖 AI Insights</Text>
          <View style={styles.insightCard}>
            <Text style={styles.insightText}>{insights.advice}</Text>
            {insights.tips && insights.tips.length > 0 && (
              <View style={styles.tipsContainer}>
                {insights.tips.map((tip, index) => (
                  <Text key={index} style={styles.tipText}>• {tip}</Text>
                ))}
              </View>
            )}
          </View>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6C757D',
  },
  header: {
    backgroundColor: '#4A90E2',
    padding: 24,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 12,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  summaryContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  summaryCard: {
    flex: 1,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  summaryTitle: {
    fontSize: 14,
    color: '#6C757D',
    marginBottom: 8,
  },
  summaryAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2D3748',
    marginBottom: 4,
  },
  summarySubtext: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  actionsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#4A90E2',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  expensesContainer: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2D3748',
    marginBottom: 16,
  },
  emptyState: {
    alignItems: 'center',
    padding: 32,
  },
  emptyStateText: {
    fontSize: 18,
    color: '#6C757D',
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    textAlign: 'center',
  },
  expenseItem: {
    flexDirection: 'row',
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  expenseInfo: {
    flex: 1,
  },
  expenseDescription: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2D3748',
    marginBottom: 4,
  },
  expenseCategory: {
    fontSize: 14,
    color: '#6C757D',
  },
  expenseAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4A90E2',
  },
  insightsContainer: {
    padding: 16,
  },
  insightCard: {
    backgroundColor: '#E8F4FD',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#4A90E2',
  },
  insightText: {
    fontSize: 16,
    color: '#2D3748',
    marginBottom: 12,
  },
  tipsContainer: {
    marginTop: 8,
  },
  tipText: {
    fontSize: 14,
    color: '#6C757D',
    marginBottom: 4,
  },
});
