import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ResponsiveContainer } from 'recharts';
import { brand, neutral } from '@/theme/colors';

interface HorizontalBarChartProps {
  data: any[];
  dataKey: string;
  nameKey: string;
}

export function HorizontalBarChart({ data, dataKey, nameKey }: HorizontalBarChartProps) {
  if (!data || data.length === 0) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#9CA3AF', fontSize: '0.875rem' }}>
      No chart data available
    </div>
  );

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={neutral[200]} />
      <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: neutral[500], fontSize: 12 }} />
      <YAxis 
        type="category" 
        dataKey={nameKey} 
        axisLine={false} 
        tickLine={false} 
        tick={{ fill: neutral[700], fontSize: 12, fontWeight: 500 }} 
        width={100}
      />
      <Tooltip 
        cursor={{ fill: 'transparent' }}
        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
      />
      <Bar dataKey={dataKey} radius={[0, 4, 4, 0]} barSize={24}>
        {data.map((_entry, index) => (
          <Cell key={`cell-${index}`} fill={brand.orange} />
        ))}
      </Bar>
    </BarChart>
    </ResponsiveContainer>
  );
}
