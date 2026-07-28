// src/routes/AppRouter.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { AppLayout } from '@/layouts/AppLayout';
import { LoginPage } from '@/features/auth/LoginPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { UploadPage } from '@/pages/UploadPage';
import { ChatPage } from '@/pages/ChatPage';
import { AnalyticsPage } from '@/pages/AnalyticsPage';
import { ForecastingPage } from '@/pages/ForecastingPage';
import { HealthPage } from '@/pages/HealthPage';
import { SettingsPage } from '@/pages/SettingsPage';

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected — wrapped in AppLayout */}
        <Route element={<ProtectedRoute />}>
          <Route
            element={
              <AppLayout>
                {/* AppLayout wraps all protected pages */}
                <Routes>
                  <Route path="/" element={<DashboardPage />} />
                  <Route path="/upload" element={<UploadPage />} />
                  <Route path="/chat" element={<ChatPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/forecasting" element={<ForecastingPage />} />
                  <Route path="/health" element={<HealthPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </AppLayout>
            }
            path="/*"
          />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
