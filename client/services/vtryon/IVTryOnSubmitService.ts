export interface IVTryOnSubmitService {
    createSubmission(request: VTryOnRequest): Promise<VTryOnSubmissionResponse>;
}

export interface VTryOnRequest {
    model_upload_id: string;
    cloth_upload_id: string;
}

export interface VTryOnSubmissionResponse {
    upload_id: string;
}