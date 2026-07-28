// src/components/chat/ChatConversation.tsx
import { useEffect, useRef } from 'react';
import { Box, Stack, Typography, Avatar } from '@mui/material';
import { SmartToy } from '@mui/icons-material';
import type { ChatMessage } from '@/types/chat';
import { ChatMessageItem } from './ChatMessageItem';

interface ChatConversationProps {
  conversation: ChatMessage[];
  isThinking: boolean;
}

export function ChatConversation({ conversation, isThinking }: ChatConversationProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const isNearBottom = useRef(true);

  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    // Check if user is within 100px of the bottom
    isNearBottom.current = el.scrollHeight - el.scrollTop - el.clientHeight < 100;
  };

  useEffect(() => {
    if (isNearBottom.current && scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [conversation, isThinking]);

  return (
    <Box
      ref={scrollRef}
      onScroll={handleScroll}
      sx={{
        flexGrow: 1,
        overflowY: 'auto',
        p: 3,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Stack spacing={2} sx={{ flexGrow: 1 }}>
        {conversation.map((msg) => (
          <ChatMessageItem key={msg.id} message={msg} />
        ))}

        {isThinking && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 3 }}>
            <Stack direction="row" spacing={2} sx={{ alignItems: 'flex-start' }}>
              <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                <SmartToy sx={{ fontSize: 20 }} />
              </Avatar>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'background.paper',
                  boxShadow: 2,
                }}
              >
                <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                  Thinking...
                </Typography>
              </Box>
            </Stack>
          </Box>
        )}
      </Stack>
    </Box>
  );
}
