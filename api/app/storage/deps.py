from fastapi import HTTPException
from app.storage.storage_manager import StorageManager, StorageManagerFactory
from app.core.config import settings

def get_storage_manager() -> StorageManager:
    storage_setting = settings.STORAGE_SETTING
    if storage_setting == "local":
        return StorageManagerFactory.get_storage_manager(setting="local", base_directory="./local_storage")
    elif storage_setting == "azure":
        return StorageManagerFactory.get_storage_manager(
            setting="azure", 
            connection_string="your-connection-string", 
            container_name="your-container"
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid storage setting")