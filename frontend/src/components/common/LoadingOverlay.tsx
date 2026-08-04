// src/components/common/LoadingOverlay.tsx
import { Box, CircularProgress, Typography } from '@mui/material';
import { brand } from '@/theme/colors';

interface LoadingOverlayProps {
  message?: string;
}

export function LoadingOverlay({ message = 'Loading...' }: LoadingOverlayProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 8,
        height: '100%',
        minHeight: 200,
        gap: 2,
      }}
    >
      <CircularProgress
        size={36}
        thickness={4}
        sx={{ color: brand.orange }}
      />
      <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
        {message}
      </Typography>
    </Box>
  );
}
