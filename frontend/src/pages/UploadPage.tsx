// src/pages/UploadPage.tsx
import { useState } from 'react';
import {
  Box, Card, CardContent, Typography, Stack, LinearProgress,
  Divider, Chip, Skeleton,
} from '@mui/material';
import { FileSpreadsheet, CheckCircle2, XCircle, Clock, Loader2 } from 'lucide-react';
import { useSnackbar } from 'notistack';
import { PageHeader } from '@/components/common/PageHeader';
import { UploadDropzone } from '@/components/common/UploadDropzone';
import { StatusChip } from '@/components/common/StatusChip';
import { EmptyState } from '@/components/common/EmptyState';
import { useUpload } from '@/hooks/useUpload';
import { useJobPolling, useJobs } from '@/hooks/useJobs';
import { brand, neutral, semantic } from '@/theme/colors';
import { radius } from '@/theme/radius';
import { shadows } from '@/theme/shadows';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
dayjs.extend(relativeTime);

// ── Status helpers ────────────────────────────────────────────────────────────

const JOB_ACTIVE_STATUSES = ['queued', 'validating', 'saving_files', 'indexing'];

const getStatusLabel = (
  isUploading: boolean,
  jobStatus?: string,
): string => {
  if (isUploading)                   return 'Uploading files to server…';
  if (jobStatus === 'queued')        return 'Queued for processing…';
  if (jobStatus === 'validating')    return 'Validating files…';
  if (jobStatus === 'saving_files')  return 'Saving files to disk…';
  if (jobStatus === 'indexing')      return 'Indexing into vector store…';
  if (jobStatus === 'completed')     return 'Processing completed successfully.';
  if (jobStatus === 'failed')        return 'Processing failed.';
  return '';
};

const getStatusIcon = (status?: string) => {
  if (!status) return null;
  if (status === 'completed') return <CheckCircle2 size={16} color={semantic.success} />;
  if (status === 'failed')    return <XCircle size={16} color={semantic.error} />;
  if (JOB_ACTIVE_STATUSES.includes(status)) {
    return (
      <Loader2
        size={16}
        color={brand.orange}
        style={{ animation: 'spin 1.5s linear infinite' }}
      />
    );
  }
  return <Clock size={16} color={neutral[400]} />;
};

// ── Job History Item ──────────────────────────────────────────────────────────

function JobHistoryItem({ job, isFirst }: { job: any; isFirst: boolean }) {
  const isActive   = JOB_ACTIVE_STATUSES.includes(job.status);
  const isComplete = job.status === 'completed';
  const isFailed   = job.status === 'failed';

  const accentColor = isComplete ? semantic.success : isFailed ? semantic.error : isActive ? brand.orange : neutral[300];
  const bgColor     = isComplete ? semantic.successSubtle : isFailed ? semantic.errorSubtle : isActive ? brand.orangeSubtle : 'transparent';

  return (
    <>
      {!isFirst && <Divider />}
      <Box
        sx={{
          py: 2.5,
          px: 2,
          mx: -2,
          borderRadius: `${radius.chip}px`,
          bgcolor: isActive ? brand.orangeSubtle : 'transparent',
          transition: 'background 200ms ease',
          '&:hover': {
            bgcolor: (t) => t.palette.mode === 'light' ? neutral[50] : 'rgba(255,255,255,0.03)',
          },
        }}
      >
        <Stack direction="row" sx={{ alignItems: 'flex-start', gap: 2 }}>
          {/* File icon */}
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: `${radius.chip}px`,
              flexShrink: 0,
              bgcolor: bgColor,
              border: `1px solid ${accentColor}33`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: accentColor,
            }}
          >
            <FileSpreadsheet size={18} />
          </Box>

          {/* Job content */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 0.5, gap: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600 }} noWrap>
                {job.uploaded_files.length === 1
                  ? job.uploaded_files[0]
                  : `${job.uploaded_files.length} files — ${job.uploaded_files[0]}…`}
              </Typography>
              <StatusChip status={job.status} size="small" />
            </Stack>

            <Stack direction="row" sx={{ gap: 1.5, flexWrap: 'wrap', alignItems: 'center' }}>
              <Typography variant="caption" color="text.secondary">
                {dayjs(job.created_at).fromNow()}
              </Typography>
              {job.indexed_documents != null && job.indexed_documents > 0 && (
                <>
                  <Typography variant="caption" color="text.disabled">·</Typography>
                  <Chip
                    label={`${job.indexed_documents} docs indexed`}
                    size="small"
                    sx={{
                      height: 18,
                      fontSize: '0.65rem',
                      fontWeight: 600,
                      bgcolor: semantic.successSubtle,
                      color: semantic.successDark,
                      border: `1px solid ${semantic.success}33`,
                      borderRadius: `${radius.full}px`,
                    }}
                  />
                </>
              )}
              {job.uploaded_files.length > 1 && (
                <>
                  <Typography variant="caption" color="text.disabled">·</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {job.uploaded_files.length} files
                  </Typography>
                </>
              )}
            </Stack>

            {/* Active job progress bar */}
            {isActive && job.progress_percentage != null && (
              <Box sx={{ mt: 1.5 }}>
                <LinearProgress
                  variant={job.status === 'queued' ? 'indeterminate' : 'determinate'}
                  value={job.progress_percentage}
                  sx={{
                    height: 4,
                    borderRadius: `${radius.full}px`,
                    bgcolor: `${brand.orange}22`,
                    '& .MuiLinearProgress-bar': { bgcolor: brand.orange },
                  }}
                />
              </Box>
            )}

            {/* Error message */}
            {isFailed && job.error_message && (
              <Box
                sx={{
                  mt: 1.25,
                  p: 1,
                  borderRadius: `${radius.chip}px`,
                  bgcolor: semantic.errorSubtle,
                  border: `1px solid ${semantic.error}22`,
                }}
              >
                <Typography variant="caption" sx={{ color: semantic.errorDark, fontWeight: 500 }}>
                  {job.error_message}
                </Typography>
              </Box>
            )}
          </Box>
        </Stack>
      </Box>
    </>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────────

export function UploadPage() {
  const { enqueueSnackbar } = useSnackbar();
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const { mutate: uploadFiles, isPending: isUploading } = useUpload();
  const { data: jobData } = useJobPolling(activeJobId);
  const { data: jobsHistory, isLoading: historyLoading } = useJobs();

  const handleFilesSelected = (files: File[]) => {
    setUploadProgress(0);
    uploadFiles(
      { files, onProgress: setUploadProgress },
      {
        onSuccess: (data) => {
          enqueueSnackbar(data.message, { variant: 'success' });
          setActiveJobId(data.job_id);
        },
        onError: (err: any) => {
          enqueueSnackbar(err.response?.data?.detail || 'Upload failed', { variant: 'error' });
        },
      }
    );
  };

  const isJobActive   = jobData && JOB_ACTIVE_STATUSES.includes(jobData.status);
  const showProgress  = isUploading || isJobActive;
  const progressValue = isUploading ? uploadProgress : jobData?.progress_percentage ?? 0;
  const statusLabel   = getStatusLabel(isUploading, jobData?.status);
  const isIndeterminate = jobData?.status === 'queued' || isUploading;

  return (
    <Box>
      <PageHeader
        title="Upload Reports"
        subtitle="Ingest Excel spreadsheets into the RAG vector store for AI analysis."
      />

      <Stack spacing={3}>

        {/* ── Upload Zone Card ─────────────────────────────────────────────── */}
        <Card
          sx={{
            borderRadius: `${radius.card}px`,
            boxShadow: shadows.card,
            border: 'none',
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.25 }}>
                Upload Files
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Drop your Excel reports here. Files will be processed and indexed automatically.
              </Typography>
            </Box>

            <UploadDropzone
              onFilesSelected={handleFilesSelected}
              disabled={isUploading || Boolean(isJobActive)}
            />

            {/* ── Progress section ─────────────────────────────────────────── */}
            {(showProgress || jobData) && (
              <Box
                sx={{
                  mt: 3,
                  p: 2.5,
                  borderRadius: `${radius.chip}px`,
                  bgcolor: (t) => t.palette.mode === 'light' ? neutral[50] : 'rgba(255,255,255,0.03)',
                  border: (t) => `1px solid ${t.palette.divider}`,
                }}
              >
                {/* Status row */}
                <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
                  <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {getStatusIcon(isUploading ? 'indexing' : jobData?.status)}
                    </Box>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {statusLabel || 'Processing…'}
                    </Typography>
                  </Stack>
                  {!isUploading && !isIndeterminate && (
                    <Typography variant="body2" sx={{ fontWeight: 700, color: brand.orange }}>
                      {progressValue}%
                    </Typography>
                  )}
                </Stack>

                {/* Progress bar */}
                <LinearProgress
                  variant={isIndeterminate ? 'indeterminate' : 'determinate'}
                  value={isIndeterminate ? undefined : progressValue}
                  sx={{
                    height: 8,
                    borderRadius: `${radius.full}px`,
                    bgcolor: (t) => t.palette.mode === 'light' ? neutral[200] : 'rgba(255,255,255,0.08)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor:
                        jobData?.status === 'completed'
                          ? semantic.success
                          : jobData?.status === 'failed'
                          ? semantic.error
                          : brand.orange,
                      borderRadius: `${radius.full}px`,
                    },
                  }}
                />

                {/* Completed message */}
                {jobData?.status === 'completed' && (
                  <Stack direction="row" spacing={1} sx={{ alignItems: 'center', mt: 1.5 }}>
                    <CheckCircle2 size={14} color={semantic.success} />
                    <Typography variant="caption" sx={{ color: semantic.successDark, fontWeight: 600 }}>
                      {jobData.indexed_documents != null
                        ? `Successfully indexed ${jobData.indexed_documents} documents.`
                        : 'Processing completed successfully.'}
                    </Typography>
                  </Stack>
                )}

                {/* Failed message */}
                {jobData?.status === 'failed' && jobData.error_message && (
                  <Stack direction="row" spacing={1} sx={{ alignItems: 'flex-start', mt: 1.5 }}>
                    <XCircle size={14} color={semantic.error} style={{ marginTop: 1, flexShrink: 0 }} />
                    <Typography variant="caption" sx={{ color: semantic.errorDark }}>
                      {jobData.error_message}
                    </Typography>
                  </Stack>
                )}
              </Box>
            )}
          </CardContent>
        </Card>

        {/* ── Upload History Card ──────────────────────────────────────────── */}
        <Card
          sx={{
            borderRadius: `${radius.card}px`,
            boxShadow: shadows.card,
            border: 'none',
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 2.5 }}>
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.25 }}>
                  Upload History
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  All upload and indexing jobs, newest first.
                </Typography>
              </Box>
              {jobsHistory?.jobs && jobsHistory.jobs.length > 0 && (
                <Chip
                  label={`${jobsHistory.jobs.length} job${jobsHistory.jobs.length !== 1 ? 's' : ''}`}
                  size="small"
                  sx={{
                    bgcolor: brand.orangeSubtle,
                    color: brand.orange,
                    fontWeight: 700,
                    fontSize: '0.7rem',
                    borderRadius: `${radius.full}px`,
                    border: `1px solid ${brand.orange}33`,
                  }}
                />
              )}
            </Stack>

            {historyLoading ? (
              <Stack spacing={2.5}>
                {[1, 2, 3].map((i) => (
                  <Stack key={i} direction="row" spacing={2} sx={{ alignItems: 'flex-start' }}>
                    <Skeleton variant="rounded" width={44} height={44} sx={{ borderRadius: `${radius.chip}px`, flexShrink: 0 }} />
                    <Box sx={{ flex: 1 }}>
                      <Skeleton width="55%" height={16} sx={{ mb: 0.75 }} />
                      <Skeleton width="35%" height={13} />
                    </Box>
                    <Skeleton variant="rounded" width={76} height={22} sx={{ borderRadius: 1 }} />
                  </Stack>
                ))}
              </Stack>
            ) : jobsHistory?.jobs && jobsHistory.jobs.length > 0 ? (
              <Box>
                {jobsHistory.jobs.map((job, idx) => (
                  <JobHistoryItem key={job.job_id} job={job} isFirst={idx === 0} />
                ))}
              </Box>
            ) : (
              <EmptyState
                icon={<FileSpreadsheet size={32} />}
                title="No Upload History"
                description="Upload Excel reports above to see them listed here."
              />
            )}
          </CardContent>
        </Card>

      </Stack>

      {/* Spin keyframe for active loader */}
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </Box>
  );
}
