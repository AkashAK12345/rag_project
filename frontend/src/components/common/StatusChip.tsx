// src/components/common/StatusChip.tsx
import { Chip } from '@mui/material';
import type { JobStatus } from '@/types/jobs';
import {
  CheckCircle, Error as ErrorIcon, WarningAmber, HourglassEmpty, Autorenew
} from '@mui/icons-material';

type UnifiedStatus = string | JobStatus | 'unknown';

interface StatusChipProps {
  status?: UnifiedStatus;
  label?: string;
  size?: 'small' | 'medium';
}

export function StatusChip({ status = 'unknown', label, size = 'small' }: StatusChipProps) {
  const getProps = () => {
    switch (status.toLowerCase()) {
      case 'ok':
      case 'completed':
        return { color: 'success' as const, icon: <CheckCircle /> };
      case 'degraded':
      case 'queued':
        return { color: 'warning' as const, icon: <HourglassEmpty /> };
      case 'unavailable':
      case 'failed':
      case 'error':
        return { color: 'error' as const, icon: <ErrorIcon /> };
      case 'indexing':
      case 'active':
        return { color: 'primary' as const, icon: <Autorenew sx={{ animation: 'spin 2s linear infinite' }} /> };
      default:
        return { color: 'default' as const, icon: <WarningAmber /> };
    }
  };

  const { color, icon } = getProps();

  return (
    <Chip
      size={size}
      color={color}
      icon={icon}
      label={label || status.toUpperCase()}
      variant="outlined"
      sx={{
        fontWeight: 600,
        '@keyframes spin': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      }}
    />
  );
}
