// src/components/common/StatusChip.tsx
import { Chip } from '@mui/material';
import { CheckCircle, XCircle, AlertTriangle, Clock, RefreshCw } from 'lucide-react';
import type { JobStatus } from '@/types/jobs';
import { brand, semantic, neutral } from '@/theme/colors';
import { radius } from '@/theme/radius';

type UnifiedStatus = string | JobStatus | 'unknown';

interface StatusChipProps {
  status?: UnifiedStatus;
  label?: string;
  size?: 'small' | 'medium';
}

interface ChipStyle {
  bgcolor: string;
  color: string;
  border: string;
  icon: React.ReactElement;
}

const getChipStyle = (status: string): ChipStyle => {
  switch (status.toLowerCase()) {
    case 'ok':
    case 'completed':
      return {
        bgcolor: semantic.successSubtle,
        color: semantic.successDark,
        border: `1px solid ${semantic.success}33`,
        icon: <CheckCircle size={12} />,
      };
    case 'degraded':
    case 'queued':
    case 'validating':
    case 'saving_files':
      return {
        bgcolor: semantic.warningSubtle,
        color: semantic.warningDark,
        border: `1px solid ${semantic.warning}33`,
        icon: <Clock size={12} />,
      };
    case 'failed':
    case 'error':
    case 'unavailable':
      return {
        bgcolor: semantic.errorSubtle,
        color: semantic.errorDark,
        border: `1px solid ${semantic.error}33`,
        icon: <XCircle size={12} />,
      };
    case 'indexing':
    case 'active':
      return {
        bgcolor: brand.orangeSubtle,
        color: brand.orangeDark,
        border: `1px solid ${brand.orange}33`,
        icon: <RefreshCw size={12} style={{ animation: 'spin 2s linear infinite' }} />,
      };
    default:
      return {
        bgcolor: neutral[100],
        color: neutral[500],
        border: `1px solid ${neutral[200]}`,
        icon: <AlertTriangle size={12} />,
      };
  }
};

export function StatusChip({ status = 'unknown', label, size = 'small' }: StatusChipProps) {
  const style = getChipStyle(status);
  const displayLabel = label ?? status.replace(/_/g, ' ').toUpperCase();

  return (
    <>
      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
      <Chip
        size={size}
        icon={style.icon}
        label={displayLabel}
        sx={{
          bgcolor: style.bgcolor,
          color: style.color,
          border: style.border,
          fontWeight: 700,
          fontSize: size === 'small' ? '0.65rem' : '0.75rem',
          borderRadius: `${radius.chip}px`,
          height: size === 'small' ? 22 : 28,
          '& .MuiChip-icon': {
            color: 'inherit',
            ml: '6px',
          },
        }}
      />
    </>
  );
}
