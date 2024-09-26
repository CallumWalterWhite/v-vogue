// services/AxiosUploadService.ts

import axios, { AxiosProgressEvent } from 'axios';
import { IUploadService, FileObject, UploadResponse } from './IUploadService';

export class BaseAxiosUploadService implements IUploadService {
  private uploadUrl: string;

  constructor(uploadUrl: string) {
    this.uploadUrl = uploadUrl;
  }

  async uploadFile(
    file: FileObject,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> {
    const formData = new FormData();
    const response = await fetch(file.uri);
    const blob = await response.blob();
    formData.append('file', blob);
    try {
      const response = await axios.post<UploadResponse>(this.uploadUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent: AxiosProgressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      });
      return response.data;
    } catch (error: any) {
      throw error.response?.data || error.message;
    }
  }
}
