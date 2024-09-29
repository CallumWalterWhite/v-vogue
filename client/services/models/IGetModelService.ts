export interface IGetModelService {
    getAllModels(): Promise<UploadedModelResponse[]>;
}

export interface UploadedModelResponse {
    filename: string;
    file_path: string;
    upload_id: string;
    url: string;
}