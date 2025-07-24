import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import apiService from '../services/apiService';

export default function InsightsScreen({ navigation }) {
  const [insights, setInsights] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      setLoading(true);
      
      const [insightsData, expensesData] = await Promise.all([
        apiService.getInsights(),
        apiService.getExpenses(),
      ]);

      setInsights(insightsData.insights || {});
      setExpenses(expensesData.expenses || []);
      
    } catch (error) {
      console.error('Insights load error:', error);
      Alert.alert(
        'Connection Error',
        'Unable to load insights. Please check your internet connection.',
        [{ text: 'Retry', onPress: loadInsights }]
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadInsights();
  };

  const formatCurrency = (amount) => {
    return `$${Number(amount).toFixed(2)}`;
  };

  const getSpendingBreakdown = () => {
    if (!insights?.spending_breakdown) return [];
    
    return Object.entries(insights.spending_breakdown).map(([category, amount]) => ({
      category,
      amount,
      percentage: insights.total_spent > 0 ? (amount / insights.total_spent) * 100 : 0,
    })).sort((a, b) => b.amount - a.amount);
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4A90E2" />
        <Text style={styles.loadingText}>Analyzing your spending patterns...</Text>
      </View>
    );
  }

  const spendingBreakdown = getSpendingBreakdown();

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>🤖 AI Insights</Text>
        <Text style={styles.subtitle}>Smart analysis of your spending habits</Text>
      </View>

      {/* Main Insight Card */}
      {insights && (
        <View style={styles.insightCard}>
          <Text style={styles.insightTitle}>💡 Financial Advice</Text>
          <Text style={styles.insightText}>
            {insights.advice || "Start tracking expenses to get personalized insights!"}
          </Text>
          
          {insights.ai_used ? (
            <View style={styles.aiBadge}>
              <Text style={styles.aiBadgeText}>✨ Powered by AI</Text>
            </View>
          ) : (
            <View style={styles.aiBadge}>
              <Text style={styles.aiBadgeText}>🔬 Smart Analysis</Text>
            </View>
          )}
        </View>
      )}

      {/* Summary Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {formatCurrency(insights?.total_spent || 0)}
          </Text>
          <Text style={styles.statLabel}>Total Tracked</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {expenses.length}
          </Text>
          <Text style={styles.statLabel}>Transactions</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {spendingBreakdown.length}
          </Text>
          <Text style={styles.statLabel}>Categories</Text>
        </View>
      </View>

      {/* Spending Breakdown */}
      {spendingBreakdown.length > 0 && (
        <View style={styles.breakdownContainer}>
          <Text style={styles.sectionTitle}>📊 Spending Breakdown</Text>
          {spendingBreakdown.map((item, index) => (
            <View key={item.category} style={styles.breakdownItem}>
              <View style={styles.breakdownInfo}>
                <Text style={styles.breakdownCategory}>{item.category}</Text>
                <Text style={styles.breakdownAmount}>
                  {formatCurrency(item.amount)}
                </Text>
              </View>
              <View style={styles.breakdownBar}>
                <View 
                  style={[
                    styles.breakdownBarFill,
                    { width: `${item.percentage}%` }
                  ]} 
                />
              </View>
              <Text style={styles.breakdownPercentage}>
                {item.percentage.toFixed(1)}%
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* AI Tips */}
      {insights?.tips && insights.tips.length > 0 && (
        <View style={styles.tipsContainer}>
          <Text style={styles.sectionTitle}>💡 Smart Tips</Text>
          {insights.tips.map((tip, index) => (
            <View key={index} style={styles.tipItem}>
              <Text style={styles.tipIcon}>✨</Text>
              <Text style={styles.tipText}>{tip}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('AddExpense')}
        >
          <Text style={styles.actionButtonText}>➕ Add Expense</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.secondaryButton]}
          onPress={onRefresh}
        >
          <Text style={[styles.actionButtonText, styles.secondaryButtonText]}>
            🔄 Refresh Analysis
          </Text>
        </TouchableOpacity>
      </View>

      {/* Empty State */}
      {expenses.length === 0 && (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateIcon}>📈</Text>
          <Text style={styles.emptyStateTitle}>No Data Yet</Text>
          <Text style={styles.emptyStateText}>
            Start adding expenses to see AI-powered insights about your spending patterns!
          </Text>
          <TouchableOpacity
            style={styles.emptyStateButton}
            onPress={() => navigation.navigate('AddExpense')}
          >
            <Text style={styles.emptyStateButtonText}>Add First Expense</Text>
          </TouchableOpacity>
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
  backButton: {
    marginBottom: 16,
  },
  backButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
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
  },
  insightCard: {
    margin: 16,
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  insightTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2D3748',
    marginBottom: 12,
  },
  insightText: {
    fontSize: 16,
    color: '#4A5568',
    lineHeight: 24,
    marginBottom: 16,
  },
  aiBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#E8F4FD',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  aiBadgeText: {
    color: '#4A90E2',
    fontSize: 12,
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4A90E2',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6C757D',
    textAlign: 'center',
  },
  breakdownContainer: {
    margin: 16,
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2D3748',
    marginBottom: 16,
  },
  breakdownItem: {
    marginBottom: 16,
  },
  breakdownInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  breakdownCategory: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2D3748',
  },
  breakdownAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4A90E2',
  },
  breakdownBar: {
    height: 8,
    backgroundColor: '#E2E8F0',
    borderRadius: 4,
    marginBottom: 4,
  },
  breakdownBarFill: {
    height: '100%',
    backgroundColor: '#4A90E2',
    borderRadius: 4,
  },
  breakdownPercentage: {
    fontSize: 12,
    color: '#6C757D',
    textAlign: 'right',
  },
  tipsContainer: {
    margin: 16,
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tipItem: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'flex-start',
  },
  tipIcon: {
    fontSize: 16,
    marginRight: 12,
    marginTop: 2,
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    color: '#4A5568',
    lineHeight: 20,
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
  secondaryButton: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#4A90E2',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButtonText: {
    color: '#4A90E2',
  },
  emptyState: {
    alignItems: 'center',
    padding: 40,
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 16,
  },
  emptyStateIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2D3748',
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#6C757D',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  emptyStateButton: {
    backgroundColor: '#4A90E2',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 24,
  },
  emptyStateButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
