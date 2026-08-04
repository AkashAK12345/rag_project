// src/components/common/StatCard.tsx
import { Card, CardContent, Typography, Box, Stack, Skeleton } from '@mui/material';
import type { ReactNode } from 'react';
import { brand, semantic } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: ReactNode;
  subtitle?: ReactNode;
  loading?: boolean;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
}

const colorMap: Record<string, { bg: string; icon: string; shadow: string }> = {
  primary:   { bg: brand.orangeSubtle,          icon: brand.orange,    shadow: `${brand.orange}22` },
  secondary: { bg: '#EFF6FF',                   icon: semantic.info,   shadow: `${semantic.info}22` },
  success:   { bg: semantic.successSubtle,       icon: semantic.success, shadow: `${semantic.success}22` },
  warning:   { bg: semantic.warningSubtle,       icon: semantic.warning, shadow: `${semantic.warning}22` },
  error:     { bg: semantic.errorSubtle,         icon: semantic.error,  shadow: `${semantic.error}22` },
  info:      { bg: '#EFF6FF',                   icon: semantic.info,   shadow: `${semantic.info}22` },
};

export function StatCard({ title, value, icon, subtitle, loading, color = 'primary' }: StatCardProps) {
  const colors = colorMap[color] ?? colorMap.primary;

  return (
    <Card
      sx={{
        height: '100%',
        borderRadius: `${radius.card}px`,
        boxShadow: shadows.card,
        border: 'none',
        transition: 'box-shadow 200ms ease, transform 200ms ease',
        '&:hover': {
          boxShadow: shadows.cardHover,
          transform: 'translateY(-2px)',
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="overline"
              sx={{ color: 'text.secondary', fontWeight: 700, fontSize: '0.6875rem', letterSpacing: '0.07em', mb: 1.5, display: 'block' }}
            >
              {title}
            </Typography>
            {loading ? (
              <>
                <Skeleton variant="text" width={80} height={44} sx={{ borderRadius: 1 }} />
                <Skeleton variant="text" width={120} height={18} sx={{ mt: 0.5 }} />
              </>
            ) : (
              <>
                <Typography variant="h3" sx={{ fontWeight: 800, lineHeight: 1, mb: subtitle ? 0.75 : 0 }}>
                  {value}
                </Typography>
                {subtitle && (
                  <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.4, display: 'block' }}>
                    {subtitle}
                  </Typography>
                )}
              </>
            )}
          </Box>
          {icon && (
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: `${radius.avatar}px`,
                flexShrink: 0,
                ml: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: colors.bg,
                color: colors.icon,
                boxShadow: `0 4px 12px ${colors.shadow}`,
                '& svg': { width: 22, height: 22 },
              }}
            >
              {icon}
            </Box>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
