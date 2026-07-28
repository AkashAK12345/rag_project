// src/components/common/EmptyState.tsx
import { Box, Typography } from '@mui/material';
import type { ReactNode } from 'react';

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
        p: 6,
        bgcolor: 'background.paper',
        borderRadius: 2,
        border: (t) => `1px dashed ${t.palette.divider}`,
      }}
    >
      <Box sx={{ color: 'text.disabled', '& > svg': { fontSize: 64, mb: 2 } }}>
        {icon}
      </Box>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
        {description}
      </Typography>
      {action && <Box>{action}</Box>}
    </Box>
  );
}
