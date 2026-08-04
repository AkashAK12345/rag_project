// src/components/chat/ChatConversation.tsx
import { useEffect, useRef } from 'react';
import { Box, Stack, Avatar } from '@mui/material';
import { Bot } from 'lucide-react';
import type { ChatMessage } from '@/types/chat';
import { ChatMessageItem } from './ChatMessageItem';
import { brand, neutral } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

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
        px: { xs: 2, md: 5 },
        py: 4,
        display: 'flex',
        flexDirection: 'column',
        '&::-webkit-scrollbar': { width: 6 },
        '&::-webkit-scrollbar-track': { bgcolor: 'transparent' },
        '&::-webkit-scrollbar-thumb': { bgcolor: neutral[200], borderRadius: `${radius.full}px` },
      }}
    >
      <Stack spacing={0} sx={{ flexGrow: 1 }}>
        {conversation.map((msg) => (
          <ChatMessageItem key={msg.id} message={msg} />
        ))}

        {/* Thinking indicator */}
        {isThinking && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 3 }}>
            <Stack direction="row" spacing={1.5} sx={{ alignItems: 'flex-end', maxWidth: { xs: '90%', sm: '80%', md: '75%' } }}>
              <Avatar
                sx={{
                  bgcolor: neutral[100],
                  width: 34,
                  height: 34,
                  borderRadius: `${radius.chip}px`,
                  flexShrink: 0,
                  '& svg': { color: neutral[500] }
                }}
              >
                <Bot size={16} />
              </Avatar>
              <Box
                sx={{
                  px: 3,
                  py: 2.5,
                  borderRadius: `${radius.card}px ${radius.card}px ${radius.card}px 6px`,
                  bgcolor: 'background.paper',
                  boxShadow: shadows.card,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  minHeight: 52,
                }}
              >
                {[0, 1, 2].map((i) => (
                  <Box
                    key={i}
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      bgcolor: brand.orange,
                      animation: 'pulse 1.4s ease-in-out infinite both',
                      animationDelay: `${i * 0.16}s`,
                      '@keyframes pulse': {
                        '0%, 80%, 100%': { transform: 'scale(0.6)', opacity: 0.4 },
                        '40%': { transform: 'scale(1)', opacity: 1 },
                      },
                    }}
                  />
                ))}
              </Box>
            </Stack>
          </Box>
        )}
      </Stack>
    </Box>
  );
}
