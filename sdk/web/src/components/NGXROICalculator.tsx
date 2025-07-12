/**
 * NGX Real-time ROI Calculator Component
 * Interactive component that visualizes personalized ROI in real-time
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { motion, AnimatePresence } from 'framer-motion';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

interface ROICalculation {
  metricType: string;
  currentValue: number;
  projectedValue: number;
  improvementPercentage: number;
  monthlyBenefit: number;
  annualBenefit: number;
  paybackMonths: number;
  confidenceLevel: number;
  calculationBasis: string;
  supportingData: Record<string, any>;
}

interface PersonalizedROI {
  userId: string;
  profession: string;
  tier: string;
  totalROIPercentage: number;
  monthlySavings: number;
  annualSavings: number;
  paybackPeriodMonths: number;
  calculations: ROICalculation[];
  keyInsights: string[];
  comparisonScenarios: Record<string, any>;
}

interface NGXROICalculatorProps {
  userContext: {
    profession?: string;
    detectedTier?: string;
    hourlyRate?: number;
    companySize?: string;
    region?: string;
  };
  onROICalculated?: (roi: PersonalizedROI) => void;
  theme?: 'light' | 'dark';
  compact?: boolean;
}

const NGXROICalculator: React.FC<NGXROICalculatorProps> = ({
  userContext,
  onROICalculated,
  theme = 'dark',
  compact = false,
}) => {
  const [roiData, setROIData] = useState<PersonalizedROI | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedTier, setSelectedTier] = useState(userContext.detectedTier || 'ESSENTIAL');
  const [viewMode, setViewMode] = useState<'overview' | 'breakdown' | 'comparison'>('overview');
  const [animationKey, setAnimationKey] = useState(0);

  const tiers = [
    { name: 'ESSENTIAL', price: 79, color: '#6B7280' },
    { name: 'PRO', price: 149, color: '#8B5CF6' },
    { name: 'ELITE', price: 199, color: '#7C3AED' },
    { name: 'PRIME', price: 3997, color: '#6D28D9' },
    { name: 'LONGEVITY', price: 3997, color: '#5B21B6' },
  ];

  const calculateROI = async (tier: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/roi/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userContext: {
            ...userContext,
            detectedTier: tier,
          },
          tier,
          timeframeMonths: 12,
        }),
      });

      if (response.ok) {
        const roiResult = await response.json();
        setROIData(roiResult);
        setAnimationKey(prev => prev + 1);
        onROICalculated?.(roiResult);
      }
    } catch (error) {
      console.error('Error calculating ROI:', error);
      // Fallback to demo data
      setROIData(generateDemoROI(tier));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    calculateROI(selectedTier);
  }, [selectedTier, userContext]);

  const generateDemoROI = (tier: string): PersonalizedROI => {
    const tierPrice = tiers.find(t => t.name === tier)?.price || 79;
    const baseROI = tier === 'PRIME' || tier === 'LONGEVITY' ? 850 : 300;
    
    return {
      userId: 'demo',
      profession: userContext.profession || 'Professional',
      tier,
      totalROIPercentage: baseROI,
      monthlySavings: tierPrice * (baseROI / 100) / 12,
      annualSavings: tierPrice * (baseROI / 100),
      paybackPeriodMonths: 12 / (baseROI / 100),
      calculations: [
        {
          metricType: 'financial',
          currentValue: 5000,
          projectedValue: 6250,
          improvementPercentage: 25,
          monthlyBenefit: 1250,
          annualBenefit: 15000,
          paybackMonths: 2.5,
          confidenceLevel: 0.85,
          calculationBasis: 'Productivity gains',
          supportingData: {},
        },
        {
          metricType: 'time_savings',
          currentValue: 160,
          projectedValue: 200,
          improvementPercentage: 25,
          monthlyBenefit: 800,
          annualBenefit: 9600,
          paybackMonths: 3.2,
          confidenceLevel: 0.80,
          calculationBasis: 'Efficiency improvements',
          supportingData: {},
        },
      ],
      keyInsights: [
        `Your investment pays for itself in ${(12 / (baseROI / 100)).toFixed(1)} months`,
        `${baseROI}% annual ROI - significantly outperforming traditional investments`,
        'Productivity gains compound over time, accelerating career growth',
      ],
      comparisonScenarios: {},
    };
  };

  const chartTheme = useMemo(() => ({
    backgroundColor: theme === 'dark' ? '#1F2937' : '#FFFFFF',
    textColor: theme === 'dark' ? '#F3F4F6' : '#1F2937',
    gridColor: theme === 'dark' ? '#374151' : '#E5E7EB',
    accent: '#8B5CF6',
  }), [theme]);

  const donutChartData = useMemo(() => {
    if (!roiData) return null;

    return {
      labels: roiData.calculations.map(calc => 
        calc.metricType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
      ),
      datasets: [
        {
          data: roiData.calculations.map(calc => calc.annualBenefit),
          backgroundColor: [
            '#8B5CF6',
            '#7C3AED', 
            '#6D28D9',
            '#5B21B6',
            '#4C1D95',
          ],
          borderColor: chartTheme.backgroundColor,
          borderWidth: 2,
        },
      ],
    };
  }, [roiData, chartTheme]);

  const timelineChartData = useMemo(() => {
    if (!roiData) return null;

    const months = Array.from({ length: 12 }, (_, i) => i + 1);
    const tierPrice = tiers.find(t => t.name === selectedTier)?.price || 79;
    
    return {
      labels: months.map(m => `Month ${m}`),
      datasets: [
        {
          label: 'Cumulative Benefits',
          data: months.map(m => roiData.monthlySavings * m + tierPrice * m),
          borderColor: '#8B5CF6',
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          tension: 0.4,
          fill: true,
        },
        {
          label: 'Cumulative Investment',
          data: months.map(m => tierPrice * m),
          borderColor: '#EF4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          fill: true,
        },
      ],
    };
  }, [roiData, selectedTier]);

  const comparisonChartData = useMemo(() => {
    if (!roiData) return null;

    return {
      labels: roiData.calculations.map(calc => 
        calc.metricType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
      ),
      datasets: [
        {
          label: 'Before HIE',
          data: roiData.calculations.map(calc => calc.currentValue),
          backgroundColor: '#6B7280',
        },
        {
          label: 'After HIE',
          data: roiData.calculations.map(calc => calc.projectedValue),
          backgroundColor: '#8B5CF6',
        },
      ],
    };
  }, [roiData]);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          color: chartTheme.textColor,
        },
      },
      tooltip: {
        backgroundColor: chartTheme.backgroundColor,
        titleColor: chartTheme.textColor,
        bodyColor: chartTheme.textColor,
        borderColor: chartTheme.accent,
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: { color: chartTheme.textColor },
        grid: { color: chartTheme.gridColor },
      },
      y: {
        ticks: { color: chartTheme.textColor },
        grid: { color: chartTheme.gridColor },
      },
    },
  };

  if (loading) {
    return (
      <div className={`ngx-roi-calculator ${theme} loading`}>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Calculating your personalized ROI...</p>
        </div>
      </div>
    );
  }

  if (!roiData) {
    return (
      <div className={`ngx-roi-calculator ${theme} error`}>
        <p>Unable to calculate ROI. Please try again.</p>
      </div>
    );
  }

  return (
    <div className={`ngx-roi-calculator ${theme} ${compact ? 'compact' : ''}`}>
      {/* Tier Selection */}
      <div className="tier-selection">
        <h3>Select Your Plan</h3>
        <div className="tier-buttons">
          {tiers.map(tier => (
            <button
              key={tier.name}
              className={`tier-button ${selectedTier === tier.name ? 'active' : ''}`}
              onClick={() => setSelectedTier(tier.name)}
              style={{ 
                borderColor: selectedTier === tier.name ? tier.color : 'transparent',
                backgroundColor: selectedTier === tier.name ? `${tier.color}20` : 'transparent'
              }}
            >
              <span className="tier-name">{tier.name}</span>
              <span className="tier-price">${tier.price}/mo</span>
            </button>
          ))}
        </div>
      </div>

      {/* View Mode Toggle */}
      <div className="view-mode-toggle">
        {['overview', 'breakdown', 'comparison'].map(mode => (
          <button
            key={mode}
            className={`mode-button ${viewMode === mode ? 'active' : ''}`}
            onClick={() => setViewMode(mode as any)}
          >
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </button>
        ))}
      </div>

      {/* ROI Overview */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`${viewMode}-${animationKey}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="roi-content"
        >
          {viewMode === 'overview' && (
            <div className="roi-overview">
              <div className="roi-hero">
                <div className="roi-stat">
                  <h2>{roiData.totalROIPercentage.toFixed(0)}%</h2>
                  <p>Annual ROI</p>
                </div>
                <div className="roi-stat">
                  <h2>{roiData.paybackPeriodMonths.toFixed(1)}</h2>
                  <p>Months to Break-even</p>
                </div>
                <div className="roi-stat">
                  <h2>${roiData.annualSavings.toLocaleString()}</h2>
                  <p>Annual Savings</p>
                </div>
              </div>

              {donutChartData && (
                <div className="chart-container">
                  <h4>Annual Benefits Breakdown</h4>
                  <Doughnut data={donutChartData} options={chartOptions} />
                </div>
              )}

              <div className="key-insights">
                <h4>Key Insights</h4>
                {roiData.keyInsights.map((insight, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="insight"
                  >
                    <span className="insight-icon">💡</span>
                    <p>{insight}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {viewMode === 'breakdown' && (
            <div className="roi-breakdown">
              <div className="metrics-grid">
                {roiData.calculations.map((calc, index) => (
                  <motion.div
                    key={calc.metricType}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="metric-card"
                  >
                    <h4>{calc.metricType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                    <div className="metric-values">
                      <div className="metric-value">
                        <span className="label">Monthly Benefit</span>
                        <span className="value">${calc.monthlyBenefit.toLocaleString()}</span>
                      </div>
                      <div className="metric-value">
                        <span className="label">Annual Benefit</span>
                        <span className="value">${calc.annualBenefit.toLocaleString()}</span>
                      </div>
                      <div className="metric-value">
                        <span className="label">Improvement</span>
                        <span className="value">{calc.improvementPercentage.toFixed(1)}%</span>
                      </div>
                      <div className="metric-value">
                        <span className="label">Confidence</span>
                        <span className="value">{(calc.confidenceLevel * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    <p className="calculation-basis">{calc.calculationBasis}</p>
                  </motion.div>
                ))}
              </div>

              {timelineChartData && (
                <div className="chart-container">
                  <h4>Payback Timeline</h4>
                  <Line data={timelineChartData} options={chartOptions} />
                </div>
              )}
            </div>
          )}

          {viewMode === 'comparison' && (
            <div className="roi-comparison">
              {comparisonChartData && (
                <div className="chart-container">
                  <h4>Before vs After HIE</h4>
                  <Bar data={comparisonChartData} options={chartOptions} />
                </div>
              )}

              <div className="tier-comparison">
                <h4>Compare Plans</h4>
                <div className="comparison-grid">
                  {tiers.map(tier => {
                    const tierROI = tier.price * 3; // Simplified calculation
                    const isSelected = tier.name === selectedTier;
                    
                    return (
                      <div
                        key={tier.name}
                        className={`comparison-card ${isSelected ? 'selected' : ''}`}
                        onClick={() => setSelectedTier(tier.name)}
                      >
                        <h5>{tier.name}</h5>
                        <div className="comparison-price">${tier.price}/mo</div>
                        <div className="comparison-roi">{((tierROI - tier.price * 12) / (tier.price * 12) * 100).toFixed(0)}% ROI</div>
                        <div className="comparison-payback">
                          {(tier.price / (tierROI / 12)).toFixed(1)} mo payback
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* CTA */}
      <div className="roi-cta">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="cta-button"
          onClick={() => window.open('/signup', '_blank')}
        >
          Start Your HIE Journey - {selectedTier} Plan
        </motion.button>
        <p className="cta-subtitle">
          Join {roiData.profession}s who are already experiencing these results
        </p>
      </div>

      <style jsx>{`
        .ngx-roi-calculator {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
          border-radius: 16px;
          background: ${theme === 'dark' ? 'linear-gradient(135deg, #1F2937 0%, #111827 100%)' : 'linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%)'};
          border: 1px solid ${theme === 'dark' ? '#374151' : '#E5E7EB'};
          color: ${theme === 'dark' ? '#F3F4F6' : '#1F2937'};
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }

        .ngx-roi-calculator.compact {
          padding: 1rem;
        }

        .tier-selection {
          margin-bottom: 2rem;
        }

        .tier-selection h3 {
          text-align: center;
          margin-bottom: 1rem;
          color: #8B5CF6;
        }

        .tier-buttons {
          display: flex;
          gap: 0.5rem;
          justify-content: center;
          flex-wrap: wrap;
        }

        .tier-button {
          padding: 0.75rem 1rem;
          border: 2px solid transparent;
          border-radius: 8px;
          background: transparent;
          color: inherit;
          cursor: pointer;
          transition: all 0.3s ease;
          text-align: center;
        }

        .tier-button:hover {
          transform: translateY(-2px);
        }

        .tier-button.active {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        }

        .tier-name {
          display: block;
          font-weight: bold;
        }

        .tier-price {
          display: block;
          font-size: 0.875rem;
          opacity: 0.8;
        }

        .view-mode-toggle {
          display: flex;
          gap: 0.5rem;
          justify-content: center;
          margin-bottom: 2rem;
        }

        .mode-button {
          padding: 0.5rem 1rem;
          border: 1px solid #374151;
          border-radius: 6px;
          background: transparent;
          color: inherit;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .mode-button.active {
          background: #8B5CF6;
          border-color: #8B5CF6;
          color: white;
        }

        .roi-overview {
          text-align: center;
        }

        .roi-hero {
          display: flex;
          justify-content: space-around;
          margin-bottom: 2rem;
          flex-wrap: wrap;
        }

        .roi-stat h2 {
          font-size: 2.5rem;
          font-weight: bold;
          margin: 0;
          background: linear-gradient(135deg, #8B5CF6, #5B21B6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .roi-stat p {
          margin: 0.5rem 0 0 0;
          opacity: 0.8;
        }

        .chart-container {
          margin: 2rem 0;
          padding: 1rem;
          border-radius: 8px;
          background: ${theme === 'dark' ? 'rgba(0, 0, 0, 0.2)' : 'rgba(255, 255, 255, 0.5)'};
        }

        .chart-container h4 {
          text-align: center;
          margin-bottom: 1rem;
          color: #8B5CF6;
        }

        .key-insights {
          margin-top: 2rem;
          text-align: left;
        }

        .key-insights h4 {
          text-align: center;
          margin-bottom: 1rem;
          color: #8B5CF6;
        }

        .insight {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          margin-bottom: 1rem;
          padding: 1rem;
          border-radius: 8px;
          background: ${theme === 'dark' ? 'rgba(139, 92, 246, 0.1)' : 'rgba(139, 92, 246, 0.05)'};
          border-left: 4px solid #8B5CF6;
        }

        .insight-icon {
          font-size: 1.2rem;
          flex-shrink: 0;
        }

        .insight p {
          margin: 0;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .metric-card {
          padding: 1.5rem;
          border-radius: 12px;
          background: ${theme === 'dark' ? 'rgba(139, 92, 246, 0.1)' : 'rgba(139, 92, 246, 0.05)'};
          border: 1px solid ${theme === 'dark' ? '#8B5CF6' : 'rgba(139, 92, 246, 0.2)'};
        }

        .metric-card h4 {
          margin: 0 0 1rem 0;
          color: #8B5CF6;
          text-align: center;
        }

        .metric-values {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }

        .metric-value {
          text-align: center;
        }

        .metric-value .label {
          display: block;
          font-size: 0.875rem;
          opacity: 0.7;
          margin-bottom: 0.25rem;
        }

        .metric-value .value {
          display: block;
          font-weight: bold;
          font-size: 1.1rem;
        }

        .calculation-basis {
          font-size: 0.875rem;
          opacity: 0.8;
          text-align: center;
          margin: 0;
          font-style: italic;
        }

        .comparison-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .comparison-card {
          padding: 1rem;
          border-radius: 8px;
          border: 2px solid transparent;
          background: ${theme === 'dark' ? 'rgba(0, 0, 0, 0.2)' : 'rgba(255, 255, 255, 0.5)'};
          cursor: pointer;
          transition: all 0.3s ease;
          text-align: center;
        }

        .comparison-card:hover {
          transform: translateY(-2px);
        }

        .comparison-card.selected {
          border-color: #8B5CF6;
          background: ${theme === 'dark' ? 'rgba(139, 92, 246, 0.1)' : 'rgba(139, 92, 246, 0.05)'};
        }

        .comparison-card h5 {
          margin: 0 0 0.5rem 0;
          color: #8B5CF6;
        }

        .comparison-price {
          font-size: 1.2rem;
          font-weight: bold;
          margin-bottom: 0.5rem;
        }

        .comparison-roi {
          color: #10B981;
          font-weight: bold;
          margin-bottom: 0.25rem;
        }

        .comparison-payback {
          font-size: 0.875rem;
          opacity: 0.8;
        }

        .roi-cta {
          text-align: center;
          margin-top: 2rem;
          padding-top: 2rem;
          border-top: 1px solid ${theme === 'dark' ? '#374151' : '#E5E7EB'};
        }

        .cta-button {
          padding: 1rem 2rem;
          border: none;
          border-radius: 8px;
          background: linear-gradient(135deg, #8B5CF6, #5B21B6);
          color: white;
          font-size: 1.1rem;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
          margin-bottom: 0.5rem;
        }

        .cta-button:hover {
          box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);
        }

        .cta-subtitle {
          margin: 0.5rem 0 0 0;
          opacity: 0.8;
          font-size: 0.875rem;
        }

        .loading {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 400px;
        }

        .loading-spinner {
          text-align: center;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid ${theme === 'dark' ? '#374151' : '#E5E7EB'};
          border-top: 4px solid #8B5CF6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem auto;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .ngx-roi-calculator {
            padding: 1rem;
          }

          .roi-hero {
            flex-direction: column;
            gap: 1rem;
          }

          .metrics-grid {
            grid-template-columns: 1fr;
          }

          .tier-buttons {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default NGXROICalculator;