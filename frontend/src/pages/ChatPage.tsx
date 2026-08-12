// src/pages/ChatPage.tsx
import { useState } from 'react';
import {
  Box, Typography, Stack, Card, CardActionArea, IconButton, Tooltip, Chip,
} from '@mui/material';
import {
  Trash2, Brain, BarChart3, TrendingUp, FileText,
  GitCompare, Calendar, Sparkles,
} from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { queryApi } from '@/api/queryApi';
import type { ChatMessage } from '@/types/chat';
import { ChatConversation } from '@/components/chat/ChatConversation';
import { ChatInput } from '@/components/chat/ChatInput';
import { brand, neutral } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

// ── Suggested prompts ─────────────────────────────────────────────────────────

const PROMPTS = [
  {
    icon: <FileText size={18} />,
    title: 'Summarize Reports',
    text: 'Provide a comprehensive summary of all uploaded business reports.',
    color: brand.orange,
    bg: brand.orangeSubtle,
  },
  {
    icon: <TrendingUp size={18} />,
    title: 'Revenue Trends',
    text: 'What are the revenue trends over the past six months?',
    color: '#3B82F6',
    bg: '#EFF6FF',
  },
  {
    icon: <BarChart3 size={18} />,
    title: 'Business Performance',
    text: 'Analyze overall business performance and identify key metrics.',
    color: '#8B5CF6',
    bg: '#F5F3FF',
  },
  {
    icon: <Sparkles size={18} />,
    title: 'Executive Summary',
    text: 'Generate an executive summary suitable for a board presentation.',
    color: '#10B981',
    bg: '#F0FDF4',
  },
  {
    icon: <Calendar size={18} />,
    title: 'Sales Forecast',
    text: 'Forecast next month\'s sales based on historical data.',
    color: '#F59E0B',
    bg: '#FFFBEB',
  },
  {
    icon: <GitCompare size={18} />,
    title: 'Compare Branches',
    text: 'Compare performance across different branches or locations.',
    color: '#EF4444',
    bg: '#FEF2F2',
  },
] as const;

// ── Welcome / Landing screen ──────────────────────────────────────────────────

interface WelcomeScreenProps {
  onPrompt: (text: string) => void;
}

function WelcomeScreen({ onPrompt }: WelcomeScreenProps) {
  return (
    <Box
      sx={{
        flexGrow: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-start',
        px: 3,
        py: { xs: 4, md: 8 },
        overflowY: 'auto',
      }}
    >
      <Box sx={{ margin: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', maxWidth: 840 }}>
      {/* Brand icon + heading */}
      <Stack sx={{ alignItems: 'center', mb: 5 }}>
        <Box
          sx={{
            width: 72,
            height: 72,
            borderRadius: `${radius.card}px`,
            background: `linear-gradient(135deg, ${brand.orange}, ${brand.orangeDark})`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 12px 32px ${brand.orange}40`,
            mb: 3,
          }}
        >
          <Brain size={36} color="#fff" />
        </Box>

        <Typography
          variant="h2"
          sx={{ fontWeight: 800, letterSpacing: '-0.03em', mb: 0.75, textAlign: 'center' }}
        >
          GROVIT AI
        </Typography>

        <Chip
          label="Digital CEO for Modern Businesses"
          size="small"
          sx={{
            bgcolor: brand.orangeSubtle,
            color: brand.orange,
            fontWeight: 700,
            fontSize: '0.75rem',
            borderRadius: `${radius.full}px`,
            border: `1px solid ${brand.orange}33`,
            mb: 2.5,
            px: 1,
          }}
        />

        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ textAlign: 'center', maxWidth: 480, lineHeight: 1.7 }}
        >
          Ask questions about your uploaded business reports, generate insights,
          forecast performance, and analyze operational data.
        </Typography>
      </Stack>

      {/* Prompt cards grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
          gap: 2,
          width: '100%',
          maxWidth: 840,
        }}
      >
        {PROMPTS.map((prompt, idx) => (
          <Card
            key={idx}
            elevation={0}
            sx={{
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
            <CardActionArea
              onClick={() => onPrompt(prompt.text)}
              sx={{
                p: 2.5,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                justifyContent: 'flex-start',
                borderRadius: `${radius.card}px`,
              }}
            >
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: `${radius.chip}px`,
                  bgcolor: prompt.bg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: prompt.color,
                  mb: 1.75,
                  flexShrink: 0,
                }}
              >
                {prompt.icon}
              </Box>
              <Typography variant="body2" sx={{ fontWeight: 700, mb: 0.5, color: 'text.primary' }}>
                {prompt.title}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.5 }}>
                {prompt.text}
              </Typography>
            </CardActionArea>
          </Card>
        ))}
      </Box>

      <Typography variant="caption" color="text.disabled" sx={{ mt: 4, textAlign: 'center' }}>
        Press <strong>Enter</strong> to send · <strong>Shift+Enter</strong> for a new line
      </Typography>
      </Box>
    </Box>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────────

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

  const hasMessages = conversation.length > 0;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 64px - 64px)',
        minHeight: 500,
      }}
    >
      {/* ── Page header bar ──────────────────────────────────────────────── */}
      <Stack
        direction="row"
        sx={{
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 2,
          flexShrink: 0,
        }}
      >
        <Box>
          <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: '-0.02em' }}>
            AI Chat
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {hasMessages
              ? `${conversation.length} message${conversation.length !== 1 ? 's' : ''} · Session active`
              : 'Enterprise AI assistant powered by your business data'}
          </Typography>
        </Box>

        {hasMessages && (
          <Tooltip title="Clear conversation" placement="left">
            <IconButton
              onClick={handleClear}
              size="small"
              sx={{
                color: 'text.secondary',
                bgcolor: (t) => t.palette.mode === 'light' ? neutral[100] : 'rgba(255,255,255,0.07)',
                borderRadius: `${radius.chip}px`,
                '&:hover': { bgcolor: 'error.main', color: '#fff' },
                transition: 'all 200ms ease',
              }}
            >
              <Trash2 size={16} />
            </IconButton>
          </Tooltip>
        )}
      </Stack>

      {/* ── Chat card ────────────────────────────────────────────────────── */}
      <Card
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          borderRadius: `${radius.card}px`,
          boxShadow: shadows.card,
          border: 'none',
          minHeight: 0,
        }}
      >
        {/* Conversation or landing screen */}
        {hasMessages ? (
          <ChatConversation
            conversation={conversation}
            isThinking={queryMutation.isPending}
          />
        ) : (
          <WelcomeScreen onPrompt={handleSend} />
        )}

        {/* Sticky input */}
        <ChatInput onSend={handleSend} isLoading={queryMutation.isPending} />
      </Card>
    </Box>
  );
}
