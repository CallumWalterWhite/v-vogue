// services/IUploadService.ts

export interface IUploadService {
    /**
     * Uploads a file to a specified URL.
     * @param file The file object to upload.
     * @param onProgress Optional callback to track upload progress (0 to 100).
     * @returns A promise that resolves with the server response.
     */
    uploadFile(
      file: FileObject,
      onProgress?: (progress: number) => void
    ): Promise<UploadResponse>;
  }
  
  /**
   * Represents a file object.
   */
  export interface FileObject {
    uri: string;
  }
  
  /**
   * Represents the server's response after a successful upload.
   */
  export interface UploadResponse {
    filename: string;
    correlation_id: string | null;
    upload_id: string; // UUID as string
  }
  