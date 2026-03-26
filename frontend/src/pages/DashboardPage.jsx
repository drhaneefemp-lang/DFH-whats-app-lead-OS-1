import { useState, useMemo } from 'react';
import {
  ChartBar,
  Users,
  ChatCircleDots,
  Clock,
  TrendUp,
  TrendDown,
  Funnel,
  CalendarBlank,
  CaretDown
} from '@phosphor-icons/react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { format, subDays, startOfDay, endOfDay, startOfWeek, startOfMonth } from 'date-fns';
import { Calendar } from '../components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '../components/ui/popover';
import { Button } from '../components/ui/button';
import {
  useDashboardMetrics,
  useLeadsOverTime,
  useMessagesOverTime,
  useResponseTimes
} from '../hooks/useDashboard';

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

const TIME_PRESETS = [
  { label: 'Today', value: 'today' },
  { label: 'This Week', value: 'week' },
  { label: 'This Month', value: 'month' },
  { label: 'Custom', value: 'custom' }
];

const DashboardPage = () => {
  const [timePreset, setTimePreset] = useState('month');
  const [customRange, setCustomRange] = useState({ from: null, to: null });
  const [showDatePicker, setShowDatePicker] = useState(false);

  // Calculate date range based on preset
  const dateRange = useMemo(() => {
    const now = new Date();
    
    if (timePreset === 'today') {
      return {
        start: startOfDay(now).toISOString(),
        end: endOfDay(now).toISOString()
      };
    } else if (timePreset === 'week') {
      return {
        start: startOfWeek(now, { weekStartsOn: 1 }).toISOString(),
        end: endOfDay(now).toISOString()
      };
    } else if (timePreset === 'month') {
      return {
        start: startOfMonth(now).toISOString(),
        end: endOfDay(now).toISOString()
      };
    } else if (timePreset === 'custom' && customRange.from) {
      return {
        start: startOfDay(customRange.from).toISOString(),
        end: customRange.to ? endOfDay(customRange.to).toISOString() : endOfDay(customRange.from).toISOString()
      };
    }
    
    // Default to last 30 days
    return {
      start: subDays(now, 30).toISOString(),
      end: endOfDay(now).toISOString()
    };
  }, [timePreset, customRange]);

  // Fetch data
  const { metrics, loading: metricsLoading } = useDashboardMetrics(dateRange.start, dateRange.end);
  const { data: leadsData, loading: leadsLoading } = useLeadsOverTime(dateRange.start, dateRange.end, 'day');
  const { data: messagesData, loading: messagesLoading } = useMessagesOverTime(dateRange.start, dateRange.end, 'day');
  const { data: responseData, loading: responseLoading } = useResponseTimes(dateRange.start, dateRange.end);

  // Transform data for charts
  const statusData = useMemo(() => {
    if (!metrics?.leads_by_status) return [];
    return Object.entries(metrics.leads_by_status)
      .map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value }))
      .filter(item => item.value > 0);
  }, [metrics]);

  const sourceData = useMemo(() => {
    if (!metrics?.leads_by_source) return [];
    return Object.entries(metrics.leads_by_source)
      .map(([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value }))
      .filter(item => item.value > 0);
  }, [metrics]);

  const responseDistribution = useMemo(() => {
    if (!responseData?.distribution) return [];
    return [
      { name: '<5 min', value: responseData.distribution.under_5min },
      { name: '5-15 min', value: responseData.distribution['5_to_15min'] },
      { name: '15-60 min', value: responseData.distribution['15_to_60min'] },
      { name: '1-4 hrs', value: responseData.distribution['1_to_4h'] },
      { name: '>4 hrs', value: responseData.distribution.over_4h }
    ].filter(item => item.value > 0);
  }, [responseData]);

  const handlePresetChange = (preset) => {
    setTimePreset(preset);
    if (preset !== 'custom') {
      setShowDatePicker(false);
    }
  };

  const handleDateSelect = (range) => {
    setCustomRange(range || { from: null, to: null });
    if (range?.from && range?.to) {
      setShowDatePicker(false);
    }
  };

  const formatDateRange = () => {
    if (timePreset === 'today') return 'Today';
    if (timePreset === 'week') return 'This Week';
    if (timePreset === 'month') return 'This Month';
    if (customRange.from) {
      const fromStr = format(customRange.from, 'MMM d');
      const toStr = customRange.to ? format(customRange.to, 'MMM d, yyyy') : format(customRange.from, 'MMM d, yyyy');
      return `${fromStr} - ${toStr}`;
    }
    return 'Select dates';
  };

  return (
    <div className="min-h-screen bg-gray-50" data-testid="dashboard-page">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ChartBar size={28} weight="fill" className="text-green-500" />
            <div>
              <h1 className="text-xl font-bold text-gray-900 font-[Chivo]">Dashboard</h1>
              <p className="text-xs text-gray-500">Analytics and performance metrics</p>
            </div>
          </div>

          {/* Time Filter */}
          <div className="flex items-center gap-2">
            {TIME_PRESETS.map((preset) => (
              <button
                key={preset.value}
                onClick={() => handlePresetChange(preset.value)}
                className={`px-3 py-1.5 text-sm font-medium rounded-sm transition-colors ${
                  timePreset === preset.value
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                data-testid={`time-filter-${preset.value}`}
              >
                {preset.label}
              </button>
            ))}

            {/* Custom Date Picker */}
            {timePreset === 'custom' && (
              <Popover open={showDatePicker} onOpenChange={setShowDatePicker}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="flex items-center gap-2 text-sm"
                    data-testid="custom-date-picker"
                  >
                    <CalendarBlank size={16} />
                    {formatDateRange()}
                    <CaretDown size={14} />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="end">
                  <Calendar
                    mode="range"
                    selected={customRange}
                    onSelect={handleDateSelect}
                    numberOfMonths={2}
                  />
                </PopoverContent>
              </Popover>
            )}
          </div>
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-4 gap-4">
          <KPICard
            title="Total Leads"
            value={metrics?.total_leads || 0}
            icon={<Users size={24} />}
            color="blue"
            loading={metricsLoading}
            subtitle={`${metrics?.new_leads || 0} new`}
          />
          <KPICard
            title="Conversion Rate"
            value={`${metrics?.conversion_rate || 0}%`}
            icon={<TrendUp size={24} />}
            color="green"
            loading={metricsLoading}
            subtitle={`${metrics?.converted_leads || 0} converted`}
          />
          <KPICard
            title="Avg Response Time"
            value={responseData?.average_minutes ? `${Math.round(responseData.average_minutes)} min` : '0 min'}
            icon={<Clock size={24} />}
            color="yellow"
            loading={responseLoading}
            subtitle={`${responseData?.total_responses || 0} responses`}
          />
          <KPICard
            title="Total Messages"
            value={metrics?.total_messages || 0}
            icon={<ChatCircleDots size={24} />}
            color="purple"
            loading={metricsLoading}
            subtitle={`${metrics?.inbound_messages || 0} in / ${metrics?.outbound_messages || 0} out`}
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-2 gap-6">
          {/* Leads Over Time */}
          <div className="bg-white border border-gray-200 rounded-sm p-4">
            <h3 className="font-bold text-gray-900 mb-4">Leads Over Time</h3>
            {leadsLoading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="loading-spinner w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full" />
              </div>
            ) : leadsData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={leadsData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 11 }}
                    tickFormatter={(val) => {
                      try {
                        return format(new Date(val), 'MMM d');
                      } catch {
                        return val;
                      }
                    }}
                  />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip 
                    labelFormatter={(val) => {
                      try {
                        return format(new Date(val), 'MMM d, yyyy');
                      } catch {
                        return val;
                      }
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="total" stroke="#3b82f6" strokeWidth={2} name="Total Leads" />
                  <Line type="monotone" dataKey="converted" stroke="#22c55e" strokeWidth={2} name="Converted" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400">
                No data available
              </div>
            )}
          </div>

          {/* Messages Over Time */}
          <div className="bg-white border border-gray-200 rounded-sm p-4">
            <h3 className="font-bold text-gray-900 mb-4">Messages Over Time</h3>
            {messagesLoading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="loading-spinner w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full" />
              </div>
            ) : messagesData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={messagesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 11 }}
                    tickFormatter={(val) => {
                      try {
                        return format(new Date(val), 'MMM d');
                      } catch {
                        return val;
                      }
                    }}
                  />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="inbound" fill="#3b82f6" name="Inbound" />
                  <Bar dataKey="outbound" fill="#22c55e" name="Outbound" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400">
                No data available
              </div>
            )}
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-3 gap-6">
          {/* Leads by Status */}
          <div className="bg-white border border-gray-200 rounded-sm p-4">
            <h3 className="font-bold text-gray-900 mb-4">Leads by Status</h3>
            {metricsLoading ? (
              <div className="h-48 flex items-center justify-center">
                <div className="loading-spinner w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full" />
              </div>
            ) : statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={70}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                    labelLine={false}
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-48 flex items-center justify-center text-gray-400">
                No data
              </div>
            )}
          </div>

          {/* Leads by Source */}
          <div className="bg-white border border-gray-200 rounded-sm p-4">
            <h3 className="font-bold text-gray-900 mb-4">Leads by Source</h3>
            {metricsLoading ? (
              <div className="h-48 flex items-center justify-center">
                <div className="loading-spinner w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full" />
              </div>
            ) : sourceData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={sourceData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={80} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#22c55e" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-48 flex items-center justify-center text-gray-400">
                No data
              </div>
            )}
          </div>

          {/* Response Time Distribution */}
          <div className="bg-white border border-gray-200 rounded-sm p-4">
            <h3 className="font-bold text-gray-900 mb-4">Response Time Distribution</h3>
            {responseLoading ? (
              <div className="h-48 flex items-center justify-center">
                <div className="loading-spinner w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full" />
              </div>
            ) : responseDistribution.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={responseDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#f59e0b" name="Responses" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-48 flex items-center justify-center text-gray-400">
                No data
              </div>
            )}
          </div>
        </div>

        {/* Agent Performance */}
        <div className="bg-white border border-gray-200 rounded-sm p-4">
          <h3 className="font-bold text-gray-900 mb-4">Agent Performance</h3>
          {metricsLoading ? (
            <div className="h-32 flex items-center justify-center">
              <div className="loading-spinner w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full" />
            </div>
          ) : metrics?.agent_performance?.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm" data-testid="agent-performance-table">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-bold text-gray-700">Agent</th>
                    <th className="text-right py-3 px-4 font-bold text-gray-700">Leads</th>
                    <th className="text-right py-3 px-4 font-bold text-gray-700">Converted</th>
                    <th className="text-right py-3 px-4 font-bold text-gray-700">Conversion Rate</th>
                    <th className="py-3 px-4 font-bold text-gray-700">Progress</th>
                  </tr>
                </thead>
                <tbody>
                  {metrics.agent_performance.map((agent) => (
                    <tr key={agent.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold text-xs">
                            {agent.name.charAt(0)}
                          </div>
                          {agent.name}
                        </div>
                      </td>
                      <td className="text-right py-3 px-4 font-medium">{agent.leads_count}</td>
                      <td className="text-right py-3 px-4 text-green-600 font-medium">{agent.converted_count}</td>
                      <td className="text-right py-3 px-4">
                        <span className={`font-medium ${agent.conversion_rate >= 20 ? 'text-green-600' : 'text-gray-600'}`}>
                          {agent.conversion_rate.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3 px-4 w-32">
                        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500 transition-all"
                            style={{ width: `${Math.min(agent.conversion_rate, 100)}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="h-32 flex items-center justify-center text-gray-400">
              No agents with assigned leads
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// KPI Card Component
const KPICard = ({ title, value, icon, color, loading, subtitle }) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600'
  };

  return (
    <div className="bg-white border border-gray-200 rounded-sm p-4" data-testid={`kpi-${title.toLowerCase().replace(/\s+/g, '-')}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">{title}</p>
          {loading ? (
            <div className="h-8 w-20 bg-gray-200 animate-pulse rounded" />
          ) : (
            <p className="text-2xl font-bold text-gray-900 font-[Chivo]">{value}</p>
          )}
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-sm ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
