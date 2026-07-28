// src/pages/ChatPage.tsx
import { useState } from 'react';
import { Box, Typography, Stack, Card, CardActionArea, IconButton, Tooltip, Avatar } from '@mui/material';
import { DeleteOutlined, SmartToy, TrendingUp, Summarize, AttachMoney } from '@mui/icons-material';
import { useMutation } from '@tanstack/react-query';
import { queryApi } from '@/api/queryApi';
import type { ChatMessage } from '@/types/chat';
import { ChatConversation } from '@/components/chat/ChatConversation';
import { ChatInput } from '@/components/chat/ChatInput';

const EXAMPLE_PROMPTS = [
  { icon: <Summarize color="primary" />, text: "Provide a comprehensive KPI summary for the business." },
  { icon: <TrendingUp color="primary" />, text: "What is our revenue trend over the past six months?" },
  { icon: <AttachMoney color="primary" />, text: "Analyze food costs versus sales volume." },
];

export function ChatPage() {
  const [conversation, setConversation] = useState<ChatMessage[]>([]);

  const queryMutation = useMutation({
    mutationFn: queryApi.query,
    onSuccess: (data) => {
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: data.answer,
        sources: data.sources,
        metadata: data.metadata,
      };
      setConversation((prev) => [...prev, assistantMessage]);
    },
    onError: (error) => {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: 'An error occurred while communicating with the AI. Please try again.',
        isError: true,
      };
      setConversation((prev) => [...prev, errorMessage]);
      console.error('Chat error:', error);
    },
  });

  const handleSend = (text: string) => {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      text,
    };
    setConversation((prev) => [...prev, userMessage]);
    queryMutation.mutate({ question: text });
  };

  const handleClear = () => {
    setConversation([]);
    queryMutation.reset();
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px - 48px)' }}>
      {/* Header */}
      <Stack
        direction="row"
        sx={{
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
          flexShrink: 0,
        }}
      >
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          AI Chat
        </Typography>
        {conversation.length > 0 && (
          <Tooltip title="Clear conversation">
            <IconButton onClick={handleClear} color="error" size="small" sx={{ bgcolor: 'error.lighter' }}>
              <DeleteOutlined />
            </IconButton>
          </Tooltip>
        )}
      </Stack>

      {/* Main Chat Area */}
      <Card
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          borderRadius: 3,
        }}
      >
        {conversation.length === 0 ? (
          <Box
            sx={{
              flexGrow: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              p: 4,
            }}
          >
            <Avatar sx={{ bgcolor: 'primary.main', width: 64, height: 64, mb: 3 }}>
              <SmartToy sx={{ fontSize: 40 }} />
            </Avatar>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
              How can I help you today?
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 6, textAlign: 'center', maxWidth: 500 }}>
              Ask me anything about your uploaded business data. I can provide summaries, analyze trends, and answer specific questions.
            </Typography>
            
            <Stack direction="row" spacing={2} sx={{ width: '100%', maxWidth: 800, flexWrap: 'wrap', justifyContent: 'center' }}>
              {EXAMPLE_PROMPTS.map((prompt, idx) => (
                <Card key={idx} variant="outlined" sx={{ width: 240, borderRadius: 2, mb: 2 }}>
                  <CardActionArea onClick={() => handleSend(prompt.text)} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-start' }}>
                    <Box sx={{ mb: 1.5 }}>{prompt.icon}</Box>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {prompt.text}
                    </Typography>
                  </CardActionArea>
                </Card>
              ))}
            </Stack>
          </Box>
        ) : (
          <ChatConversation conversation={conversation} isThinking={queryMutation.isPending} />
        )}

        <ChatInput onSend={handleSend} isLoading={queryMutation.isPending} />
      </Card>
    </Box>
  );
}
