// src/components/common/ErrorState.tsx
import { Box, Typography, Button } from '@mui/material';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { semantic } from '@/theme/colors';
import { radius } from '@/theme/radius';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'Something went wrong',
  message = 'Failed to load data. Please try again later.',
  onRetry,
}: ErrorStateProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        py: 6,
        px: 4,
        bgcolor: semantic.errorSubtle,
        borderRadius: `${radius.card}px`,
      }}
    >
      <Box
        sx={{
          width: 56,
          height: 56,
          borderRadius: `${radius.avatar}px`,
          bgcolor: `${semantic.error}18`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 2.5,
        }}
      >
        <AlertCircle size={26} color={semantic.error} />
      </Box>

      <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.75, color: semantic.errorDark }}>
        {title}
      </Typography>
      <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3, maxWidth: 380 }}>
        {message}
      </Typography>
      {onRetry && (
        <Button
          variant="outlined"
          color="error"
          size="small"
          startIcon={<RefreshCw size={14} />}
          onClick={onRetry}
          sx={{ borderRadius: `${radius.button}px` }}
        >
          Try Again
        </Button>
      )}
    </Box>
  );
}
