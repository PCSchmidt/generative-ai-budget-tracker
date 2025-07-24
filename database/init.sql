-- AI Budget Tracker Database Schema
-- PostgreSQL initialization script

-- Create database if it doesn't exist (handled by Docker)
-- CREATE DATABASE budget_tracker;

-- Connect to the database
\c budget_tracker;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types for better data integrity
CREATE TYPE expense_category AS ENUM (
    'food_dining',
    'transportation', 
    'shopping',
    'entertainment',
    'bills_utilities',
    'healthcare',
    'education',
    'travel',
    'groceries',
    'home_garden',
    'personal_care',
    'gifts_donations',
    'business',
    'other'
);

CREATE TYPE goal_status AS ENUM (
    'active',
    'completed',
    'paused',
    'cancelled'
);

CREATE TYPE transaction_type AS ENUM (
    'expense',
    'income',
    'transfer'
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Expenses table (main transaction table)
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(12, 2) NOT NULL,
    description TEXT NOT NULL,
    category expense_category NOT NULL,
    transaction_type transaction_type DEFAULT 'expense',
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    ai_categorized BOOLEAN DEFAULT false,
    ai_confidence DECIMAL(3, 2), -- 0.00 to 1.00
    merchant_name VARCHAR(255),
    location VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Budgets table
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category expense_category NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    period VARCHAR(50) NOT NULL DEFAULT 'monthly', -- monthly, weekly, yearly
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Financial goals table
CREATE TABLE financial_goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_amount DECIMAL(12, 2) NOT NULL,
    current_amount DECIMAL(12, 2) DEFAULT 0.00,
    target_date DATE,
    status goal_status DEFAULT 'active',
    category VARCHAR(100), -- emergency_fund, vacation, car, house, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI insights table (stores generated financial advice)
CREATE TABLE ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(100) NOT NULL, -- spending_pattern, budget_advice, goal_suggestion
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    confidence_score DECIMAL(3, 2),
    is_read BOOLEAN DEFAULT false,
    relevance_score DECIMAL(3, 2),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Spending patterns table (AI analysis results)
CREATE TABLE spending_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pattern_type VARCHAR(100) NOT NULL, -- recurring, seasonal, unusual, trending
    category expense_category,
    description TEXT NOT NULL,
    frequency VARCHAR(50), -- daily, weekly, monthly
    average_amount DECIMAL(12, 2),
    trend_direction VARCHAR(20), -- increasing, decreasing, stable
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_expenses_date ON expenses(transaction_date);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_budgets_user_id ON budgets(user_id);
CREATE INDEX idx_budgets_category ON budgets(category);
CREATE INDEX idx_goals_user_id ON financial_goals(user_id);
CREATE INDEX idx_insights_user_id ON ai_insights(user_id);
CREATE INDEX idx_patterns_user_id ON spending_patterns(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_goals_updated_at BEFORE UPDATE ON financial_goals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development
INSERT INTO users (email, username, full_name, hashed_password) VALUES
('demo@example.com', 'demo_user', 'Demo User', '$2b$12$demo_hashed_password_here');

-- Get the demo user ID for sample data
-- Note: In real implementation, this would be handled by the application
INSERT INTO expenses (user_id, amount, description, category, transaction_date, merchant_name) VALUES
((SELECT id FROM users WHERE username = 'demo_user'), 12.50, 'Coffee and pastry', 'food_dining', CURRENT_TIMESTAMP - INTERVAL '1 day', 'Local Coffee Shop'),
((SELECT id FROM users WHERE username = 'demo_user'), 45.00, 'Grocery shopping', 'groceries', CURRENT_TIMESTAMP - INTERVAL '2 days', 'SuperMarket'),
((SELECT id FROM users WHERE username = 'demo_user'), 25.00, 'Gas for car', 'transportation', CURRENT_TIMESTAMP - INTERVAL '3 days', 'Gas Station');

INSERT INTO budgets (user_id, name, category, amount, period, start_date) VALUES
((SELECT id FROM users WHERE username = 'demo_user'), 'Monthly Food Budget', 'food_dining', 300.00, 'monthly', DATE_TRUNC('month', CURRENT_DATE)),
((SELECT id FROM users WHERE username = 'demo_user'), 'Grocery Budget', 'groceries', 150.00, 'monthly', DATE_TRUNC('month', CURRENT_DATE));

INSERT INTO financial_goals (user_id, title, description, target_amount, target_date, category) VALUES
((SELECT id FROM users WHERE username = 'demo_user'), 'Emergency Fund', 'Build 3-month emergency fund', 5000.00, CURRENT_DATE + INTERVAL '6 months', 'emergency_fund'),
((SELECT id FROM users WHERE username = 'demo_user'), 'Vacation Savings', 'Save for summer vacation', 2000.00, CURRENT_DATE + INTERVAL '4 months', 'vacation');

-- Create a view for expense analytics
CREATE VIEW expense_analytics AS
SELECT 
    u.username,
    e.category,
    DATE_TRUNC('month', e.transaction_date) as month,
    COUNT(*) as transaction_count,
    SUM(e.amount) as total_amount,
    AVG(e.amount) as average_amount,
    MIN(e.amount) as min_amount,
    MAX(e.amount) as max_amount
FROM expenses e
JOIN users u ON e.user_id = u.id
GROUP BY u.username, e.category, DATE_TRUNC('month', e.transaction_date);

COMMENT ON TABLE expenses IS 'Main transaction table storing all user expenses and income';
COMMENT ON TABLE budgets IS 'User-defined budgets for different expense categories';
COMMENT ON TABLE financial_goals IS 'Financial goals and savings targets';
COMMENT ON TABLE ai_insights IS 'AI-generated financial insights and recommendations';
COMMENT ON TABLE spending_patterns IS 'Detected spending patterns and trends';

-- Grant permissions (adjust as needed for production)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO budget_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO budget_user;
