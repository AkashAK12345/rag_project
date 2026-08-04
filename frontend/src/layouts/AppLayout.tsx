// src/layouts/AppLayout.tsx
import { useState, type ReactNode } from 'react';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import {
  Box, Drawer, AppBar, Toolbar, Typography, IconButton, Tooltip,
  List, ListItemButton, ListItemIcon, ListItemText, Divider, Avatar,
  Stack, Chip, useTheme, Menu, MenuItem, Badge,
} from '@mui/material';
import {
  LayoutDashboard, Upload, MessageSquare, BarChart3, TrendingUp,
  Activity, Settings, ChevronLeft, Menu as MenuIcon, Sun, Moon,
  Bell, LogOut, User, Brain, ChevronDown,
} from 'lucide-react';
import { SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH } from '@/theme';
import { shadows } from '@/theme/shadows';
import { radius } from '@/theme/radius';
import { brand, neutral } from '@/theme/colors';
import { useAuthContext } from '@/store/authStore';
import { useThemeContext } from '@/store/themeStore';
import { authApi } from '@/api/authApi';

interface NavItem { label: string; icon: ReactNode; path: string }

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard',      icon: <LayoutDashboard size={18} />, path: '/' },
  { label: 'Upload Reports', icon: <Upload size={18} />,          path: '/upload' },
  { label: 'AI Chat',        icon: <MessageSquare size={18} />,   path: '/chat' },
  { label: 'Analytics',      icon: <BarChart3 size={18} />,       path: '/analytics' },
  { label: 'Forecasting',    icon: <TrendingUp size={18} />,      path: '/forecasting' },
  { label: 'Health',         icon: <Activity size={18} />,        path: '/health' },
  { label: 'Settings',       icon: <Settings size={18} />,        path: '/settings' },
];

const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
};

interface Props { children: ReactNode }

export function AppLayout({ children }: Props) {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthContext();
  const { mode, toggleTheme } = useThemeContext();
  const [collapsed, setCollapsed] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const isLight = mode === 'light';

  const drawerWidth = collapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH;

  const handleLogout = async () => {
    setAnchorEl(null);
    try { await authApi.logout(); } catch { /* stateless */ }
    logout();
    navigate('/login', { replace: true });
  };

  const isActive = (path: string) =>
    path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);

  const sidebarBg = isLight ? neutral.white : theme.palette.background.paper;
  const activeBg  = brand.orange;
  const hoverBg   = isLight ? brand.orangeSubtle : 'rgba(249,115,22,0.10)';

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>

      {/* ── Sidebar ─────────────────────────────────────────────────────────── */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            overflowX: 'hidden',
            transition: theme.transitions.create('width'),
            border: 'none',
            boxShadow: shadows.sidebar,
            bgcolor: sidebarBg,
            display: 'flex',
            flexDirection: 'column',
          },
        }}
      >
        {/* Logo area */}
        <Box
          sx={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'space-between',
            px: collapsed ? 1 : 2.5,
            borderBottom: `1px solid ${isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.06)'}`,
          }}
        >
          <Stack direction="row" sx={{ alignItems: 'center', gap: 1.5, overflow: 'hidden', flexGrow: 1 }}>
            {/* Brand icon */}
            <Box
              sx={{
                width: 36,
                height: 36,
                borderRadius: `${radius.avatar}px`,
                flexShrink: 0,
                background: `linear-gradient(135deg, ${brand.orange}, ${brand.orangeDark})`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: `0 4px 12px ${brand.orange}55`,
              }}
            >
              <Brain size={20} color="#fff" />
            </Box>
            {!collapsed && (
              <Box sx={{ minWidth: 0 }}>
                <Typography variant="h6" noWrap sx={{ fontWeight: 800, color: 'text.primary', lineHeight: 1.1 }}>
                  GROVIT AI
                </Typography>
                <Typography variant="caption" noWrap sx={{ color: brand.orange, fontWeight: 500, fontSize: '0.65rem', lineHeight: 1 }}>
                  Digital CEO for Modern Businesses
                </Typography>
              </Box>
            )}
          </Stack>
          {!collapsed && (
            <IconButton size="small" onClick={() => setCollapsed(true)} sx={{ color: 'text.secondary', flexShrink: 0 }}>
              <ChevronLeft size={16} />
            </IconButton>
          )}
        </Box>

        {/* Nav items */}
        <List sx={{ px: 1.5, py: 2, flexGrow: 1 }}>
          {NAV_ITEMS.map((item) => {
            const active = isActive(item.path);
            return (
              <Tooltip key={item.path} title={collapsed ? item.label : ''} placement="right">
                <ListItemButton
                  component={RouterLink}
                  to={item.path}
                  selected={active}
                  sx={{
                    borderRadius: `${radius.navPill}px`,
                    mb: 0.5,
                    px: collapsed ? 1.5 : 1.5,
                    py: 1,
                    justifyContent: collapsed ? 'center' : 'flex-start',
                    bgcolor: active ? activeBg : 'transparent',
                    color: active ? neutral.white : 'text.secondary',
                    '&:hover': {
                      bgcolor: active ? brand.orangeDark : hoverBg,
                      color: active ? neutral.white : brand.orange,
                    },
                    '&.Mui-selected': {
                      bgcolor: activeBg,
                      '&:hover': { bgcolor: brand.orangeDark },
                    },
                    transition: 'all 150ms ease',
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: collapsed ? 0 : 36,
                      color: 'inherit',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  {!collapsed && (
                    <ListItemText
                      primary={item.label}
                      slotProps={{
                        primary: { sx: { fontSize: '0.875rem', fontWeight: active ? 600 : 500, color: 'inherit' } },
                      }}
                    />
                  )}
                </ListItemButton>
              </Tooltip>
            );
          })}
        </List>

        {/* Expand when collapsed */}
        {collapsed && (
          <>
            <Divider />
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 1.5 }}>
              <Tooltip title="Expand sidebar" placement="right">
                <IconButton size="small" onClick={() => setCollapsed(false)} sx={{ color: 'text.secondary' }}>
                  <MenuIcon size={18} />
                </IconButton>
              </Tooltip>
            </Box>
          </>
        )}

        {/* User profile footer */}
        <Box
          sx={{
            borderTop: `1px solid ${isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.06)'}`,
            p: collapsed ? 1.5 : 2,
          }}
        >
          {collapsed ? (
            <Tooltip title={user?.username ?? 'User'} placement="right">
              <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: brand.orange, fontSize: 13, fontWeight: 700 }}>
                  {user?.username?.[0]?.toUpperCase()}
                </Avatar>
              </IconButton>
            </Tooltip>
          ) : (
            <Stack
              direction="row"
              sx={{ alignItems: 'center', gap: 1.5, cursor: 'pointer', borderRadius: `${radius.navPill}px`, p: 1, transition: 'background 150ms ease', '&:hover': { bgcolor: hoverBg } }}
              onClick={(e) => setAnchorEl(e.currentTarget)}
            >
              <Avatar sx={{ width: 34, height: 34, bgcolor: brand.orange, fontSize: 13, fontWeight: 700, flexShrink: 0 }}>
                {user?.username?.[0]?.toUpperCase()}
              </Avatar>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="body2" noWrap sx={{ fontWeight: 600, color: 'text.primary' }}>
                  {user?.username}
                </Typography>
                <Typography variant="caption" noWrap sx={{ color: 'text.secondary', textTransform: 'capitalize' }}>
                  {user?.role}
                </Typography>
              </Box>
              <ChevronDown size={14} style={{ color: neutral[400], flexShrink: 0 }} />
            </Stack>
          )}
        </Box>
      </Drawer>

      {/* ── Main right panel ────────────────────────────────────────────────── */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>

        {/* Top navigation bar */}
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            bgcolor: isLight ? neutral.white : theme.palette.background.paper,
            boxShadow: shadows.topbar,
            color: 'text.primary',
            zIndex: theme.zIndex.drawer - 1,
          }}
        >
          <Toolbar sx={{ gap: 1.5, height: 64, px: 3 }}>
            {/* Greeting */}
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
                {getGreeting()}, {user?.username ?? 'there'} 👋
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {NAV_ITEMS.find((n) => isActive(n.path))?.label ?? 'Dashboard'}
              </Typography>
            </Box>

            {/* AI Powered badge */}
            <Chip
              label="AI Powered"
              size="small"
              icon={<Brain size={12} />}
              sx={{
                bgcolor: brand.orangeSubtle,
                color: brand.orange,
                fontWeight: 700,
                fontSize: '0.7rem',
                borderRadius: `${radius.full}px`,
                border: `1px solid ${brand.orangeLight}55`,
                '& .MuiChip-icon': { color: brand.orange },
              }}
            />

            {/* Notifications (visual only) */}
            <Tooltip title="Notifications">
              <IconButton size="small" sx={{ color: 'text.secondary' }}>
                <Badge badgeContent={0} color="error">
                  <Bell size={18} />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* Theme toggle */}
            <Tooltip title={`Switch to ${mode === 'dark' ? 'light' : 'dark'} mode`}>
              <IconButton
                onClick={toggleTheme}
                size="small"
                sx={{
                  color: 'text.secondary',
                  bgcolor: isLight ? neutral[100] : 'rgba(255,255,255,0.07)',
                  borderRadius: `${radius.chip}px`,
                  '&:hover': { bgcolor: isLight ? neutral[200] : 'rgba(255,255,255,0.12)' },
                }}
              >
                {mode === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              </IconButton>
            </Tooltip>

            {/* User avatar → menu */}
            <Tooltip title={user?.username ?? 'Account'}>
              <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ p: 0 }}>
                <Avatar sx={{ width: 34, height: 34, bgcolor: brand.orange, fontSize: 13, fontWeight: 700 }}>
                  {user?.username?.[0]?.toUpperCase()}
                </Avatar>
              </IconButton>
            </Tooltip>
          </Toolbar>
        </AppBar>

        {/* Page content */}
        <Box
          component="main"
          sx={{ flexGrow: 1, p: 4, overflow: 'auto', bgcolor: 'background.default' }}
        >
          {children}
        </Box>
      </Box>

      {/* ── User menu ───────────────────────────────────────────────────────── */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
        transformOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'top' }}
        slotProps={{
          paper: {
            sx: {
              borderRadius: `${radius.card}px`,
              boxShadow: shadows.floating,
              minWidth: 200,
              mt: 1,
            },
          },
        }}
      >
        <MenuItem disabled sx={{ opacity: 1 }}>
          <ListItemIcon><User size={16} /></ListItemIcon>
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>{user?.username}</Typography>
            <Typography variant="caption" color="text.secondary">{user?.email}</Typography>
          </Box>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
          <ListItemIcon sx={{ color: 'error.main' }}><LogOut size={16} /></ListItemIcon>
          <Typography variant="body2">Sign out</Typography>
        </MenuItem>
      </Menu>
    </Box>
  );
}
