# AI Budget Tracker - Frontend

React web application for the AI Budget Tracker, deployed on **Vercel**.

## 🚀 Deployment Architecture

- **Frontend**: Vercel (this directory)
- **Backend**: Railway (../backend/)
- **Database**: PostgreSQL on Railway

## 🛠️ Development

### Local Development
```bash
cd frontend
npm install
npm start
```
Runs on `http://localhost:3000` and connects to Railway backend.

### Production Build
```bash
npm run build
```
Creates optimized build for Vercel deployment.

## 🌐 Environment Variables

### Vercel Production
Set in Vercel dashboard:
```
REACT_APP_API_URL=https://generative-ai-budget-tracker-production.up.railway.app
REACT_APP_ENVIRONMENT=production
```

### Local Development
Uses `.env.development`:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## 📁 Project Structure

```
frontend/
├── public/           # Static assets
├── src/
│   ├── components/   # Reusable React components
│   ├── contexts/     # React contexts (Auth, etc.)
│   ├── screens/      # Page components
│   ├── services/     # API services
│   ├── styles/       # Global styles
│   └── utils/        # Utility functions
├── App.js           # Main app component
├── index.js         # React DOM entry point
└── package.json     # Dependencies and scripts
```

## 🔐 Authentication Features

- JWT-based authentication
- Protected routes
- Password visibility toggles with eyeball icons (👁️/🙈)
- Professional fintech UI design

## 🔗 API Integration

Connects to Railway backend for:
- User authentication
- Expense management
- AI categorization
- Financial insights

## 📦 Key Dependencies

- React 18.2.0
- React Router DOM 6.30.1
- Axios for API calls
- Chart.js for data visualization
- Framer Motion for animations
