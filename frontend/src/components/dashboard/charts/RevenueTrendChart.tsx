import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { brand, neutral } from '@/theme/colors';

interface RevenueTrendChartProps {
  data: any[];
}

export function RevenueTrendChart({ data }: RevenueTrendChartProps) {
  if (!data || data.length === 0) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#9CA3AF', fontSize: '0.875rem' }}>
      No chart data available
    </div>
  );

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
      <defs>
        <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
          <stop offset="5%" stopColor={brand.orange} stopOpacity={0.8}/>
          <stop offset="95%" stopColor={brand.orange} stopOpacity={0}/>
        </linearGradient>
      </defs>
      <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: neutral[500], fontSize: 12 }} dy={10} />
      <YAxis 
        axisLine={false} 
        tickLine={false} 
        tick={{ fill: neutral[500], fontSize: 12 }} 
        dx={-10} 
        tickFormatter={(value) => `$${value >= 1000 ? (value/1000).toFixed(1) + 'k' : value}`} 
      />
      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={neutral[200]} />
      <Tooltip 
        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
        itemStyle={{ color: neutral[900], fontWeight: 600 }}
      />
      <Area type="monotone" dataKey="revenue" stroke={brand.orange} strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue)" />
    </AreaChart>
    </ResponsiveContainer>
  );
}
