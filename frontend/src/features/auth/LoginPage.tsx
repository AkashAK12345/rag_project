// src/features/auth/LoginPage.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box, Card, CardContent, TextField, Button, Typography,
  InputAdornment, IconButton, Alert, CircularProgress, Stack,
} from '@mui/material';
import { Eye, EyeOff, Brain, Lock, User } from 'lucide-react';
import { authApi } from '@/api/authApi';
import { useAuthContext } from '@/store/authStore';
import { brand, neutral } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

const schema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});
type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuthContext();
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState('');

  const {
    register, handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    setServerError('');
    try {
      const tokenRes = await authApi.login(values);
      localStorage.setItem('access_token', tokenRes.access_token);
      const userRes = await authApi.me();
      login(tokenRes.access_token, userRes);
      navigate('/', { replace: true });
    } catch {
      setServerError('Invalid username or password. Please try again.');
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: (t) =>
          t.palette.mode === 'dark'
            ? `radial-gradient(ellipse at 60% 20%, ${brand.orange}22 0%, #0F172A 60%)`
            : `radial-gradient(ellipse at 70% 30%, ${brand.orange}14 0%, ${neutral[50]} 55%)`,
        p: 2,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: 440 }}>
        {/* Brand header above card */}
        <Stack sx={{ alignItems: 'center', mb: 4 }}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: `${radius.avatar}px`,
              background: `linear-gradient(135deg, ${brand.orange}, ${brand.orangeDark})`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: `0 8px 24px ${brand.orange}44`,
              mb: 2,
            }}
          >
            <Brain size={28} color="#fff" />
          </Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: 'text.primary', letterSpacing: '-0.02em' }}>
            GROVIT AI
          </Typography>
          <Typography variant="body2" sx={{ color: brand.orange, fontWeight: 500, mt: 0.25 }}>
            Digital CEO for Modern Businesses
          </Typography>
        </Stack>

        {/* Login card */}
        <Card
          sx={{
            borderRadius: `${radius.card}px`,
            boxShadow: shadows.floating,
            border: 'none',
            overflow: 'visible',
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Stack sx={{ gap: 3 }}>
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
                  Welcome back
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Sign in to your account to continue.
                </Typography>
              </Box>

              {serverError && (
                <Alert severity="error" sx={{ borderRadius: `${radius.chip}px` }}>
                  {serverError}
                </Alert>
              )}

              <form onSubmit={handleSubmit(onSubmit)} noValidate>
                <Stack sx={{ gap: 2.5 }}>
                  <TextField
                    {...register('username')}
                    label="Username"
                    fullWidth
                    autoFocus
                    autoComplete="username"
                    error={Boolean(errors.username)}
                    helperText={errors.username?.message}
                    slotProps={{
                      input: {
                        startAdornment: (
                          <InputAdornment position="start">
                            <User size={16} style={{ color: neutral[400] }} />
                          </InputAdornment>
                        ),
                      },
                    }}
                  />
                  <TextField
                    {...register('password')}
                    label="Password"
                    type={showPassword ? 'text' : 'password'}
                    fullWidth
                    autoComplete="current-password"
                    error={Boolean(errors.password)}
                    helperText={errors.password?.message}
                    slotProps={{
                      input: {
                        startAdornment: (
                          <InputAdornment position="start">
                            <Lock size={16} style={{ color: neutral[400] }} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword((v) => !v)}
                              edge="end"
                              size="small"
                            >
                              {showPassword
                                ? <EyeOff size={16} style={{ color: neutral[400] }} />
                                : <Eye size={16} style={{ color: neutral[400] }} />
                              }
                            </IconButton>
                          </InputAdornment>
                        ),
                      },
                    }}
                  />
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    fullWidth
                    disabled={isSubmitting}
                    sx={{
                      py: 1.5,
                      mt: 0.5,
                      borderRadius: `${radius.button}px`,
                      fontWeight: 700,
                      fontSize: '0.9375rem',
                    }}
                  >
                    {isSubmitting ? <CircularProgress size={22} color="inherit" /> : 'Sign In'}
                  </Button>
                </Stack>
              </form>
            </Stack>
          </CardContent>
        </Card>

        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: 'block', textAlign: 'center', mt: 3 }}
        >
          © {new Date().getFullYear()} GROVIT AI. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
}
