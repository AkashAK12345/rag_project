// src/pages/DashboardPage.tsx
import { Box, Grid, Typography, Card, CardContent, Divider, Stack } from '@mui/material';
import { Storage, Hub, SettingsInputComponent, Memory, History } from '@mui/icons-material';
import { PageHeader } from '@/components/common/PageHeader';
import { StatCard } from '@/components/common/StatCard';
import { StatusChip } from '@/components/common/StatusChip';
import { ErrorState } from '@/components/common/ErrorState';
import { useSystemHealth, useIndexStats } from '@/hooks/useSystem';
import { useJobs } from '@/hooks/useJobs';
import { EmptyState } from '@/components/common/EmptyState';
import dayjs from 'dayjs';

export function DashboardPage() {
  const { data: health, isLoading: healthLoading, isError: healthError } = useSystemHealth();
  const { data: indexStats, isLoading: indexLoading } = useIndexStats();
  const { data: jobsData, isLoading: jobsLoading } = useJobs();

  if (healthError) {
    return <ErrorState title="System Unavailable" message="Could not connect to the backend services." />;
  }

  // Format uptime
  const formatUptime = (seconds?: number) => {
    if (!seconds) return '--';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hrs}h ${mins}m`;
  };

  return (
    <Box>
      <PageHeader
        title="Dashboard"
        subtitle="Overview of system health, indexing status, and recent activity."
      />

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <StatCard
            title="System Status"
            value={healthLoading ? '--' : health?.status.toUpperCase() || 'UNKNOWN'}
            subtitle={`Uptime: ${formatUptime(health?.uptime_seconds)}`}
            icon={<Memory />}
            color={health?.status === 'ok' ? 'success' : 'warning'}
            loading={healthLoading}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <StatCard
            title="Total Uploaded Reports"
            value={indexLoading ? '--' : indexStats?.indexed_files ?? 0}
            subtitle={indexStats?.last_indexing_timestamp ? `Last update: ${dayjs.unix(indexStats.last_indexing_timestamp).format('MMM D, HH:mm')}` : 'No reports yet'}
            icon={<Storage />}
            color="primary"
            loading={indexLoading}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <StatCard
            title="Vector Index Status"
            value={indexLoading ? '--' : indexStats?.indexed_documents ?? 0}
            subtitle="Total indexed nodes/documents"
            icon={<Hub />}
            color="secondary"
            loading={indexLoading}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* System Components */}
        <Grid size={{ xs: 12, lg: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Component Health
              </Typography>
              <Stack spacing={2} divider={<Divider />}>
                {[
                  { label: 'Vector Store', key: 'index_loaded', icon: <Hub fontSize="small" /> },
                  { label: 'Embedding Model', key: 'embedding_loaded', icon: <SettingsInputComponent fontSize="small" /> },
                  { label: 'LLM Engine', key: 'llm_loaded', icon: <Memory fontSize="small" /> },
                ].map((item) => (
                  <Stack key={item.key} direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
                    <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center' }}>
                      <Box sx={{ color: 'text.secondary', display: 'flex' }}>{item.icon}</Box>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>{item.label}</Typography>
                    </Stack>
                    <StatusChip 
                      status={health?.[item.key as keyof typeof health] ? 'ok' : 'error'} 
                      size="small" 
                    />
                  </Stack>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Jobs */}
        <Grid size={{ xs: 12, lg: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Recent Jobs
              </Typography>
              {jobsLoading ? (
                <Typography color="text.secondary">Loading...</Typography>
              ) : jobsData?.jobs && jobsData.jobs.length > 0 ? (
                <Stack spacing={2} divider={<Divider />}>
                  {jobsData.jobs.slice(0, 5).map((job) => (
                    <Stack key={job.job_id} direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          Job {job.job_id.substring(0, 8)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {dayjs(job.created_at).format('MMM D, YYYY HH:mm:ss')} • {job.uploaded_files.length} file(s)
                        </Typography>
                      </Box>
                      <StatusChip status={job.status} size="small" />
                    </Stack>
                  ))}
                </Stack>
              ) : (
                <EmptyState
                  icon={<History />}
                  title="No Jobs Found"
                  description="There are no recent background indexing jobs."
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
