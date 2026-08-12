import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { brand, neutral } from '@/theme/colors';

interface DonutChartProps {
  data: any[];
  dataKey: string;
  nameKey: string;
}

const COLORS = [brand.orange, '#3B82F6', '#14B8A6', '#8B5CF6', '#10B981', '#F59E0B'];

export function DonutChart({ data, dataKey, nameKey }: DonutChartProps) {
  if (!data || data.length === 0) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#9CA3AF', fontSize: '0.875rem' }}>
      No chart data available
    </div>
  );

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
      <Pie
        data={data}
        innerRadius={60}
        outerRadius={100}
        paddingAngle={5}
        dataKey={dataKey}
        nameKey={nameKey}
        stroke="none"
      >
        {data.map((_entry, index) => (
          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
        ))}
      </Pie>
      <Tooltip 
        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
        itemStyle={{ color: neutral[900], fontWeight: 600 }}
      />
      <Legend 
        verticalAlign="bottom" 
        height={36} 
        iconType="circle"
        formatter={(value) => <span style={{ color: neutral[700], fontWeight: 500 }}>{value}</span>}
      />
    </PieChart>
    </ResponsiveContainer>
  );
}
