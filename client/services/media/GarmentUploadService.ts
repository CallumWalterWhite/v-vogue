import { API_BASE_URL } from '../../config';
import { BaseAxiosUploadService } from './BaseAxiosUploadService';

export class GarmentUploadService extends BaseAxiosUploadService {
  constructor() {
    super(`${API_BASE_URL}/uploadfile/garment`);
  }
}
