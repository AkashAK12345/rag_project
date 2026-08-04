// src/components/chat/ChatMessageItem.tsx
import { useState } from 'react';
import {
  Box, Typography, Stack, IconButton, Tooltip, Avatar,
  Snackbar, Collapse, Chip,
} from '@mui/material';
import { Copy, Check, User, Bot, ChevronDown, FileSpreadsheet, Zap, BrainCircuit, FileSearch } from 'lucide-react';
import type { ChatMessage } from '@/types/chat';
import { brand, neutral, semantic } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

// ── Inline source cards ───────────────────────────────────────────────────────

interface SourceCardsProps {
  sources: ChatMessage['sources'];
}

function SourceCards({ sources }: SourceCardsProps) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <Box sx={{ mt: 2.5, pt: 2, borderTop: '1px solid rgba(0,0,0,0.06)' }}>
      {/* Toggle row */}
      <Stack
        direction="row"
        sx={{ alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', mb: expanded ? 1.5 : 0 }}
        onClick={() => setExpanded((p) => !p)}
      >
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
          <FileSearch size={13} color={neutral[400]} />
          <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
            {sources.length} source{sources.length !== 1 ? 's' : ''} retrieved
          </Typography>
        </Stack>
        <IconButton size="small" tabIndex={-1} sx={{ p: 0.25, color: 'text.disabled' }}>
          <ChevronDown
            size={14}
            style={{
              transition: 'transform 200ms ease',
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            }}
          />
        </IconButton>
      </Stack>

      <Collapse in={expanded} timeout="auto">
        <Stack spacing={1.25}>
          {sources.map((src, idx) => (
            <Box
              key={idx}
              sx={{
                p: 1.75,
                borderRadius: `${radius.chip}px`,
                bgcolor: neutral[50],
                border: `1px solid ${neutral[100]}`,
                transition: 'border-color 150ms ease',
                '&:hover': { borderColor: `${brand.orange}55` },
              }}
            >
              <Stack direction="row" sx={{ alignItems: 'flex-start', gap: 1.5 }}>
                {/* File icon */}
                <Box
                  sx={{
                    width: 34,
                    height: 34,
                    borderRadius: `${radius.chip}px`,
                    bgcolor: brand.orangeSubtle,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: brand.orange,
                    flexShrink: 0,
                  }}
                >
                  <FileSpreadsheet size={16} />
                </Box>

                {/* File metadata */}
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 0.25, gap: 1 }}>
                    <Typography variant="caption" sx={{ fontWeight: 700, color: 'text.primary' }} noWrap>
                      {src.file}
                    </Typography>
                    <Chip
                      label={`${(src.score * 100).toFixed(0)}% match`}
                      size="small"
                      sx={{
                        height: 18,
                        fontSize: '0.6rem',
                        fontWeight: 700,
                        flexShrink: 0,
                        bgcolor: src.score >= 0.8 ? semantic.successSubtle : brand.orangeSubtle,
                        color: src.score >= 0.8 ? semantic.successDark : brand.orange,
                        border: `1px solid ${src.score >= 0.8 ? semantic.success : brand.orange}33`,
                        borderRadius: `${radius.full}px`,
                      }}
                    />
                  </Stack>
                  {src.sheet && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.75 }}>
                      Sheet: {src.sheet}
                    </Typography>
                  )}
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ display: 'block', lineHeight: 1.55, fontStyle: 'italic' }}
                  >
                    {src.preview}
                  </Typography>
                </Box>
              </Stack>
            </Box>
          ))}
        </Stack>
      </Collapse>
    </Box>
  );
}

// ── Inline metadata row ───────────────────────────────────────────────────────

interface MetadataRowProps {
  metadata: NonNullable<ChatMessage['metadata']>;
}

function MetadataRow({ metadata }: MetadataRowProps) {
  const chips = [
    { icon: <Zap size={10} />, label: `${Math.round(metadata.latency_ms)}ms` },
    { icon: <BrainCircuit size={10} />, label: metadata.model },
    { icon: <FileSearch size={10} />, label: `${metadata.retrieved_documents} docs` },
  ];

  return (
    <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: 'wrap', gap: 0.75 }}>
      {chips.map((chip, i) => (
        <Stack key={i} direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
          <Box sx={{ color: 'text.disabled', display: 'flex' }}>{chip.icon}</Box>
          <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 500 }}>
            {chip.label}
          </Typography>
        </Stack>
      ))}
    </Stack>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

interface ChatMessageItemProps {
  message: ChatMessage;
}

export function ChatMessageItem({ message }: ChatMessageItemProps) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', mb: 3 }}>
      <Stack
        direction={isUser ? 'row-reverse' : 'row'}
        spacing={1.5}
        sx={{ maxWidth: { xs: '90%', sm: '80%', md: '75%' }, alignItems: 'flex-end' }}
      >
        {/* Avatar */}
        <Avatar
          sx={{
            width: 34,
            height: 34,
            flexShrink: 0,
            borderRadius: `${radius.chip}px`,
            bgcolor: isUser ? brand.orange : neutral[100],
            boxShadow: isUser ? `0 4px 12px ${brand.orange}40` : 'none',
            '& svg': { color: isUser ? neutral.white : neutral[500] },
          }}
        >
          {isUser ? <User size={16} /> : <Bot size={16} />}
        </Avatar>

        {/* Bubble */}
        <Box
          sx={{
            position: 'relative',
            px: isUser ? 2.5 : 3,
            py: isUser ? 2 : 2.5,
            borderRadius: isUser
              ? `${radius.card}px ${radius.card}px 6px ${radius.card}px`
              : `${radius.card}px ${radius.card}px ${radius.card}px 6px`,
            bgcolor: isUser ? brand.orange : 'background.paper',
            color: isUser ? neutral.white : 'text.primary',
            boxShadow: isUser
              ? `0 4px 16px ${brand.orange}45`
              : shadows.card,
            '&:hover .copy-btn': { opacity: 1 },
          }}
        >
          {/* Message text */}
          {message.isError ? (
            <Typography
              variant="body2"
              sx={{
                color: isUser ? neutral.white : 'error.main',
                lineHeight: 1.75,
                fontStyle: 'italic',
              }}
            >
              {message.text}
            </Typography>
          ) : (
            <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
              {message.text}
            </Typography>
          )}

          {/* Copy button — assistant messages only */}
          {!isUser && !message.isError && (
            <Tooltip title={copied ? 'Copied!' : 'Copy response'} placement="top">
              <IconButton
                size="small"
                className="copy-btn"
                onClick={handleCopy}
                sx={{
                  position: 'absolute',
                  top: 10,
                  right: 10,
                  opacity: 0,
                  transition: 'opacity 200ms ease, background 150ms ease',
                  borderRadius: `${radius.chip}px`,
                  p: 0.75,
                  bgcolor: copied ? semantic.successSubtle : neutral[100],
                  color: copied ? semantic.success : neutral[500],
                  '&:hover': {
                    bgcolor: copied ? semantic.successSubtle : neutral[200],
                  },
                }}
              >
                {copied ? <Check size={13} /> : <Copy size={13} />}
              </IconButton>
            </Tooltip>
          )}

          {/* Sources as premium cards (assistant only) */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <SourceCards sources={message.sources} />
          )}

          {/* Metadata (assistant only) */}
          {!isUser && message.metadata && (
            <Box
              sx={{
                mt: 2,
                pt: 1.5,
                borderTop: `1px solid ${neutral[100]}`,
              }}
            >
              <MetadataRow metadata={message.metadata} />
            </Box>
          )}
        </Box>
      </Stack>

      {/* Snackbar is no longer needed since we use tooltip, but keep for accessibility */}
      <Snackbar
        open={copied}
        autoHideDuration={2000}
        onClose={() => setCopied(false)}
        message="Copied to clipboard"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
}
