import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import apiService from '../services/apiService';

export default function AddExpenseScreen({ navigation }) {
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const predefinedCategories = [
    '🍕 Food & Dining',
    '🚗 Transportation',
    '🛍️ Shopping',
    '🎬 Entertainment',
    '💡 Utilities',
    '🏥 Healthcare',
    '🎓 Education',
    '💰 Other',
  ];

  const analyzeExpense = async () => {
    if (!description.trim()) return;

    try {
      setIsAnalyzing(true);
      const result = await apiService.categorizeExpense(description, parseFloat(amount) || 0);
      setAiSuggestion(result.categorization);
      
      // Auto-fill category if AI is confident
      if (result.categorization?.confidence > 0.7) {
        setCategory(result.categorization.category);
      }
    } catch (error) {
      console.error('AI analysis error:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = async () => {
    // Validation
    if (!description.trim()) {
      Alert.alert('Missing Information', 'Please enter a description for your expense.');
      return;
    }

    if (!amount.trim() || isNaN(parseFloat(amount))) {
      Alert.alert('Invalid Amount', 'Please enter a valid amount.');
      return;
    }

    const expenseAmount = parseFloat(amount);
    if (expenseAmount <= 0) {
      Alert.alert('Invalid Amount', 'Amount must be greater than zero.');
      return;
    }

    try {
      setLoading(true);
      
      const expenseData = {
        description: description.trim(),
        amount: expenseAmount,
        category: category || 'Other',
      };

      const result = await apiService.createExpense(expenseData);
      
      Alert.alert(
        'Success! 🎉',
        `Expense "${description}" has been added successfully.`,
        [
          {
            text: 'Add Another',
            onPress: () => {
              setDescription('');
              setAmount('');
              setCategory('');
              setAiSuggestion(null);
            }
          },
          {
            text: 'Go to Dashboard',
            onPress: () => navigation.navigate('Dashboard'),
            style: 'default'
          }
        ]
      );

    } catch (error) {
      console.error('Submit error:', error);
      Alert.alert(
        'Error',
        'Failed to add expense. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity 
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Add New Expense</Text>
          <Text style={styles.subtitle}>Track your spending with AI assistance</Text>
        </View>

        {/* Form */}
        <View style={styles.formContainer}>
          {/* Description Input */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Description</Text>
            <TextInput
              style={styles.textInput}
              value={description}
              onChangeText={setDescription}
              placeholder="e.g., Coffee at Starbucks, Gas station, Grocery shopping"
              multiline={true}
              numberOfLines={2}
              onBlur={analyzeExpense}
            />
          </View>

          {/* Amount Input */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Amount ($)</Text>
            <TextInput
              style={styles.textInput}
              value={amount}
              onChangeText={setAmount}
              placeholder="0.00"
              keyboardType="decimal-pad"
            />
          </View>

          {/* AI Analysis */}
          {(isAnalyzing || aiSuggestion) && (
            <View style={styles.aiContainer}>
              <Text style={styles.aiTitle}>🤖 AI Analysis</Text>
              {isAnalyzing ? (
                <View style={styles.analyzingContainer}>
                  <ActivityIndicator size="small" color="#4A90E2" />
                  <Text style={styles.analyzingText}>Analyzing expense...</Text>
                </View>
              ) : aiSuggestion ? (
                <View style={styles.suggestionContainer}>
                  <Text style={styles.suggestionText}>
                    Suggested category: <Text style={styles.categoryHighlight}>
                      {aiSuggestion.category}
                    </Text>
                  </Text>
                  <Text style={styles.confidenceText}>
                    Confidence: {Math.round(aiSuggestion.confidence * 100)}%
                  </Text>
                  {!aiSuggestion.ai_used && (
                    <Text style={styles.fallbackText}>
                      (Using smart rules - full AI coming soon!)
                    </Text>
                  )}
                </View>
              ) : null}
            </View>
          )}

          {/* Category Selection */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Category</Text>
            <View style={styles.categoryContainer}>
              {predefinedCategories.map((cat) => (
                <TouchableOpacity
                  key={cat}
                  style={[
                    styles.categoryButton,
                    category === cat && styles.categoryButtonSelected
                  ]}
                  onPress={() => setCategory(cat)}
                >
                  <Text style={[
                    styles.categoryButtonText,
                    category === cat && styles.categoryButtonTextSelected
                  ]}>
                    {cat}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Custom Category Input */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Custom Category (Optional)</Text>
            <TextInput
              style={styles.textInput}
              value={category}
              onChangeText={setCategory}
              placeholder="Enter custom category"
            />
          </View>

          {/* Submit Button */}
          <TouchableOpacity
            style={[styles.submitButton, loading && styles.submitButtonDisabled]}
            onPress={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.submitButtonText}>💾 Add Expense</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  scrollView: {
    flex: 1,
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
  formContainer: {
    padding: 16,
  },
  inputGroup: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2D3748',
    marginBottom: 8,
  },
  textInput: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  aiContainer: {
    backgroundColor: '#E8F4FD',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    borderLeftWidth: 4,
    borderLeftColor: '#4A90E2',
  },
  aiTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2D3748',
    marginBottom: 8,
  },
  analyzingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  analyzingText: {
    marginLeft: 8,
    color: '#6C757D',
    fontSize: 14,
  },
  suggestionContainer: {
    marginTop: 4,
  },
  suggestionText: {
    fontSize: 14,
    color: '#2D3748',
    marginBottom: 4,
  },
  categoryHighlight: {
    fontWeight: 'bold',
    color: '#4A90E2',
  },
  confidenceText: {
    fontSize: 12,
    color: '#6C757D',
    marginBottom: 4,
  },
  fallbackText: {
    fontSize: 12,
    color: '#9CA3AF',
    fontStyle: 'italic',
  },
  categoryContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  categoryButton: {
    backgroundColor: 'white',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 8,
  },
  categoryButtonSelected: {
    backgroundColor: '#4A90E2',
    borderColor: '#4A90E2',
  },
  categoryButtonText: {
    fontSize: 14,
    color: '#6C757D',
    fontWeight: '500',
  },
  categoryButtonTextSelected: {
    color: 'white',
  },
  submitButton: {
    backgroundColor: '#4A90E2',
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 24,
    shadowColor: '#4A90E2',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  submitButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
