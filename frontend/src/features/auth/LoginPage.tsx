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
import { Visibility, VisibilityOff, Psychology } from '@mui/icons-material';
import { authApi } from '@/api/authApi';
import { useAuthContext } from '@/store/authStore';

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

      // Store the token FIRST so Axios can attach it
      localStorage.setItem('access_token', tokenRes.access_token);

      // Now this request will include Authorization: Bearer <token>
      const userRes = await authApi.me();

      // Update React context
      login(tokenRes.access_token, userRes);

      navigate('/', { replace: true });
    } catch {
      setServerError('Invalid username or password.');
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
            ? 'radial-gradient(ellipse at 60% 20%, #4338CA33 0%, #0F172A 60%)'
            : 'radial-gradient(ellipse at 60% 20%, #EEF2FF 0%, #F8FAFC 60%)',
      }}
    >
      <Card sx={{ width: 420, p: 1 }}>
        <CardContent>
          <Stack sx={{ gap: 3 }}>
            {/* Logo / branding */}
            <Stack direction="row" sx={{ alignItems: 'center', gap: 1.5 }}>
              <Box
                sx={{
                  width: 44, height: 44, borderRadius: 2,
                  background: 'linear-gradient(135deg, #6366F1, #0EA5E9)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}
              >
                <Psychology sx={{ color: '#fff', fontSize: 26 }} />
              </Box>
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>RAG Analytics</Typography>
                <Typography variant="caption" color="text.secondary">
                  Enterprise Intelligence Platform
                </Typography>
              </Box>
            </Stack>

            <Box>
              <Typography variant="h6">Sign in to your account</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                Use your administrator credentials to continue.
              </Typography>
            </Box>

            {serverError && <Alert severity="error">{serverError}</Alert>}

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
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword((v) => !v)}
                            edge="end"
                            size="small"
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
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
                  sx={{ py: 1.5 }}
                >
                  {isSubmitting ? <CircularProgress size={22} color="inherit" /> : 'Sign In'}
                </Button>
              </Stack>
            </form>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
