import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import {
  UploadCloud,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader,
} from 'lucide-react';

import { uploadBatchCSV, formatApiError } from '../api/api';
import { useAuth } from '../context/AuthContext';

const BatchUploader = ({ onBatchComplete }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const { token } = useAuth();

  const onDrop = useCallback((acceptedFiles) => {
    setError('');
    setSuccessMsg('');

    const selected = acceptedFiles[0];
    if (!selected) return;

    if (selected.name.toLowerCase().endsWith('.csv')) {
      setFile(selected);
    } else {
      setFile(null);
      setError('Please upload a valid .csv file.');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError('');
    setSuccessMsg('');

    try {
      const response = await uploadBatchCSV(file, token);

      if (!response || response.success === false) {
        throw new Error('The backend could not process this dataset.');
      }

      const processedRows =
        response?.metadata?.final_rows ??
        response?.prediction_summary?.records ??
        0;

      setSuccessMsg(
        `Successfully processed ${processedRows.toLocaleString()} rows.`
      );

      if (onBatchComplete) {
        onBatchComplete(response);
      }
    } catch (err) {
      console.error('Batch upload failed:', err);
      setError(formatApiError(err, 'Failed to process the CSV file.'));
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError('');
    setSuccessMsg('');
  };

  return (
    <div className="glass-card p-6 flex flex-col h-full relative overflow-hidden">
      <h3 className="text-2xl font-bold text-white mb-2">
        Organization Batch Processing
      </h3>

      <p className="text-gray-400 text-sm mb-6">
        Upload an organizational{' '}
        <span className="text-neon-green font-mono">.csv</span> file to run
        carbon emission predictions and generate real dataset analytics.
      </p>

      <div
        {...getRootProps()}
        className={`flex-1 flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-8 transition-colors cursor-pointer text-center ${
          isDragActive
            ? 'border-neon-green bg-neon-green/5'
            : 'border-white/20 hover:border-white/40 hover:bg-white/5 bg-black/20'
        } ${file ? 'border-blue-500 bg-blue-500/5' : ''}`}
      >
        <input {...getInputProps()} />

        {file ? (
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="flex flex-col items-center"
          >
            <div className="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center mb-4">
              <FileText className="w-8 h-8 text-blue-400" />
            </div>

            <p className="text-white font-medium mb-1">{file.name}</p>

            <p className="text-gray-400 text-sm">
              {(file.size / 1024).toFixed(1)} KB
            </p>

            <button
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                handleRemoveFile();
              }}
              className="mt-3 text-xs text-red-400 hover:text-red-300"
            >
              Remove file
            </button>
          </motion.div>
        ) : (
          <div className="flex flex-col items-center">
            <div
              className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors ${
                isDragActive ? 'bg-neon-green/20' : 'bg-white/5'
              }`}
            >
              <UploadCloud
                className={`w-8 h-8 ${
                  isDragActive ? 'text-neon-green' : 'text-gray-400'
                }`}
              />
            </div>

            <p className="text-white font-medium mb-1">
              {isDragActive ? 'Drop your CSV here' : 'Drag & drop a CSV file'}
            </p>

            <p className="text-gray-400 text-sm">Or click to browse your files</p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 flex items-start">
          <AlertCircle className="w-5 h-5 text-red-400 mr-2 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-200">{error}</p>
        </div>
      )}

      {successMsg && (
        <div className="mt-4 p-3 rounded-lg bg-neon-green/10 border border-neon-green/30 flex items-start">
          <CheckCircle className="w-5 h-5 text-neon-green mr-2 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-green-200">{successMsg}</p>
        </div>
      )}

      <button
        type="button"
        onClick={handleUpload}
        disabled={!file || isUploading}
        className={`mt-6 w-full py-3 rounded-lg font-bold flex items-center justify-center transition-all ${
          !file || isUploading
            ? 'bg-white/5 text-gray-500 cursor-not-allowed'
            : 'bg-neon-green text-deep-blue hover:bg-green-400 shadow-[0_0_15px_rgba(57,255,20,0.3)]'
        }`}
      >
        {isUploading ? (
          <>
            <Loader className="w-5 h-5 mr-2 animate-spin" />
            Processing Dataset...
          </>
        ) : (
          'Run Carbon Prediction'
        )}
      </button>

      {isUploading && (
        <div className="absolute bottom-0 left-0 h-1 bg-neon-green w-full origin-left animate-pulse" />
      )}
    </div>
  );
};

export default BatchUploader;