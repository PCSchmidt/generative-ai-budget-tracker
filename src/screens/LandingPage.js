/**
 * Landing Page - AI Budget Tracker
 * Public landing page with call-to-action for signup/login
 */

import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const LandingPage = () => {
  const { isAuthenticated, user, isLoading } = useAuth();
  const navigate = useNavigate();

  // Debug info
  console.log('LandingPage - Auth state:', { isAuthenticated, user, isLoading });

  // Redirect to dashboard if authenticated
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      console.log('LandingPage: User is authenticated, redirecting to dashboard');
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  // Smooth scroll to section
  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const headerStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    background: 'rgba(15, 23, 42, 0.95)',
    backdropFilter: 'blur(10px)',
    borderBottom: '1px solid rgba(226, 232, 240, 0.1)',
    padding: '1rem 2rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    zIndex: 1000,
    transition: 'all 0.3s ease'
  };

  const logoStyle = {
    fontSize: '1.5rem',
    fontWeight: '700',
    color: '#f8fafc',
    textDecoration: 'none'
  };

  const navLinksStyle = {
    display: 'flex',
    gap: '1rem',
    alignItems: 'center'
  };

  const navLinkStyle = {
    color: '#cbd5e1',
    textDecoration: 'none',
    fontSize: '1rem',
    fontWeight: '500',
    padding: '0.5rem 1rem',
    borderRadius: '8px',
    transition: 'all 0.3s ease'
  };
  const containerStyle = {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
    display: 'flex',
    flexDirection: 'column',
    paddingTop: '80px', // Account for fixed header
    position: 'relative'
  };

  const backgroundAnimationStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `
      radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 40% 80%, rgba(16, 185, 129, 0.1) 0%, transparent 50%)
    `,
    animation: 'float 6s ease-in-out infinite'
  };

  const contentStyle = {
    textAlign: 'center',
    zIndex: 1,
    position: 'relative',
    maxWidth: '800px',
    margin: '0 auto'
  };

  const titleStyle = {
    fontSize: '4rem',
    fontWeight: '800',
    background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #06d6a0 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    marginBottom: '1rem',
    lineHeight: '1.1'
  };

  const subtitleStyle = {
    fontSize: '1.5rem',
    color: '#94a3b8',
    marginBottom: '3rem',
    lineHeight: '1.6'
  };

  const buttonContainerStyle = {
    display: 'flex',
    gap: '1.5rem',
    justifyContent: 'center',
    flexWrap: 'wrap'
  };

  const buttonStyle = {
    padding: '16px 32px',
    borderRadius: '12px',
    fontSize: '1.1rem',
    fontWeight: '600',
    textDecoration: 'none',
    transition: 'all 0.3s ease',
    minWidth: '180px',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center'
  };

  const primaryButtonStyle = {
    ...buttonStyle,
    background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
    color: 'white',
    border: 'none'
  };

  const secondaryButtonStyle = {
    ...buttonStyle,
    background: 'transparent',
    border: '2px solid #374151',
    color: '#f8fafc'
  };

  const featureGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '2rem',
    marginTop: '4rem',
    maxWidth: '1000px'
  };

  const featureCardStyle = {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(10px)',
    borderRadius: '16px',
    padding: '2rem',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    textAlign: 'left'
  };

  const featureIconStyle = {
    fontSize: '2.5rem',
    marginBottom: '1rem',
    display: 'block'
  };

  const featureTitleStyle = {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#f8fafc',
    marginBottom: '0.5rem'
  };

  const featureDescStyle = {
    color: '#94a3b8',
    fontSize: '1rem',
    lineHeight: '1.6'
  };

  return (
    <>
      {/* Fixed Header */}
      <header style={headerStyle}>
        <Link to="/" style={logoStyle}>
          🤖 AI Budget Tracker
        </Link>
        <nav style={navLinksStyle} className="nav-links">
          <button 
            onClick={() => scrollToSection('features')} 
            style={{...navLinkStyle, background: 'none', border: 'none', cursor: 'pointer'}}
            className="nav-link"
          >
            Features
          </button>
          <button 
            onClick={() => scrollToSection('about')} 
            style={{...navLinkStyle, background: 'none', border: 'none', cursor: 'pointer'}}
            className="nav-link"
          >
            About
          </button>
          <Link to="/login" style={{...navLinkStyle, background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6'}} className="nav-link">
            Login
          </Link>
          <Link to="/signup" style={{...navLinkStyle, background: '#3b82f6', color: 'white'}} className="nav-link">
            Sign Up
          </Link>
        </nav>
      </header>

      <div style={containerStyle}>
        <style>
          {`
            html {
              scroll-behavior: smooth;
            }
            
            @keyframes float {
              0%, 100% { transform: translateY(0px) rotate(0deg); }
              33% { transform: translateY(-10px) rotate(1deg); }
              66% { transform: translateY(5px) rotate(-1deg); }
            }

            @keyframes fadeInUp {
              from {
                opacity: 0;
                transform: translateY(30px);
              }
              to {
                opacity: 1;
                transform: translateY(0);
              }
            }

            .feature-card {
              animation: fadeInUp 0.8s ease forwards;
              transition: transform 0.3s ease, box-shadow 0.3s ease;
            }

            .feature-card:hover {
              transform: translateY(-5px);
              box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            }

            .feature-card:nth-child(1) { animation-delay: 0.1s; }
            .feature-card:nth-child(2) { animation-delay: 0.2s; }
            .feature-card:nth-child(3) { animation-delay: 0.3s; }
            
            .primary-button:hover {
              background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
              transform: translateY(-2px);
              box-shadow: 0 15px 35px rgba(37, 99, 235, 0.4);
            }
            
            .secondary-button:hover {
              border-color: #3b82f6 !important;
              background: rgba(59, 130, 246, 0.1) !important;
            }

            .nav-link:hover {
              background: rgba(59, 130, 246, 0.1) !important;
              color: #3b82f6 !important;
            }

            /* Mobile responsiveness */
            @media (max-width: 768px) {
              .hero-title {
                font-size: 2.5rem !important;
              }
              .hero-subtitle {
                font-size: 1.2rem !important;
              }
              .button-container {
                flex-direction: column !important;
                align-items: center !important;
              }
              .feature-grid {
                grid-template-columns: 1fr !important;
                gap: 1.5rem !important;
              }
              .nav-links {
                gap: 0.5rem !important;
              }
              .nav-link {
                padding: 0.5rem !important;
                font-size: 0.9rem !important;
              }
            }
          `}
        </style>
        
        <div style={backgroundAnimationStyle}></div>
        
        {/* Hero Section */}
        <section style={{...contentStyle, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '80vh', padding: '2rem'}}>
          <h1 style={titleStyle} className="hero-title">AI Budget Tracker</h1>
          <p style={subtitleStyle} className="hero-subtitle">
            Take control of your finances with intelligent insights, automated categorization, 
            and personalized recommendations powered by artificial intelligence.
          </p>
          
          <div style={buttonContainerStyle} className="button-container">
            <Link 
              to="/signup" 
              style={primaryButtonStyle}
              className="primary-button"
            >
              Get Started Free
            </Link>
            <Link 
              to="/login" 
              style={secondaryButtonStyle}
              className="secondary-button"
            >
              Sign In
            </Link>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" style={{padding: '4rem 2rem', maxWidth: '1200px', margin: '0 auto'}}>
          <h2 style={{fontSize: '2.5rem', fontWeight: '700', color: '#f8fafc', textAlign: 'center', marginBottom: '3rem'}}>
            Why Choose AI Budget Tracker?
          </h2>
          
          <div style={featureGridStyle} className="feature-grid">
            <div style={featureCardStyle} className="feature-card">
              <span style={featureIconStyle}>🤖</span>
              <h3 style={featureTitleStyle}>AI-Powered Insights</h3>
              <p style={featureDescStyle}>
                Get intelligent analysis of your spending patterns and personalized recommendations for better financial health.
              </p>
            </div>

            <div style={featureCardStyle} className="feature-card">
              <span style={featureIconStyle}>📊</span>
              <h3 style={featureTitleStyle}>Smart Categorization</h3>
              <p style={featureDescStyle}>
                Automatically categorize expenses using machine learning, saving you time and ensuring accuracy.
              </p>
            </div>

            <div style={featureCardStyle} className="feature-card">
              <span style={featureIconStyle}>🎯</span>
              <h3 style={featureTitleStyle}>Goal Tracking</h3>
              <p style={featureDescStyle}>
                Set financial goals and track your progress with AI-powered predictions and actionable insights.
              </p>
            </div>
          </div>
        </section>

        {/* About Section */}
        <section id="about" style={{padding: '4rem 2rem', textAlign: 'center', maxWidth: '800px', margin: '0 auto'}}>
          <h2 style={{fontSize: '2.5rem', fontWeight: '700', color: '#f8fafc', marginBottom: '2rem'}}>
            The Future of Personal Finance
          </h2>
          <p style={{fontSize: '1.2rem', color: '#cbd5e1', lineHeight: '1.6', marginBottom: '2rem'}}>
            Built with cutting-edge AI technology, our budget tracker doesn't just record your expenses—it understands them. 
            Get insights that help you make smarter financial decisions and achieve your goals faster.
          </p>
          <div style={{display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '2rem'}}>
            <Link 
              to="/signup" 
              style={{...primaryButtonStyle, fontSize: '1.2rem', padding: '18px 36px'}}
              className="primary-button"
            >
              Start Your Financial Journey
            </Link>
          </div>
        </section>
      </div>
    </>
  );
};

export default LandingPage;
