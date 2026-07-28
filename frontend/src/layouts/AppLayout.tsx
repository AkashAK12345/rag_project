// src/layouts/AppLayout.tsx
import { useState, type ReactNode } from 'react';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import {
  Box, Drawer, AppBar, Toolbar, Typography, IconButton, Tooltip,
  List, ListItemButton, ListItemIcon, ListItemText, Divider, Avatar,
  Stack, Chip, useTheme, Menu, MenuItem,
} from '@mui/material';
import {
  Menu as MenuIcon, ChevronLeft, Dashboard, CloudUpload,
  Chat, Analytics, TrendingUp, MonitorHeart, Settings,
  Brightness4, Brightness7, Logout, Psychology, Person,
} from '@mui/icons-material';
import { SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH } from '@/theme';
import { useAuthContext } from '@/store/authStore';
import { useThemeContext } from '@/store/themeStore';
import { authApi } from '@/api/authApi';

interface NavItem { label: string; icon: ReactNode; path: string }

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard',      icon: <Dashboard />,    path: '/' },
  { label: 'Upload Reports', icon: <CloudUpload />,   path: '/upload' },
  { label: 'AI Chat',        icon: <Chat />,          path: '/chat' },
  { label: 'Analytics',      icon: <Analytics />,     path: '/analytics' },
  { label: 'Forecasting',    icon: <TrendingUp />,    path: '/forecasting' },
  { label: 'Health',         icon: <MonitorHeart />,  path: '/health' },
  { label: 'Settings',       icon: <Settings />,      path: '/settings' },
];

interface Props { children: ReactNode }

export function AppLayout({ children }: Props) {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthContext();
  const { mode, toggleTheme } = useThemeContext();
  const [collapsed, setCollapsed] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const drawerWidth = collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH;

  const handleLogout = async () => {
    try { await authApi.logout(); } catch { /* stateless */ }
    logout();
    navigate('/login', { replace: true });
  };

  const isActive = (path: string) =>
    path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* ── Sidebar ─────────────────────────────────────────────────────── */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          transition: theme.transitions.create('width'),
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            overflowX: 'hidden',
            transition: theme.transitions.create('width'),
            borderRight: `1px solid ${theme.palette.divider}`,
            bgcolor: 'background.paper',
            display: 'flex',
            flexDirection: 'column',
          },
        }}
      >
        {/* Logo */}
        <Toolbar
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'space-between',
            px: collapsed ? 1 : 2,
            minHeight: 64,
          }}
        >
          <Stack
            direction="row"
            sx={{ alignItems: 'center', gap: 1.5, overflow: 'hidden', flexGrow: 1 }}
          >
            <Box
              sx={{
                width: 34, height: 34, borderRadius: 1.5, flexShrink: 0,
                background: 'linear-gradient(135deg, #6366F1, #0EA5E9)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}
            >
              <Psychology sx={{ color: '#fff', fontSize: 20 }} />
            </Box>
            {!collapsed && (
              <Typography variant="h6" noWrap sx={{ fontWeight: 700 }}>
                RAG Analytics
              </Typography>
            )}
          </Stack>
          {!collapsed && (
            <IconButton size="small" onClick={() => setCollapsed(true)}>
              <ChevronLeft fontSize="small" />
            </IconButton>
          )}
        </Toolbar>

        <Divider />

        {/* Nav items */}
        <List sx={{ px: 0, py: 1, flexGrow: 1 }}>
          {NAV_ITEMS.map((item) => {
            const active = isActive(item.path);
            return (
              <Tooltip key={item.path} title={collapsed ? item.label : ''}>
                <ListItemButton
                  component={RouterLink}
                  to={item.path}
                  selected={active}
                  sx={{
                    mx: 1, borderRadius: 2, mb: 0.5,
                    justifyContent: collapsed ? 'center' : 'flex-start',
                    '&.Mui-selected': {
                      bgcolor: 'primary.main', color: '#fff',
                      '& .MuiListItemIcon-root': { color: '#fff' },
                      '&:hover': { bgcolor: 'primary.dark' },
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: collapsed ? 0 : 40,
                      color: active ? 'inherit' : 'text.secondary',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  {!collapsed && (
                    <ListItemText
                      primary={item.label}
                      slotProps={{
                        primary: { sx: { fontSize: '0.875rem', fontWeight: active ? 600 : 400 } },
                      }}
                    />
                  )}
                </ListItemButton>
              </Tooltip>
            );
          })}
        </List>

        {/* Expand button when collapsed */}
        {collapsed && (
          <>
            <Divider />
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 1 }}>
              <Tooltip title="Expand sidebar">
                <IconButton size="small" onClick={() => setCollapsed(false)}>
                  <MenuIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </>
        )}

        {/* User footer */}
        <Divider />
        <Box sx={{ p: collapsed ? 1 : 2 }}>
          {collapsed ? (
            <Tooltip title={user?.username ?? 'User'}>
              <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: 14 }}>
                  {user?.username?.[0]?.toUpperCase()}
                </Avatar>
              </IconButton>
            </Tooltip>
          ) : (
            <Stack
              direction="row"
              sx={{ alignItems: 'center', gap: 1.5, cursor: 'pointer' }}
              onClick={(e) => setAnchorEl(e.currentTarget)}
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: 14 }}>
                {user?.username?.[0]?.toUpperCase()}
              </Avatar>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="body2" noWrap sx={{ fontWeight: 600 }}>
                  {user?.username}
                </Typography>
                <Chip
                  label={user?.role}
                  size="small"
                  sx={{ height: 18, fontSize: '0.65rem', fontWeight: 700 }}
                  color="primary"
                  variant="outlined"
                />
              </Box>
            </Stack>
          )}
        </Box>
      </Drawer>

      {/* ── Right side: topbar + content ────────────────────────────────── */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            bgcolor: 'background.paper',
            borderBottom: (t) => `1px solid ${t.palette.divider}`,
            color: 'text.primary',
          }}
        >
          <Toolbar sx={{ gap: 1 }}>
            <Typography
              variant="h6"
              sx={{ fontWeight: 600, flexGrow: 1 }}
            >
              {NAV_ITEMS.find((n) => isActive(n.path))?.label ?? 'Dashboard'}
            </Typography>

            <Tooltip title={`Switch to ${mode === 'dark' ? 'light' : 'dark'} mode`}>
              <IconButton onClick={toggleTheme} size="small">
                {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
              </IconButton>
            </Tooltip>
          </Toolbar>
        </AppBar>

        <Box
          component="main"
          sx={{ flexGrow: 1, p: 3, overflow: 'auto', bgcolor: 'background.default' }}
        >
          {children}
        </Box>
      </Box>

      {/* ── User menu ───────────────────────────────────────────────────── */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
        transformOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'top' }}
      >
        <MenuItem disabled>
          <ListItemIcon><Person fontSize="small" /></ListItemIcon>
          <Typography variant="body2">{user?.email}</Typography>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon><Logout fontSize="small" /></ListItemIcon>
          <Typography variant="body2">Sign out</Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
}
