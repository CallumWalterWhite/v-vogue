from abc import ABC, abstractmethod
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

class StorageManager(ABC):
    @abstractmethod
    def get_file(self, file_path: str) -> bytes:
        pass
    
    @abstractmethod
    def get_file_path(self, file_path: str) -> str:
        pass

    @abstractmethod
    def create_file(self, file_path: str, content: bytes):
        pass

    @abstractmethod
    def update_file(self, file_path: str, content: bytes):
        pass

    @abstractmethod
    def delete_file(self, file_path: str):
        pass
    
class LocalStorageManager(StorageManager):
    def __init__(self, base_directory: str):
        self.base_directory = base_directory

    def _get_full_path(self, file_path: str) -> str:
        return os.path.join(self.base_directory, file_path)

    def get_file(self, file_path: str) -> bytes:
        full_path = self._get_full_path(file_path)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as file:
                return file.read()
        else:
            raise FileNotFoundError(f"File {file_path} not found in local storage.")
        
    def get_file_path(self, file_path: str) -> str:
        return self._get_full_path(file_path)

    def create_file(self, file_path: str, content: bytes):
        full_path = self._get_full_path(file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as file:
            file.write(content)

    def update_file(self, file_path: str, content: bytes):
        self.create_file(file_path, content)

    def delete_file(self, file_path: str):
        full_path = self._get_full_path(file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        else:
            raise FileNotFoundError(f"File {file_path} not found in local storage.")

class AzureBlobStorageManager(StorageManager):
    def __init__(self, connection_string: str, container_name: str):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)

    def get_file(self, file_path: str):
        blob_client = self.container_client.get_blob_client(file_path)
        try:
            downloader = blob_client.download_blob()
            return downloader.readall()
        except Exception as e:
            raise FileNotFoundError(f"File {file_path} not found in Azure Blob storage. Error: {e}")

    def create_file(self, file_path: str, content: bytes):
        blob_client = self.container_client.get_blob_client(file_path)
        blob_client.upload_blob(content, overwrite=True)

    def update_file(self, file_path: str, content: bytes):
        self.create_file(file_path, content)

    def delete_file(self, file_path: str):
        blob_client = self.container_client.get_blob_client(file_path)
        blob_client.delete_blob()

class StorageManagerFactory:
    @staticmethod
    def get_storage_manager(setting: str, **kwargs) -> StorageManager:
        """
        Returns the appropriate StorageManager instance based on the given setting.
        
        :param setting: Can be "local" or "azure".
        :param kwargs: Additional arguments for the specific storage manager.
        :return: An instance of a subclass of StorageManager.
        """
        if setting == "local":
            base_directory = kwargs.get("base_directory", "./")
            return LocalStorageManager(base_directory=base_directory)
        
        elif setting == "azure":
            connection_string = kwargs.get("connection_string")
            container_name = kwargs.get("container_name")
            
            if not connection_string or not container_name:
                raise ValueError("Azure Blob storage requires both a connection_string and container_name.")
            
            return AzureBlobStorageManager(connection_string=connection_string, container_name=container_name)
        
        else:
            raise ValueError(f"Unsupported storage setting: {setting}")