import { API_BASE_URL } from "@/config";
import { BaseGetModelService } from "./BaseGetModelService";

export class GetModelService extends BaseGetModelService {
    constructor() {
        super(`${API_BASE_URL}/uploadfile/models`);
    }
}
