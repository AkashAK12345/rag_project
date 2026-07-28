// src/components/common/UploadDropzone.tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Button, Stack } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

interface UploadDropzoneProps {
  onFilesSelected: (files: File[]) => void;
  disabled?: boolean;
}

export function UploadDropzone({ onFilesSelected, disabled }: UploadDropzoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFilesSelected(acceptedFiles);
      }
    },
    [onFilesSelected]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    disabled,
  });

  return (
    <Box
      {...getRootProps()}
      sx={{
        border: (t) => `2px dashed ${isDragActive ? t.palette.primary.main : t.palette.divider}`,
        bgcolor: (t) => (isDragActive ? `${t.palette.primary.main}11` : 'background.paper'),
        borderRadius: 3,
        p: 6,
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'all 0.2s ease',
        '&:hover': {
          bgcolor: (t) => (!disabled ? `${t.palette.primary.main}08` : undefined),
          borderColor: (t) => (!disabled ? t.palette.primary.main : undefined),
        },
      }}
    >
      <input {...getInputProps()} />
      <Stack sx={{ alignItems: 'center', gap: 2 }}>
        <CloudUpload sx={{ fontSize: 64, color: isDragReject ? 'error.main' : 'primary.main' }} />
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {isDragActive
              ? isDragReject
                ? 'Invalid file type'
                : 'Drop the files here...'
              : 'Drag & drop Excel files here'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Only .xls and .xlsx files are supported.
          </Typography>
        </Box>
        <Button variant="contained" disabled={disabled} sx={{ mt: 2 }}>
          Select Files
        </Button>
      </Stack>
    </Box>
  );
}
