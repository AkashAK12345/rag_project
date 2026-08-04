// src/components/common/UploadDropzone.tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Button, Stack } from '@mui/material';
import { UploadCloud } from 'lucide-react';
import { brand, neutral, semantic } from '@/theme/colors';
import { radius } from '@/theme/radius';

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

  const borderColor = isDragReject
    ? semantic.error
    : isDragActive
    ? brand.orange
    : neutral[200];

  const bgColor = isDragReject
    ? semantic.errorSubtle
    : isDragActive
    ? brand.orangeSubtle
    : 'transparent';

  return (
    <Box
      {...getRootProps()}
      sx={{
        border: `2px dashed ${borderColor}`,
        bgcolor: bgColor,
        borderRadius: `${radius.card}px`,
        p: { xs: 4, sm: 6 },
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'all 200ms ease',
        opacity: disabled ? 0.6 : 1,
        '&:hover': !disabled
          ? {
              bgcolor: brand.orangeSubtle,
              borderColor: brand.orange,
              transform: 'translateY(-1px)',
            }
          : {},
      }}
    >
      <input {...getInputProps()} />
      <Stack sx={{ alignItems: 'center', gap: 2.5 }}>
        <Box
          sx={{
            width: 72,
            height: 72,
            borderRadius: `${radius.avatar}px`,
            bgcolor: isDragReject ? semantic.errorSubtle : brand.orangeSubtle,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <UploadCloud
            size={32}
            color={isDragReject ? semantic.error : brand.orange}
          />
        </Box>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.75 }}>
            {isDragActive
              ? isDragReject
                ? 'Invalid file type'
                : 'Drop files here'
              : 'Drag & drop Excel files'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Supports <strong>.xls</strong> and <strong>.xlsx</strong> formats only.
          </Typography>
        </Box>
        <Button
          variant="contained"
          disabled={disabled}
          sx={{ px: 4, py: 1.25, borderRadius: `${radius.button}px`, fontWeight: 700 }}
        >
          Browse Files
        </Button>
      </Stack>
    </Box>
  );
}
