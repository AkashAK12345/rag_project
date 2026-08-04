// src/components/common/PageHeader.tsx
import { Box, Typography, Stack } from '@mui/material';
import type { ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

export function PageHeader({ title, subtitle, action }: PageHeaderProps) {
  return (
    <Stack
      direction="row"
      sx={{
        justifyContent: 'space-between',
        alignItems: 'flex-end',
        mb: 4,
      }}
    >
      <Box>
        <Typography
          variant="h3"
          sx={{
            fontWeight: 800,
            letterSpacing: '-0.02em',
            lineHeight: 1.15,
            mb: subtitle ? 0.5 : 0,
            color: 'text.primary',
          }}
        >
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.5 }}>
            {subtitle}
          </Typography>
        )}
      </Box>
      {action && <Box sx={{ flexShrink: 0, ml: 3 }}>{action}</Box>}
    </Stack>
  );
}
