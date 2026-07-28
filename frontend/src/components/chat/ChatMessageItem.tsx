// src/components/chat/ChatMessageItem.tsx
import { useState } from 'react';
import { Box, Typography, Stack, IconButton, Tooltip, Avatar, Snackbar } from '@mui/material';
import { ContentCopy, Person, SmartToy } from '@mui/icons-material';
import type { ChatMessage } from '@/types/chat';
import { SourceDocuments } from '../common/SourceDocuments';
import { ResponseMetadata } from '../common/ResponseMetadata';

interface ChatMessageItemProps {
  message: ChatMessage;
}

export function ChatMessageItem({ message }: ChatMessageItemProps) {
  const isUser = message.role === 'user';
  const [copyOpen, setCopyOpen] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopyOpen(true);
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', mb: 3 }}>
      <Stack
        direction={isUser ? 'row-reverse' : 'row'}
        spacing={2}
        sx={{ maxWidth: '85%', alignItems: 'flex-start' }}
      >
        <Avatar
          sx={{
            bgcolor: isUser ? 'primary.main' : 'secondary.main',
            width: 32,
            height: 32,
          }}
        >
          {isUser ? <Person sx={{ fontSize: 20 }} /> : <SmartToy sx={{ fontSize: 20 }} />}
        </Avatar>

        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            bgcolor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary',
            boxShadow: isUser ? 1 : 2,
            position: 'relative',
            '&:hover .copy-btn': { opacity: 1 },
          }}
        >
          {message.isError ? (
            <Typography variant="body2" color="error">
              {message.text}
            </Typography>
          ) : (
            <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}>
              {message.text}
            </Typography>
          )}

          {!isUser && !message.isError && (
            <IconButton
              size="small"
              className="copy-btn"
              onClick={handleCopy}
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                opacity: 0,
                transition: 'opacity 0.2s',
                color: 'text.secondary',
              }}
            >
              <Tooltip title="Copy response">
                <ContentCopy sx={{ fontSize: 16 }} />
              </Tooltip>
            </IconButton>
          )}

          {message.sources && message.sources.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <SourceDocuments sources={message.sources} />
            </Box>
          )}

          {message.metadata && (
            <Box sx={{ mt: 1.5 }}>
              <ResponseMetadata metadata={message.metadata} />
            </Box>
          )}
        </Box>
      </Stack>

      <Snackbar
        open={copyOpen}
        autoHideDuration={2000}
        onClose={() => setCopyOpen(false)}
        message="Response copied to clipboard"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
}
