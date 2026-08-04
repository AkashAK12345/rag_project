// src/pages/DashboardPage.tsx
import { Box, Grid, Typography, Card, CardContent, Divider, Stack, Skeleton, LinearProgress } from '@mui/material';
import {
  Server, Database, Cpu, Network, History,
} from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { StatCard } from '@/components/common/StatCard';
import { StatusChip } from '@/components/common/StatusChip';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { useSystemHealth, useIndexStats } from '@/hooks/useSystem';
import { useJobs } from '@/hooks/useJobs';
import { brand, neutral, semantic } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
dayjs.extend(relativeTime);

// ── Helpers ──────────────────────────────────────────────────────────────────

const formatUptime = (seconds?: number) => {
  if (!seconds) return '--';
  const hrs  = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return hrs > 0 ? `${hrs}h ${mins}m uptime` : `${mins}m uptime`;
};

// ── Component Health Row ──────────────────────────────────────────────────────

interface ComponentRowProps {
  label: string;
  icon: React.ReactNode;
  loaded: boolean | undefined;
  loading: boolean;
}

function ComponentRow({ label, icon, loaded, loading }: ComponentRowProps) {
  const ok = Boolean(loaded);
  return (
    <Stack
      direction="row"
      sx={{ justifyContent: 'space-between', alignItems: 'center', py: 1.75 }}
    >
      <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: `${radius.chip}px`,
            bgcolor: ok ? semantic.successSubtle : semantic.errorSubtle,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: ok ? semantic.success : semantic.error,
            transition: 'all 200ms ease',
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
            {label}
          </Typography>
          {loading ? (
            <Skeleton width={60} height={14} sx={{ borderRadius: 1 }} />
          ) : (
            <Typography variant="caption" sx={{ color: ok ? semantic.success : semantic.error, fontWeight: 500 }}>
              {ok ? 'Operational' : 'Unavailable'}
            </Typography>
          )}
        </Box>
      </Stack>
      {loading ? (
        <Skeleton variant="rounded" width={72} height={22} sx={{ borderRadius: 1 }} />
      ) : (
        <StatusChip status={ok ? 'ok' : 'error'} size="small" />
      )}
    </Stack>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────────

export function DashboardPage() {
  const { data: health, isLoading: healthLoading, isError: healthError, refetch: refetchHealth } = useSystemHealth();
  const { data: indexStats, isLoading: indexLoading } = useIndexStats();
  const { data: jobsData, isLoading: jobsLoading } = useJobs();

  if (healthError) {
    return (
      <Box>
        <PageHeader title="Dashboard" subtitle="System overview and operational status." />
        <ErrorState
          title="System Unavailable"
          message="Could not connect to backend services. Make sure the server is running."
          onRetry={refetchHealth}
        />
      </Box>
    );
  }

  const systemOk    = health?.status === 'ok';
  const recentJobs  = jobsData?.jobs?.slice(0, 6) ?? [];

  const components = [
    { label: 'Vector Store',     key: 'index_loaded',     icon: <Database size={16} /> },
    { label: 'Embedding Model',  key: 'embedding_loaded', icon: <Network size={16} /> },
    { label: 'LLM Engine',       key: 'llm_loaded',       icon: <Cpu size={16} /> },
  ] as const;

  return (
    <Box>
      <PageHeader
        title="Dashboard"
        subtitle="Real-time system health, data ingestion metrics, and activity overview."
      />

      {/* ── KPI Stat Cards ───────────────────────────────────────────────── */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <StatCard
            title="System Status"
            value={healthLoading ? '--' : systemOk ? 'Healthy' : (health?.status?.toUpperCase() ?? 'Unknown')}
            subtitle={healthLoading ? undefined : formatUptime(health?.uptime_seconds)}
            icon={<Server size={22} />}
            color={systemOk ? 'success' : 'warning'}
            loading={healthLoading}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <StatCard
            title="Indexed Reports"
            value={indexLoading ? '--' : indexStats?.indexed_files ?? 0}
            subtitle={
              indexStats?.last_indexing_timestamp
                ? `Last update ${dayjs.unix(indexStats.last_indexing_timestamp).fromNow()}`
                : 'No reports ingested yet'
            }
            icon={<Database size={22} />}
            color="primary"
            loading={indexLoading}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <StatCard
            title="Vector Documents"
            value={indexLoading ? '--' : indexStats?.indexed_documents ?? 0}
            subtitle="Total indexed nodes in vector store"
            icon={<Network size={22} />}
            color="secondary"
            loading={indexLoading}
          />
        </Grid>
      </Grid>

      {/* ── Lower panels ─────────────────────────────────────────────────── */}
      <Grid container spacing={3}>

        {/* Component Health */}
        <Grid size={{ xs: 12, lg: 5 }}>
          <Card
            sx={{
              height: '100%',
              borderRadius: `${radius.card}px`,
              boxShadow: shadows.card,
              border: 'none',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              {/* Card header */}
              <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700 }}>Component Health</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Live status of AI pipeline components
                  </Typography>
                </Box>
                {!healthLoading && (
                  <Box
                    sx={{
                      px: 1.5,
                      py: 0.5,
                      borderRadius: `${radius.full}px`,
                      bgcolor: systemOk ? semantic.successSubtle : semantic.warningSubtle,
                      border: `1px solid ${systemOk ? semantic.success : semantic.warning}33`,
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{ fontWeight: 700, color: systemOk ? semantic.successDark : semantic.warningDark }}
                    >
                      {systemOk ? 'All systems go' : 'Degraded'}
                    </Typography>
                  </Box>
                )}
              </Stack>

              <Divider sx={{ mb: 0.5 }} />

              <Stack divider={<Divider />}>
                {components.map((c) => (
                  <ComponentRow
                    key={c.key}
                    label={c.label}
                    icon={c.icon}
                    loaded={health?.[c.key]}
                    loading={healthLoading}
                  />
                ))}
              </Stack>

              {/* Pipeline throughput bar */}
              {!healthLoading && indexStats && indexStats.indexed_documents > 0 && (
                <Box
                  sx={{
                    mt: 2.5,
                    p: 2,
                    borderRadius: `${radius.chip}px`,
                    bgcolor: brand.orangeSubtle,
                    border: `1px solid ${brand.orange}22`,
                  }}
                >
                  <Stack direction="row" sx={{ justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: brand.orange }}>
                      Index Utilization
                    </Typography>
                    <Typography variant="caption" sx={{ fontWeight: 700, color: brand.orange }}>
                      {indexStats.indexed_documents.toLocaleString()} nodes
                    </Typography>
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(100, (indexStats.indexed_documents / 10000) * 100)}
                    sx={{
                      height: 6,
                      borderRadius: `${radius.full}px`,
                      bgcolor: `${brand.orange}22`,
                      '& .MuiLinearProgress-bar': { bgcolor: brand.orange },
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Jobs */}
        <Grid size={{ xs: 12, lg: 7 }}>
          <Card
            sx={{
              height: '100%',
              borderRadius: `${radius.card}px`,
              boxShadow: shadows.card,
              border: 'none',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>Recent Jobs</Typography>
                <Typography variant="caption" color="text.secondary">
                  Latest background indexing and processing activity
                </Typography>
              </Box>

              {jobsLoading ? (
                <Stack spacing={2}>
                  {[1, 2, 3].map((i) => (
                    <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Skeleton variant="rounded" width={40} height={40} sx={{ borderRadius: `${radius.chip}px`, flexShrink: 0 }} />
                      <Box sx={{ flex: 1 }}>
                        <Skeleton width="45%" height={16} sx={{ mb: 0.5 }} />
                        <Skeleton width="65%" height={13} />
                      </Box>
                      <Skeleton variant="rounded" width={72} height={22} sx={{ borderRadius: 1 }} />
                    </Box>
                  ))}
                </Stack>
              ) : recentJobs.length > 0 ? (
                <Stack divider={<Divider />}>
                  {recentJobs.map((job) => {
                    const statusColor =
                      job.status === 'completed' ? semantic.success :
                      job.status === 'failed'    ? semantic.error :
                      job.status === 'indexing'  ? brand.orange :
                      neutral[400];

                    return (
                      <Stack
                        key={job.job_id}
                        direction="row"
                        sx={{
                          alignItems: 'center',
                          gap: 2,
                          py: 1.75,
                          transition: 'background 150ms ease',
                          borderRadius: `${radius.chip}px`,
                          px: 0.5,
                          mx: -0.5,
                          '&:hover': { bgcolor: (t) => t.palette.mode === 'light' ? neutral[50] : 'rgba(255,255,255,0.03)' },
                        }}
                      >
                        {/* Job icon */}
                        <Box
                          sx={{
                            width: 40,
                            height: 40,
                            borderRadius: `${radius.chip}px`,
                            flexShrink: 0,
                            bgcolor: `${statusColor}18`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: statusColor,
                          }}
                        >
                          <History size={16} />
                        </Box>

                        {/* Job info */}
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography variant="body2" noWrap sx={{ fontWeight: 600 }}>
                            {job.uploaded_files.length > 0
                              ? job.uploaded_files[0]
                              : `Job ${job.job_id.slice(0, 8)}`}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {dayjs(job.created_at).fromNow()} · {job.uploaded_files.length} file{job.uploaded_files.length !== 1 ? 's' : ''}
                            {job.indexed_documents ? ` · ${job.indexed_documents} docs` : ''}
                          </Typography>
                        </Box>

                        <StatusChip status={job.status} size="small" />
                      </Stack>
                    );
                  })}
                </Stack>
              ) : (
                <EmptyState
                  icon={<History size={32} />}
                  title="No Jobs Yet"
                  description="Upload Excel reports to start a background indexing job."
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
