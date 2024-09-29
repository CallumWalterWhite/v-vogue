import axios, { AxiosProgressEvent } from 'axios';
import { IVTryOnSubmitService, VTryOnRequest, VTryOnSubmissionResponse } from './IVTryOnSubmitService';
import { API_BASE_URL } from '@/config';

export class VTryOnSubmitService implements IVTryOnSubmitService {
  private submitUrl: string;

  constructor() {
    this.submitUrl = `${API_BASE_URL}/viton/submit`
  }
    async createSubmission(request: VTryOnRequest): Promise<VTryOnSubmissionResponse> {
        try {
        const response = await axios.post<VTryOnSubmissionResponse>(this.submitUrl, request, {
            headers: {
            'Content-Type': 'application/json',
            }
        });
        return response.data;
        } catch (error: any) {
        throw error.response?.data || error.message;
        }
    }
}
