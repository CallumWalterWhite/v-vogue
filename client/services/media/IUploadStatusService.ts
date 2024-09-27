export interface IUploadStatusService {
    checkStatusFile(
      fileStatus: FileUploadStatus,
      onProgress?: (progress: number) => void
    ): Promise<FileUploadStatusResponse>;
  }
  export interface FileUploadStatus {
    fileId: string;
  }
  export interface FileUploadStatusResponse {
    file_id: string
    has_completed: boolean
    has_error: boolean
    error_message: string
    state: number
    progression: number
  }
  