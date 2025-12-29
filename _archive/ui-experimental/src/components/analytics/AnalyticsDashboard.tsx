/**
 * Analytics Dashboard - Frontend für Advanced Analytics
 * 
 * Features:
 * - Metriken anzeigen
 * - Insights
 * - Anomaly Detection
 * - Forecasting
 * - Vergleich
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TrendingUp, TrendingDown, AlertTriangle, BarChart3 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { EmptyState } from '@/components/empty-states/EmptyState';
import { SmartSuggestions } from '@/components/smart-suggestions/SmartSuggestions';

interface Insights {
  metric_name: string;
  current_value: number;
  mean: number;
  median: number;
  stdev: number;
  trend: string;
  trend_percentage: number;
  anomaly: {
    is_anomaly: boolean;
    score: number;
    reason?: string;
  };
  forecast: {
    next_7_days: number[];
    method: string;
  };
  data_points_count: number;
}

export const AnalyticsDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [selectedMetric, setSelectedMetric] = useState<string>('');
  const [metrics, setMetrics] = useState<string[]>([]);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [loading, setLoading] = useState(false);
  const [forecastData, setForecastData] = useState<any[]>([]);

  useEffect(() => {
    loadMetrics();
  }, []);

  useEffect(() => {
    if (selectedMetric) {
      loadInsights(selectedMetric);
      loadForecast(selectedMetric);
    }
  }, [selectedMetric]);

  const loadMetrics = async () => {
    try {
      const response = await fetch('/api/v1/analytics/metrics');
      const data = await response.json();
      setMetrics(data.metrics || []);
      if (data.metrics && data.metrics.length > 0) {
        setSelectedMetric(data.metrics[0]);
      }
    } catch (error) {
      console.error('Fehler beim Laden der Metriken:', error);
    }
  };

  const loadInsights = async (metricName: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/analytics/insights/${metricName}`);
      const data = await response.json();
      setInsights(data);
    } catch (error) {
      console.error('Fehler beim Laden der Insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadForecast = async (metricName: string) => {
    try {
      const response = await fetch(`/api/v1/analytics/forecast/${metricName}?periods=7`);
      const data = await response.json();
      
      // Erstelle Chart-Daten
      const chartData = data.predictions.map((pred: number, index: number) => ({
        day: `Tag ${index + 1}`,
        prediction: pred,
        lower: data.confidence_intervals[index]?.[0] || pred * 0.9,
        upper: data.confidence_intervals[index]?.[1] || pred * 1.1,
      }));
      setForecastData(chartData);
    } catch (error) {
      console.error('Fehler beim Laden der Forecast:', error);
    }
  };

  const trackMetric = async (metricName: string, value: number) => {
    try {
      await fetch('/api/v1/analytics/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metric_name: metricName,
          value: value
        })
      });
      loadInsights(metricName);
    } catch (error) {
      console.error('Fehler beim Tracken:', error);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">{t('analytics.title')}</h1>
      
      {/* Smart Suggestions */}
      <SmartSuggestions context={{ currentPage: 'analytics', userActions: [] }} />

      {/* Metric Selection */}
      <div className="mb-6">
        <Select value={selectedMetric} onValueChange={setSelectedMetric}>
          <SelectTrigger className="w-64">
            <SelectValue placeholder={t('analytics.selectMetric')} />
          </SelectTrigger>
          <SelectContent>
            {metrics.map((metric) => (
              <SelectItem key={metric} value={metric}>
                {metric}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="text-center py-12">{t('common.loading')}</div>
      ) : insights ? (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t('analytics.currentValue')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{insights.current_value.toFixed(1)}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t('analytics.average')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{insights.mean.toFixed(1)}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t('analytics.trend')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  {insights.trend === 'increasing' ? (
                    <TrendingUp className="w-5 h-5 text-green-500" />
                  ) : insights.trend === 'decreasing' ? (
                    <TrendingDown className="w-5 h-5 text-red-500" />
                  ) : (
                    <BarChart3 className="w-5 h-5 text-[var(--color-text-tertiary)]" />
                  )}
                  <span className="text-2xl font-bold text-[var(--color-text-primary)]">
                    {insights.trend_percentage > 0 ? '+' : ''}
                    {insights.trend_percentage.toFixed(1)}%
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{t('analytics.anomaly')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  {insights.anomaly.is_anomaly ? (
                    <>
                      <AlertTriangle className="w-5 h-5 text-[var(--color-error)]" />
                      <span className="text-sm text-[var(--color-text-primary)]">{t('analytics.detected')}</span>
                    </>
                  ) : (
                    <span className="text-sm text-[var(--color-success)]">{t('analytics.normal')}</span>
                  )}
                </div>
                <div className="text-xs text-[var(--color-text-tertiary)] mt-1">
                  {t('analytics.score')}: {insights.anomaly.score.toFixed(2)}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Forecast Chart */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>{t('analytics.forecast7Days')}</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="prediction"
                    stroke="#8884d8"
                    name={t('analytics.prediction')}
                  />
                  <Line
                    type="monotone"
                    dataKey="lower"
                    stroke="#82ca9d"
                    strokeDasharray="5 5"
                    name={t('analytics.lowerBound')}
                  />
                  <Line
                    type="monotone"
                    dataKey="upper"
                    stroke="#82ca9d"
                    strokeDasharray="5 5"
                    name={t('analytics.upperBound')}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">{t('analytics.statistics')}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>{t('analytics.median')}:</span>
                    <span className="font-medium">{insights.median.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>{t('analytics.standardDeviation')}:</span>
                    <span className="font-medium">{insights.stdev.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>{t('analytics.dataPoints')}:</span>
                    <span className="font-medium">{insights.data_points_count}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">{t('analytics.anomalyDetails')}</CardTitle>
              </CardHeader>
              <CardContent>
                {insights.anomaly.reason && (
                  <p className="text-sm text-[var(--color-text-secondary)]">{insights.anomaly.reason}</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">{t('analytics.forecastMethod')}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm font-medium">{insights.forecast.method}</p>
              </CardContent>
            </Card>
          </div>
        </>
      ) : (
        <EmptyState
          icon={BarChart3}
          title={t('analytics.noMetricSelected')}
          description={t('analytics.noMetricSelectedDesc')}
          action={{
            label: t('analytics.selectMetricNow'),
            onClick: () => {
              // Focus on metric selector
              const selector = document.querySelector('[role="combobox"]') as HTMLElement;
              selector?.click();
            }
          }}
        />
      )}
    </div>
  );
};
