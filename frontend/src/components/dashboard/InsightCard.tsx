import { Card, CardContent, Typography, Box } from '@mui/material';
import { neutral, brand, semantic } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

interface InsightCardProps {
  title?: string;
  summary: string;
  confidence?: number;
  timestamp?: string | Date;
}

export function InsightCard({
  title = "AI Business Insights",
  summary,
  confidence,
  timestamp,
}: InsightCardProps) {
  return (
    <Card
      sx={{
        borderRadius: `${radius.card}px`,
        boxShadow: shadows.card,
        border: 'none',
        bgcolor: brand.orangeSubtle,
        color: neutral[900],
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: brand.orange, mb: 1, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {title}
        </Typography>
        
        <Typography variant="body1" sx={{ lineHeight: 1.6, mb: (confidence !== undefined || timestamp) ? 2 : 0 }}>
          {summary}
        </Typography>

        {(confidence !== undefined || timestamp) && (
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mt: 2, pt: 2, borderTop: `1px solid ${brand.orange}33` }}>
            {confidence !== undefined && (
              <Typography variant="caption" sx={{ fontWeight: 600, color: confidence > 0.8 ? semantic.success : brand.orange }}>
                Confidence: {(confidence * 100).toFixed(0)}%
              </Typography>
            )}
            {timestamp && (
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                Generated: {new Date(timestamp).toLocaleString()}
              </Typography>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
