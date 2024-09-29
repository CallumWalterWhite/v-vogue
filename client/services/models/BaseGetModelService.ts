import axios from 'axios';
import { IGetModelService, UploadedModelResponse } from './IGetModelService';
import { API_BASE_URL } from '@/config';

const arrayBufferToBase64 = (buffer: ArrayBuffer): string => {
    const binary = String.fromCharCode(...new Uint8Array(buffer));
    return btoa(binary);
};

export class BaseGetModelService implements IGetModelService {
  private getModelUrl: string;

  private showModelUrl: string;

  constructor(getModelUrl: string, showModelUrl: string = "uploadfile") {
    this.getModelUrl = getModelUrl;
    this.showModelUrl = showModelUrl;
  }
    async getAllModels(): Promise<UploadedModelResponse[]> {
        try {
            const fileStatusUploadUrl = `${this.getModelUrl}?is_completed=true`;
            const response = await axios.get<UploadedModelResponse[]>(fileStatusUploadUrl);
            response.data.forEach((model) => {
                model.url = `${API_BASE_URL}/${this.showModelUrl}/${model.upload_id}/show`;
            })
            return response.data;
        } catch (error: any) {
            throw error.response?.data || error.message;
        }
    }
}
