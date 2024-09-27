import axios, { AxiosProgressEvent } from 'axios';
import { API_BASE_URL } from '../../config';
import { FileUploadStatus, FileUploadStatusResponse, IUploadStatusService } from './IUploadStatusService';

export class UploadStatusService implements IUploadStatusService {
  private uploadStatusUrl: string;

  constructor() {
    this.uploadStatusUrl = `${API_BASE_URL}/file`;
  }

  async checkStatusFile(
    fileStatus: FileUploadStatus,
    onProgress?: (progress: number) => void
  ): Promise<FileUploadStatusResponse> {
    try {
      const fileStatusUploadUrl = `${this.uploadStatusUrl}/${fileStatus.fileId}/status`;
      const response = await axios.get<FileUploadStatusResponse>(fileStatusUploadUrl, {
        params: {
          file_id: fileStatus.fileId,
        }
      });
      if (onProgress && response.data.progression) {
        const progress = Math.round((response.data.progression * 100) / 100);
        onProgress(progress);
      }
      return response.data;
    } catch (error: any) {
      throw error.response?.data || error.message;
    }
  }
}
