import { ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { neutral } from '@/theme/colors';

interface ForecastLineChartProps {
  data: any[];
}

export function ForecastLineChart({ data }: ForecastLineChartProps) {
  if (!data || data.length === 0) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#9CA3AF', fontSize: '0.875rem' }}>
      No chart data available
    </div>
  );

  return (
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
      <defs>
        <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2}/>
          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
        </linearGradient>
      </defs>
      <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: neutral[500], fontSize: 12 }} dy={10} />
      <YAxis 
        axisLine={false} 
        tickLine={false} 
        tick={{ fill: neutral[500], fontSize: 12 }} 
        dx={-10} 
        tickFormatter={(value) => `${value >= 1000 ? (value/1000).toFixed(1) + 'k' : value}`} 
      />
      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={neutral[200]} />
      <Tooltip 
        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
      />
      <Legend verticalAlign="top" height={36} iconType="circle" />
      
      {/* Historical Actuals */}
      <Line type="monotone" dataKey="actual" name="Historical Actual" stroke={neutral[700]} strokeWidth={2} dot={false} />
      
      {/* Forecast Band */}
      <Area type="monotone" dataKey="upper_bound" stroke="none" fill="url(#colorForecast)" fillOpacity={1} />
      <Area type="monotone" dataKey="lower_bound" stroke="none" fill="#ffffff" fillOpacity={1} />

      <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#3B82F6" strokeWidth={3} strokeDasharray="5 5" dot={false} />
    </ComposedChart>
    </ResponsiveContainer>
  );
}
