// src/components/common/EmptyState.tsx
import { Box, Typography } from '@mui/material';
import type { ReactNode } from 'react';
import { brand } from '@/theme/colors';
import { radius } from '@/theme/radius';

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        py: 8,
        px: 4,
      }}
    >
      {/* Icon container */}
      <Box
        sx={{
          width: 72,
          height: 72,
          borderRadius: `${radius.avatar}px`,
          bgcolor: brand.orangeSubtle,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 3,
          '& svg': { color: brand.orange, width: 32, height: 32 },
        }}
      >
        {icon}
      </Box>

      <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, color: 'text.primary' }}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4, maxWidth: 380, lineHeight: 1.65 }}>
        {description}
      </Typography>
      {action && <Box>{action}</Box>}
    </Box>
  );
}
