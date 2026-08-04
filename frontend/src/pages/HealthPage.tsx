// src/pages/HealthPage.tsx
import { Box, Grid, Card, CardContent, Typography, Stack, Divider, Table, TableBody, TableCell, TableHead, TableRow, CircularProgress, IconButton, Paper, TableContainer, alpha } from '@mui/material';
import { Cpu, Database, Network, Clock, RefreshCw, CheckCircle2, AlertTriangle, Activity } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { StatCard } from '@/components/common/StatCard';
import { StatusChip } from '@/components/common/StatusChip';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { useSystemHealth, useIndexStats, useModelConfigs } from '@/hooks/useSystem';
import { useJobs } from '@/hooks/useJobs';
import dayjs from 'dayjs';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';

// --- Utilities ---
const formatBytes = (bytes?: number) => {
  if (bytes === undefined) return '--';
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatUptime = (seconds?: number) => {
  if (seconds === undefined) return '--';
  const d = Math.floor(seconds / (3600 * 24));
  const h = Math.floor((seconds % (3600 * 24)) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
};

const formatTime = (ts?: number) => {
  if (!ts) return '--';
  return dayjs(ts).format('HH:mm:ss');
};

const formatTimestamp = (ts?: string | number) => {
  if (!ts) return '--';
  if (typeof ts === 'number' && ts < 2000000000) {
    return dayjs.unix(ts).format('MMM D, YYYY HH:mm:ss');
  }
  return dayjs(ts).format('MMM D, YYYY HH:mm:ss');
};

const SectionHeader = ({ title, lastUpdated, onRetry, isLoading }: { title: string, lastUpdated?: number, onRetry?: () => void, isLoading?: boolean }) => (
  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
    <Typography variant="h6" sx={{ fontWeight: 800, letterSpacing: '-0.01em' }}>{title}</Typography>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
      {isLoading && <CircularProgress size={16} />}
      {lastUpdated ? (
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
          Updated: {formatTime(lastUpdated)}
        </Typography>
      ) : null}
      {onRetry && (
        <IconButton size="small" onClick={onRetry} disabled={isLoading} title="Retry" sx={{ bgcolor: (t) => t.palette.mode === 'light' ? '#f1f5f9' : 'rgba(255,255,255,0.05)', borderRadius: `${radius.chip}px` }}>
          <RefreshCw size={16} />
        </IconButton>
      )}
    </Box>
  </Box>
);

const SectionCard = ({ children }: { children: React.ReactNode }) => (
  <Card 
    elevation={0}
    sx={{ 
      height: '100%', 
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

// --- Sub-components ---

const SystemOverviewSection = () => {
  const { data: health, isLoading, isError, refetch, dataUpdatedAt } = useSystemHealth();

  if (isError) {
    return (
      <Box sx={{ mb: 5 }}>
        <SectionHeader title="System Overview" onRetry={refetch} isLoading={isLoading} lastUpdated={dataUpdatedAt} />
        <ErrorState title="System Overview Error" message="Failed to load system health data." onRetry={refetch} />
      </Box>
    );
  }

  return (
    <Box sx={{ mb: 5 }}>
      <SectionHeader title="System Overview" onRetry={refetch} isLoading={isLoading} lastUpdated={dataUpdatedAt} />
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="System Status"
            value={isLoading ? '--' : health?.status.toUpperCase() || 'UNKNOWN'}
            subtitle={`Version: ${health?.version || '--'}`}
            icon={<Cpu />}
            color={health?.status === 'ok' ? 'success' : 'error'}
            loading={isLoading}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Uptime"
            value={isLoading ? '--' : formatUptime(health?.uptime_seconds)}
            subtitle="Continuous running time"
            icon={<Clock />}
            color="primary"
            loading={isLoading}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Server Time"
            value={isLoading ? '--' : (health?.server_time ? dayjs(health.server_time).format('HH:mm:ss') : '--')}
            subtitle={health?.server_time ? dayjs(health.server_time).format('MMM D, YYYY') : '--'}
            icon={<Activity />}
            color="secondary"
            loading={isLoading}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Core Health"
            value={isLoading ? '--' : (health?.status === 'ok' ? 'Healthy' : 'Degraded')}
            subtitle="API readiness"
            icon={health?.status === 'ok' ? <CheckCircle2 /> : <AlertTriangle />}
            color={health?.status === 'ok' ? 'success' : 'warning'}
            loading={isLoading}
          />
        </Grid>
      </Grid>
    </Box>
  );
};


const ComponentStatusSection = () => {
  const { data: health, isLoading, isError, refetch, dataUpdatedAt } = useSystemHealth();

  return (
    <SectionCard>
      <SectionHeader title="Component Status" onRetry={refetch} isLoading={isLoading} lastUpdated={dataUpdatedAt} />
      {isError ? (
        <ErrorState title="Component Status Error" message="Failed to load component statuses." onRetry={refetch} />
      ) : (
        <Stack spacing={2} divider={<Divider sx={{ opacity: 0.6 }} />}>
          {[
            { label: 'LLM Engine', key: 'llm_loaded' as const, icon: <Cpu size={18} /> },
            { label: 'Embedding Model', key: 'embedding_loaded' as const, icon: <Network size={18} /> },
            { label: 'Vector Store', key: 'index_loaded' as const, icon: <Database size={18} /> },
          ].map((item) => {
            const status = health?.[item.key] ? 'ok' : 'error';
            return (
              <Stack key={item.key} direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
                <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
                  <Box sx={{ color: 'text.secondary', display: 'flex' }}>{item.icon}</Box>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>{item.label}</Typography>
                </Stack>
                <StatusChip status={status} size="small" />
              </Stack>
            );
          })}
        </Stack>
      )}
    </SectionCard>
  );
};

const ModelConfigSection = () => {
  const { data: models, isLoading, isError, refetch, dataUpdatedAt } = useModelConfigs();

  return (
    <SectionCard>
      <SectionHeader title="Model Configuration" onRetry={refetch} isLoading={isLoading} lastUpdated={dataUpdatedAt} />
      {isError ? (
        <ErrorState title="Model Config Error" message="Failed to load model configurations." onRetry={refetch} />
      ) : (
        <Stack spacing={2} divider={<Divider sx={{ opacity: 0.6 }} />}>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>LLM Provider</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>{isLoading ? '--' : models?.llm_provider || 'N/A'}</Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>LLM Model</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>{isLoading ? '--' : models?.llm_model || 'N/A'}</Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Embedding Model</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>{isLoading ? '--' : models?.embedding_model || 'N/A'}</Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Vector Store</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>{isLoading ? '--' : models?.vector_store_type || 'N/A'}</Typography>
          </Stack>
        </Stack>
      )}
    </SectionCard>
  );
};

const IndexStatsSection = () => {
  const { data: stats, isLoading, isError, refetch, dataUpdatedAt } = useIndexStats();

  return (
    <SectionCard>
      <SectionHeader title="Index Storage Statistics" onRetry={refetch} isLoading={isLoading} lastUpdated={dataUpdatedAt} />
      {isError ? (
        <ErrorState title="Index Stats Error" message="Failed to load index statistics." onRetry={refetch} />
      ) : (
        <Stack spacing={2} divider={<Divider sx={{ opacity: 0.6 }} />}>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Storage Directory</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'monospace' }}>{isLoading ? '--' : stats?.storage_directory || 'N/A'}</Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Storage Size</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>{isLoading ? '--' : formatBytes(stats?.storage_size_bytes)}</Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Indexed Files</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>{isLoading ? '--' : stats?.indexed_files}</Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Indexed Documents</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>{isLoading ? '--' : stats?.indexed_documents}</Typography>
          </Stack>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center', py: 0.5 }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Last Indexing Activity</Typography>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>{isLoading ? '--' : formatTimestamp(stats?.last_indexing_timestamp)}</Typography>
          </Stack>
        </Stack>
      )}
    </SectionCard>
  );
};

const JobsListSection = () => {
  const { data: jobsData, isLoading, isError, refetch, dataUpdatedAt } = useJobs();

  const jobs = jobsData?.jobs || [];
  
  const summary = jobs.reduce((acc, job) => {
    if (['queued', 'validating', 'saving_files', 'indexing'].includes(job.status)) acc.running++;
    else if (job.status === 'completed') acc.completed++;
    else if (job.status === 'failed') acc.failed++;
    return acc;
  }, { running: 0, completed: 0, failed: 0 });

  return (
    <SectionCard>
      <SectionHeader title="Background Jobs Summary" onRetry={refetch} isLoading={isLoading} lastUpdated={dataUpdatedAt} />
      
      {isError ? (
        <ErrorState title="Jobs Error" message="Failed to load background jobs." onRetry={refetch} />
      ) : (
        <>
          <Box sx={{ mb: 4 }}>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 4 }}>
                <Paper elevation={0} sx={{ p: 2.5, textAlign: 'center', borderRadius: `${radius.card}px`, border: (t) => `1px solid ${alpha(t.palette.info.main, 0.3)}`, bgcolor: (t) => alpha(t.palette.info.main, 0.05) }}>
                  <Typography variant="body2" sx={{ color: 'info.main', fontWeight: 700, mb: 0.5 }}>Active / Queued</Typography>
                  <Typography variant="h4" color="info.main" sx={{ fontWeight: 800 }}>{isLoading ? '-' : summary.running}</Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <Paper elevation={0} sx={{ p: 2.5, textAlign: 'center', borderRadius: `${radius.card}px`, border: (t) => `1px solid ${alpha(t.palette.success.main, 0.3)}`, bgcolor: (t) => alpha(t.palette.success.main, 0.05) }}>
                  <Typography variant="body2" sx={{ color: 'success.main', fontWeight: 700, mb: 0.5 }}>Completed</Typography>
                  <Typography variant="h4" color="success.main" sx={{ fontWeight: 800 }}>{isLoading ? '-' : summary.completed}</Typography>
                </Paper>
              </Grid>
              <Grid size={{ xs: 12, sm: 4 }}>
                <Paper elevation={0} sx={{ p: 2.5, textAlign: 'center', borderRadius: `${radius.card}px`, border: (t) => `1px solid ${alpha(t.palette.error.main, 0.3)}`, bgcolor: (t) => alpha(t.palette.error.main, 0.05) }}>
                  <Typography variant="body2" sx={{ color: 'error.main', fontWeight: 700, mb: 0.5 }}>Failed</Typography>
                  <Typography variant="h4" color="error.main" sx={{ fontWeight: 800 }}>{isLoading ? '-' : summary.failed}</Typography>
                </Paper>
              </Grid>
            </Grid>
          </Box>

          {jobs.length === 0 && !isLoading ? (
             <EmptyState icon={<Clock size={32} />} title="No Jobs Found" description="There are no recent background indexing jobs." />
          ) : (
            <TableContainer sx={{ maxHeight: 400, borderRadius: `${radius.card}px`, border: (t) => `1px solid ${t.palette.divider}` }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Job ID</TableCell>
                    <TableCell sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Progress</TableCell>
                    <TableCell sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Created</TableCell>
                    <TableCell sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Processing Time</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.job_id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                          {job.job_id.substring(0, 8)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <StatusChip status={job.status} size="small" />
                      </TableCell>
                      <TableCell sx={{ fontWeight: 500 }}>
                        {job.progress_percentage}%
                      </TableCell>
                      <TableCell sx={{ color: 'text.secondary', fontWeight: 500 }}>
                        {formatTimestamp(job.created_at)}
                      </TableCell>
                      <TableCell sx={{ color: 'text.secondary', fontWeight: 500 }}>
                        {job.processing_time_ms ? `${(job.processing_time_ms / 1000).toFixed(1)}s` : '--'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </>
      )}
    </SectionCard>
  );
};

// --- Main Page ---

export function HealthPage() {
  return (
    <Box>
      <PageHeader
        title="Health Dashboard"
        subtitle="Real-time monitoring of system health, indexing status, and background tasks."
      />

      <SystemOverviewSection />

      <Grid container spacing={4} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <ComponentStatusSection />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <ModelConfigSection />
        </Grid>
      </Grid>

      <Grid container spacing={4}>
        <Grid size={{ xs: 12, lg: 5 }}>
          <IndexStatsSection />
        </Grid>
        <Grid size={{ xs: 12, lg: 7 }}>
          <JobsListSection />
        </Grid>
      </Grid>
    </Box>
  );
}
