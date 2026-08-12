import { StatCard } from '@/components/common/StatCard';
import type { ReactNode } from 'react';
import CountUp from 'react-countup';
import { Box, Chip } from '@mui/material';
import { ArrowUp, ArrowDown } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  icon?: ReactNode;
  trend?: {
    value: number | string;
    isPositive: boolean;
    label: string;
  };
  loading?: boolean;
}

export function KPICard({ title, value, prefix, suffix, decimals = 0, icon, trend, loading }: KPICardProps) {
  const isNumber = typeof value === 'number';

  // Handle potential CJS/ESM interop where CountUp is double-nested in a default object
  const CountUpComponent = (CountUp as any).default || CountUp;

  const displayValue = isNumber ? (
    <CountUpComponent 
      end={value as number} 
      prefix={prefix} 
      suffix={suffix} 
      decimals={decimals} 
      duration={1.5}
      separator=","
    />
  ) : (
    <>{prefix}{value}{suffix}</>
  );

  const subtitle = trend ? (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
      <Chip 
        size="small" 
        icon={trend.isPositive ? <ArrowUp size={14} /> : <ArrowDown size={14} />} 
        label={trend.value}
        sx={{ 
          height: 20, 
          fontSize: '0.75rem', 
          fontWeight: 600,
          bgcolor: trend.isPositive ? '#10B9811A' : '#EF44441A',
          color: trend.isPositive ? '#10B981' : '#EF4444',
          '& .MuiChip-icon': { color: 'inherit', ml: 0.5, mr: -0.25 }
        }}
      />
      <span style={{ color: '#6B7280', fontSize: '0.75rem' }}>{trend.label}</span>
    </Box>
  ) : undefined;

  return (
    <StatCard
      title={title}
      value={displayValue as any}
      icon={icon}
      subtitle={subtitle}
      loading={loading}
      color="primary"
    />
  );
}
