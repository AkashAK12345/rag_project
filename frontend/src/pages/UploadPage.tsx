// src/pages/UploadPage.tsx
import { useState } from 'react';
import { Box, Card, CardContent, Typography, Stack, LinearProgress, Divider, List, ListItem, ListItemText, ListItemIcon } from '@mui/material';
import { Description, History } from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import { PageHeader } from '@/components/common/PageHeader';
import { UploadDropzone } from '@/components/common/UploadDropzone';
import { StatusChip } from '@/components/common/StatusChip';
import { EmptyState } from '@/components/common/EmptyState';
import { useUpload } from '@/hooks/useUpload';
import { useJobPolling, useJobs } from '@/hooks/useJobs';
import dayjs from 'dayjs';

export function UploadPage() {
  const { enqueueSnackbar } = useSnackbar();
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const { mutate: uploadFiles, isPending: isUploading } = useUpload();
  const { data: jobData } = useJobPolling(activeJobId);
  const { data: jobsHistory } = useJobs();

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

  // Determine effective progress and status
  const isJobActive = jobData && ['queued', 'validating', 'saving_files', 'indexing'].includes(jobData.status);
  const showProgress = isUploading || isJobActive;
  const progressValue = isUploading ? uploadProgress : jobData?.progress_percentage || 0;
  
  let statusText = 'Idle';
  if (isUploading) statusText = 'Uploading files to server...';
  else if (jobData?.status === 'queued') statusText = 'Queued for background processing...';
  else if (jobData?.status === 'validating') statusText = 'Validating files...';
  else if (jobData?.status === 'saving_files') statusText = 'Saving files...';
  else if (jobData?.status === 'indexing') statusText = `Indexing documents (${jobData.progress_percentage}%)...`;
  else if (jobData?.status === 'completed') statusText = 'Processing completed successfully.';
  else if (jobData?.status === 'failed') statusText = 'Processing failed.';

  return (
    <Box>
      <PageHeader
        title="Upload Reports"
        subtitle="Ingest Excel reports into the RAG vector store for analysis."
      />

      <Stack spacing={4}>
        <Card>
          <CardContent>
            <UploadDropzone
              onFilesSelected={handleFilesSelected}
              disabled={isUploading || isJobActive}
            />

            {(showProgress || jobData) && (
              <Box sx={{ mt: 4 }}>
                <Stack direction="row" sx={{ justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {statusText}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {progressValue}%
                  </Typography>
                </Stack>
                <LinearProgress 
                  variant={jobData?.status === 'queued' ? 'indeterminate' : 'determinate'} 
                  value={progressValue} 
                  sx={{ height: 8, borderRadius: 4 }}
                />
                
                {jobData?.status === 'failed' && (
                  <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                    Error: {jobData.error_message}
                  </Typography>
                )}
              </Box>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Upload History
            </Typography>
            {jobsHistory?.jobs && jobsHistory.jobs.length > 0 ? (
              <List sx={{ p: 0 }}>
                {jobsHistory.jobs.map((job, idx) => (
                  <Box key={job.job_id}>
                    {idx > 0 && <Divider />}
                    <ListItem sx={{ py: 2, px: 0 }}>
                      <ListItemIcon>
                        <Description color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`Job ${job.job_id}`}
                        secondary={
                          <>
                            <Typography component="span" variant="body2" color="text.primary">
                              {job.uploaded_files.join(', ')}
                            </Typography>
                            <br />
                            {dayjs(job.created_at).format('MMM D, YYYY HH:mm:ss')} • {job.indexed_documents || 0} docs indexed
                          </>
                        }
                      />
                      <StatusChip status={job.status} />
                    </ListItem>
                  </Box>
                ))}
              </List>
            ) : (
              <EmptyState
                icon={<History />}
                title="No History"
                description="Upload reports to see them listed here."
              />
            )}
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
}
