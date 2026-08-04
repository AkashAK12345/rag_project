// src/components/chat/ChatInput.tsx
import { useState, KeyboardEvent } from 'react';
import { Box, TextField, IconButton, InputAdornment, CircularProgress, Stack, Tooltip } from '@mui/material';
import { Send, Paperclip, Mic } from 'lucide-react';
import { brand, neutral } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [value, setValue] = useState('');

  const handleSend = () => {
    if (!value.trim() || isLoading) return;
    onSend(value.trim());
    setValue('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        p: { xs: 2, md: 3 },
        bgcolor: 'background.paper',
        borderTop: `1px solid ${neutral[100]}`,
      }}
    >
      <Box
        sx={{
          maxWidth: 840,
          mx: 'auto',
          position: 'relative',
        }}
      >
        <TextField
          variant="outlined"
          fullWidth
          multiline
          maxRows={6}
          placeholder="Ask me anything about your business data…"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start" sx={{ alignSelf: 'flex-end', mb: 1.5, mr: 0 }}>
                  <Tooltip title="Attach file (coming soon)">
                    <span>
                      <IconButton size="small" disabled sx={{ color: neutral[400] }}>
                        <Paperclip size={20} />
                      </IconButton>
                    </span>
                  </Tooltip>
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end" sx={{ alignSelf: 'flex-end', mb: 0.75, ml: 1 }}>
                  <Stack direction="row" spacing={0.5}>
                    <Tooltip title="Voice input (coming soon)">
                      <span>
                        <IconButton size="small" disabled sx={{ color: neutral[400], mr: 0.5 }}>
                          <Mic size={20} />
                        </IconButton>
                      </span>
                    </Tooltip>
                    <IconButton
                      onClick={handleSend}
                      disabled={!value.trim() || isLoading}
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: `${radius.full}px`,
                        bgcolor: !value.trim() || isLoading ? neutral[200] : brand.orange,
                        color: !value.trim() || isLoading ? neutral[400] : neutral.white,
                        boxShadow: !value.trim() || isLoading ? 'none' : `0 4px 12px ${brand.orange}50`,
                        transition: 'all 200ms ease',
                        '&:hover': {
                          bgcolor: !value.trim() || isLoading ? neutral[200] : brand.orangeDark,
                          transform: !value.trim() || isLoading ? 'none' : 'scale(1.05)',
                        },
                        '&.Mui-disabled': {
                          bgcolor: neutral[100],
                          color: neutral[300],
                        },
                      }}
                    >
                      {isLoading
                        ? <CircularProgress size={18} sx={{ color: neutral[400] }} />
                        : <Send size={18} />
                      }
                    </IconButton>
                  </Stack>
                </InputAdornment>
              ),
              sx: {
                borderRadius: `${radius.card}px`,
                bgcolor: (t) => t.palette.mode === 'light' ? neutral.white : 'rgba(255,255,255,0.04)',
                px: 2,
                py: 1.5,
                boxShadow: shadows.card,
                '& fieldset': { 
                  border: `1px solid ${neutral[200]}`,
                  transition: 'border-color 200ms ease',
                },
                '&:hover fieldset': { borderColor: brand.orangeLight },
                '&.Mui-focused fieldset': { borderColor: brand.orange, borderWidth: '1.5px' },
                alignItems: 'flex-start',
              },
            },
          }}
        />
      </Box>
    </Box>
  );
}
