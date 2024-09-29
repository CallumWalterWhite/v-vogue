import { API_BASE_URL } from "@/config";
import { BaseGetModelService } from "./BaseGetModelService";

export class GetVTryOnService extends BaseGetModelService {
    constructor() {
        super(`${API_BASE_URL}/viton/outputs`, `viton`);
    }
}
