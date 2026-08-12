import { Card, CardContent, Typography, Box, Skeleton } from '@mui/material';
import type { ReactNode } from 'react';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

interface ChartCardProps {
  title: string;
  subtitle?: ReactNode;
  action?: ReactNode;
  loading?: boolean;
  height?: number | string;
  children: ReactNode;
}

export function ChartCard({
  title,
  subtitle,
  action,
  loading,
  height = 350,
  children,
}: ChartCardProps) {
  return (
    <Card
      sx={{
        height: '100%',
        borderRadius: `${radius.card}px`,
        boxShadow: shadows.card,
        border: 'none',
        display: 'flex',
        flexDirection: 'column',
        transition: 'box-shadow 200ms ease, transform 200ms ease',
        '&:hover': {
          boxShadow: shadows.cardHover,
          transform: 'translateY(-2px)',
        },
      }}
    >
      <CardContent sx={{ p: 3, pb: 1, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          {action && <Box>{action}</Box>}
        </Box>

        <Box sx={{ flexGrow: 1, height, position: 'relative', width: '100%' }}>
          {loading ? (
            <Skeleton variant="rounded" width="100%" height="100%" />
          ) : (
            children
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
