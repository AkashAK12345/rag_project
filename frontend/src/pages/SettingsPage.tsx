// src/pages/SettingsPage.tsx
import { useState } from 'react';
import { 
  Box, Typography, Card, CardContent, Divider, Stack, Grid, 
  Button, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions,
  Switch, CircularProgress, IconButton, List, ListItem, ListItemText, ListItemIcon, alpha
} from '@mui/material';
import { 
  Settings, Moon, Sun, User, BrainCircuit, LogOut, Info, Code, RefreshCw, Key
} from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { StatusChip } from '@/components/common/StatusChip';
import { ErrorState } from '@/components/common/ErrorState';
import { useAuthContext } from '@/store/authStore';
import { useThemeContext } from '@/store/themeStore';
import { useModelConfigs, useSystemHealth } from '@/hooks/useSystem';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

// --- Reusable Layout Components ---
const SectionTitle = ({ title, icon }: { title: string, icon: React.ReactNode }) => (
  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 1.5 }}>
    <Box sx={{ 
      p: 0.75, 
      borderRadius: `${radius.chip}px`, 
      bgcolor: (t) => alpha(t.palette.primary.main, 0.1), 
      color: 'primary.main',
      display: 'flex'
    }}>
      {icon}
    </Box>
    <Typography variant="h6" sx={{ fontWeight: 800, letterSpacing: '-0.01em' }}>{title}</Typography>
  </Box>
);

const SectionItem = ({ label, value, loading = false }: { label: string, value: React.ReactNode, loading?: boolean }) => (
  <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
    <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>{label}</Typography>
    {loading ? <CircularProgress size={16} /> : (
      typeof value === 'string' ? (
        <Typography variant="body2" sx={{ fontWeight: 700 }}>{value}</Typography>
      ) : value
    )}
  </Stack>
);

const SectionCard = ({ children }: { children: React.ReactNode }) => (
  <Card 
    elevation={0}
    sx={{ 
      height: '100%', 
      mb: 3,
      borderRadius: `${radius.card}px`,
      boxShadow: shadows.card,
      border: 'none'
    }}
  >
    <CardContent sx={{ p: { xs: 3, md: 4 } }}>
      {children}
    </CardContent>
  </Card>
);

// --- Individual Sections ---

const AppearanceSection = () => {
  const { mode, toggleTheme } = useThemeContext();

  return (
    <SectionCard>
      <SectionTitle title="Appearance" icon={<Settings size={20} />} />
      <Stack spacing={2} divider={<Divider sx={{ opacity: 0.6 }} />}>
        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            {mode === 'dark' ? <Moon size={18} /> : <Sun size={18} />}
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {mode === 'dark' ? 'Dark Mode' : 'Light Mode'}
            </Typography>
          </Box>
          <Switch checked={mode === 'dark'} onChange={toggleTheme} color="primary" />
        </Stack>
      </Stack>
    </SectionCard>
  );
};

const UserInfoSection = () => {
  const { user, isAuthenticated } = useAuthContext();

  return (
    <SectionCard>
      <SectionTitle title="User Information" icon={<User size={20} />} />
      <Stack spacing={2} divider={<Divider sx={{ opacity: 0.6 }} />}>
        <SectionItem label="Username" value={user?.username || 'N/A'} />
        <SectionItem label="Role" value={user?.role || 'N/A'} />
        <SectionItem 
          label="Authentication Status" 
          value={<StatusChip status={isAuthenticated ? 'ok' : 'error'} size="small" />} 
        />
      </Stack>
    </SectionCard>
  );
};

const AIConfigSection = () => {
  const { data: models, isLoading, isError, refetch } = useModelConfigs();

  return (
    <SectionCard>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <SectionTitle title="AI Configuration" icon={<BrainCircuit size={20} />} />
        {isError && (
          <IconButton size="small" onClick={() => refetch()} disabled={isLoading} title="Retry">
            <RefreshCw size={16} />
          </IconButton>
        )}
      </Box>
      <Typography variant="caption" color="primary.main" sx={{ display: 'block', mb: 2.5, mt: -2, fontWeight: 600 }}>
        READ ONLY
      </Typography>
      {isError ? (
        <ErrorState title="Load Error" message="Failed to load AI Configuration." onRetry={refetch} />
      ) : (
        <Stack spacing={2} divider={<Divider sx={{ opacity: 0.6 }} />}>
          <SectionItem label="Active LLM" value={models?.llm_model || 'N/A'} loading={isLoading} />
          <SectionItem label="Embedding Model" value={models?.embedding_model || 'N/A'} loading={isLoading} />
          <SectionItem label="Provider" value={models?.llm_provider || 'N/A'} loading={isLoading} />
          <SectionItem label="Vector Store Type" value={models?.vector_store_type || 'N/A'} loading={isLoading} />
        </Stack>
      )}
    </SectionCard>
  );
};

const AppInfoSection = () => {
  const { data: health, isLoading, isError, refetch } = useSystemHealth();
  const apiBaseUrl = import.meta.env.VITE_API_URL || '/api/v1';
  const mode = import.meta.env.MODE;

  return (
    <SectionCard>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <SectionTitle title="Application Information" icon={<Code size={20} />} />
        {isError && (
          <IconButton size="small" onClick={() => refetch()} disabled={isLoading} title="Retry">
            <RefreshCw size={16} />
          </IconButton>
        )}
      </Box>
      {isError ? (
        <ErrorState title="Load Error" message="Failed to load Application Information." onRetry={refetch} />
      ) : (
        <Stack spacing={2} divider={<Divider sx={{ opacity: 0.6 }} />}>
          <SectionItem label="Backend Version" value={health?.version || 'N/A'} loading={isLoading} />
          <SectionItem label="Environment" value={mode} />
          <SectionItem label="API Base URL" value={apiBaseUrl} />
          <SectionItem label="Build Mode" value={mode === 'development' ? 'Development' : 'Production'} />
        </Stack>
      )}
    </SectionCard>
  );
};

const SessionSection = () => {
  const { logout } = useAuthContext();
  const [open, setOpen] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);
  const handleLogout = () => {
    setOpen(false);
    logout();
  };

  return (
    <SectionCard>
      <SectionTitle title="Session" icon={<Key size={20} />} />
      <Box sx={{ mt: 1 }}>
        <Button 
          variant="outlined" 
          color="error" 
          startIcon={<LogOut size={16} />} 
          onClick={handleOpen}
          fullWidth
          sx={{ py: 1.25, fontWeight: 700, borderRadius: `${radius.button}px` }}
        >
          Logout
        </Button>
      </Box>

      <Dialog 
        open={open} 
        onClose={handleClose} 
        maxWidth="xs" 
        fullWidth
        slotProps={{
          paper: { sx: { borderRadius: `${radius.card}px`, boxShadow: shadows.card, border: 'none' } }
        }}
      >
        <DialogTitle sx={{ fontWeight: 800 }}>Logout</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to end your current session?
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button onClick={handleClose} color="inherit" sx={{ fontWeight: 600, borderRadius: `${radius.button}px` }}>
            Cancel
          </Button>
          <Button onClick={handleLogout} color="error" variant="contained" sx={{ fontWeight: 700, borderRadius: `${radius.button}px`, px: 3 }}>
            Logout
          </Button>
        </DialogActions>
      </Dialog>
    </SectionCard>
  );
};

const AboutSection = () => {
  const { data: health } = useSystemHealth();
  
  return (
    <SectionCard>
      <SectionTitle title="About" icon={<Info size={20} />} />
      <Stack spacing={3}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 800, color: 'primary.main', letterSpacing: '-0.02em' }}>
            GROVIT AI
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            Enterprise Business Intelligence
          </Typography>
        </Box>

        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Frontend</Typography>
          <List dense disablePadding>
            {['React', 'TypeScript', 'Material UI'].map(tech => (
              <ListItem key={tech} disablePadding sx={{ py: 0.25 }}>
                <ListItemIcon sx={{ minWidth: 24, color: 'text.secondary' }}>•</ListItemIcon>
                <ListItemText primary={<Typography variant="body2" sx={{ fontWeight: 500 }}>{tech}</Typography>} />
              </ListItem>
            ))}
          </List>
        </Box>

        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Backend</Typography>
          <List dense disablePadding>
            {['FastAPI'].map(tech => (
              <ListItem key={tech} disablePadding sx={{ py: 0.25 }}>
                <ListItemIcon sx={{ minWidth: 24, color: 'text.secondary' }}>•</ListItemIcon>
                <ListItemText primary={<Typography variant="body2" sx={{ fontWeight: 500 }}>{tech}</Typography>} />
              </ListItem>
            ))}
          </List>
        </Box>

        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>AI Stack</Typography>
          <List dense disablePadding>
            {['LlamaIndex', 'Ollama'].map(tech => (
              <ListItem key={tech} disablePadding sx={{ py: 0.25 }}>
                <ListItemIcon sx={{ minWidth: 24, color: 'text.secondary' }}>•</ListItemIcon>
                <ListItemText primary={<Typography variant="body2" sx={{ fontWeight: 500 }}>{tech}</Typography>} />
              </ListItem>
            ))}
          </List>
        </Box>

        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Embeddings</Typography>
          <List dense disablePadding>
            {['BAAI/bge-small-en-v1.5'].map(tech => (
              <ListItem key={tech} disablePadding sx={{ py: 0.25 }}>
                <ListItemIcon sx={{ minWidth: 24, color: 'text.secondary' }}>•</ListItemIcon>
                <ListItemText primary={<Typography variant="body2" sx={{ fontWeight: 500 }}>{tech}</Typography>} />
              </ListItem>
            ))}
          </List>
        </Box>

        <Divider sx={{ opacity: 0.6 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
            Version {health?.version || '1.0.0'}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
            © {new Date().getFullYear()} GROVIT AI
          </Typography>
        </Box>
      </Stack>
    </SectionCard>
  );
};

// --- Main Page ---

export function SettingsPage() {
  return (
    <Box>
      <PageHeader
        title="Settings"
        subtitle="Manage your application preferences and view system configurations."
      />

      <Grid container spacing={4}>
        {/* Left Column */}
        <Grid size={{ xs: 12, md: 6 }}>
          <AppearanceSection />
          <UserInfoSection />
          <SessionSection />
        </Grid>

        {/* Right Column */}
        <Grid size={{ xs: 12, md: 6 }}>
          <AIConfigSection />
          <AppInfoSection />
          <AboutSection />
        </Grid>
      </Grid>
    </Box>
  );
}
