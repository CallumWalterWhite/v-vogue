import { API_BASE_URL } from "@/config";
import { BaseGetModelService } from "./BaseGetModelService";

export class GetGarmentService extends BaseGetModelService {
    constructor() {
        super(`${API_BASE_URL}/uploadfile/garments`);
    }
}
