/**
 * Real-time Dashboard - Frontend für Live Monitoring
 * 
 * Features:
 * - WebSocket für Live Updates
 * - Real-time Metrics
 * - Live Alerts
 * - Agent Status
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, CheckCircle, Activity, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { EmptyState } from '@/components/empty-states/EmptyState';

interface Metric {
  name: string;
  value: number;
  labels: Record<string, string>;
  timestamp: string;
}

interface Alert {
  id: string;
  level: string;
  title: string;
  message: string;
  agent_name?: string;
  account_id?: string;
  timestamp: string;
  resolved: boolean;
}

export const RealtimeDashboard: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const metricsHistoryRef = useRef<Map<string, any[]>>(new Map());

  useEffect(() => {
    // WebSocket Verbindung
    const ws = new WebSocket(`ws://localhost:8000/api/v1/realtime/ws`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      console.log('WebSocket verbunden');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'metric') {
        const metric = message.data;
        setMetrics((prev) => [...prev.slice(-99), metric]);
        
        // Speichere in History
        const history = metricsHistoryRef.current.get(metric.name) || [];
        history.push(metric);
        if (history.length > 100) history.shift();
        metricsHistoryRef.current.set(metric.name, history);
      } else if (message.type === 'alert') {
        setAlerts((prev) => [message.data, ...prev.slice(0, 49)]);
      } else if (message.type === 'alert_resolved') {
        setAlerts((prev) => prev.filter(a => a.id !== message.data.id));
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket Fehler:', error);
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
      console.log('WebSocket getrennt');
    };

    // Lade initiale Daten
    fetch('/api/v1/realtime/metrics')
      .then(res => res.json())
      .then(data => {
        if (data.metrics) {
          const metricsList = Object.entries(data.metrics).map(([name, m]: [string, any]) => ({
            name,
            ...m
          }));
          setMetrics(metricsList);
        }
      });

    fetch('/api/v1/realtime/alerts')
      .then(res => res.json())
      .then(data => {
        if (data.alerts) {
          setAlerts(data.alerts);
        }
      });

    return () => {
      ws.close();
    };
  }, []);

  // Chart-Daten für Metrics
  const chartData = Array.from(metricsHistoryRef.current.entries()).map(([name, history]) => ({
    name,
    data: history.map((m, i) => ({
      time: i,
      value: m.value
    }))
  }));

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">{t('realtime.title')}</h1>
        <Badge variant={connected ? "default" : "destructive"}>
          {connected ? (
            <>
              <CheckCircle className="w-4 h-4 mr-2" />
              {t('realtime.connected')}
            </>
          ) : (
            <>
              <AlertTriangle className="w-4 h-4 mr-2" />
              {t('realtime.disconnected')}
            </>
          )}
        </Badge>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              {t('realtime.activeAlerts')} ({alerts.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded border ${
                    alert.level === 'critical'
                      ? 'border-red-500 bg-red-50'
                      : alert.level === 'error'
                      ? 'border-orange-500 bg-orange-50'
                      : 'border-yellow-500 bg-yellow-50'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-[var(--color-text-primary)]">{alert.title}</div>
                      <div className="text-sm text-[var(--color-text-secondary)]">{alert.message}</div>
                      {alert.agent_name && (
                        <div className="text-xs text-[var(--color-text-tertiary)] mt-1">
                          {t('realtime.agent')}: {alert.agent_name}
                        </div>
                      )}
                    </div>
                    <Badge variant="outline">{alert.level}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {metrics.slice(-4).map((metric) => (
          <Card key={metric.name}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="w-4 h-4" />
                {metric.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value.toFixed(2)}</div>
              <div className="text-xs text-[var(--color-text-tertiary)] mt-1">
                {new Date(metric.timestamp).toLocaleTimeString(
                  i18n.language === 'de' ? 'de-DE' : 
                  i18n.language === 'es' ? 'es-ES' : 
                  i18n.language === 'fr' ? 'fr-FR' : 
                  i18n.language === 'it' ? 'it-IT' : 
                  'en-US'
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Metrics Chart */}
      {chartData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t('realtime.metricsTrend')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData[0]?.data || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#8884d8"
                  name={chartData[0]?.name || t('realtime.metric')}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {metrics.length === 0 && (
        <EmptyState
          icon={Activity}
          title={t('realtime.noMetricsAvailable')}
          description={t('realtime.noMetricsAvailableDesc')}
          action={{
            label: t('realtime.refresh'),
            onClick: () => {
              window.location.reload();
            }
          }}
        />
      )}
    </div>
  );
};
