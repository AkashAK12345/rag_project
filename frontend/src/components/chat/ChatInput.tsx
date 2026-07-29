// src/components/chat/ChatInput.tsx
import { useState, KeyboardEvent } from 'react';
import { Box, TextField, IconButton, InputAdornment, CircularProgress } from '@mui/material';
import { Send } from '@mui/icons-material';

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
    <Box sx={{ p: 2, bgcolor: 'background.paper', borderTop: (t) => `1px solid ${t.palette.divider}` }}>
      <TextField
        variant="outlined"
        fullWidth
        multiline
        maxRows={4}
        placeholder="Ask a question about your business data..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
        slotProps={{
          input: {
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  color="primary"
                  onClick={handleSend}
                  disabled={!value.trim() || isLoading}
                  edge="end"
                >
                  {isLoading ? <CircularProgress size={24} color="inherit" /> : <Send />}
                </IconButton>
              </InputAdornment>
            ),
            sx: {
              borderRadius: 3,
              bgcolor: 'action.hover',
              '& fieldset': { border: 'none' },
            },
          },
        }}
      />
    </Box>
  );
}
