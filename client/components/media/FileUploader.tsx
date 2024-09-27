// components/FileUploader.tsx

import React, { useState } from 'react';
import {
  View,
  TouchableOpacity,
  Image,
  StyleSheet,
  ActivityIndicator,
  Text,
  Alert,
} from 'react-native';
import { IUploadService, FileObject, UploadResponse } from '../../services/media/IUploadService';
import { launchImageLibrary, ImageLibraryOptions } from 'react-native-image-picker';
import { FileUploadStatus, IUploadStatusService, FileUploadStatusResponse } from '@/services/media/IUploadStatusService';

interface FileUploaderProps {
  uploadService: IUploadService;
  requiresPostProgressing?: boolean;
  uploadStatusService?: IUploadStatusService;
}

const FileUploader: React.FC<FileUploaderProps> = ({ uploadService, requiresPostProgressing, uploadStatusService }) => {
  const [file, setFile] = useState<FileObject | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [postProcessing, setPostProcessing] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [postProgress, setPostProgress] = useState<number>(0);
  const [response, setResponse] = useState<UploadResponse | null>(null);
  const [postProcessingResponse, setPostProcessingResponse] = useState<FileUploadStatusResponse | null>(null);

  /**
   * Opens the image library for the user to select an image.
   */
  const selectFile = () => {
    const options: ImageLibraryOptions = {
      mediaType: 'photo',
      quality: 1,
      includeBase64: true,
    };

    launchImageLibrary(options, (responsePicker) => {
      if (responsePicker.didCancel) {
        console.log('User cancelled image picker');
      } else if (responsePicker.errorMessage) {
        console.error('ImagePicker Error: ', responsePicker.errorMessage);
        Alert.alert('Error', responsePicker.errorMessage);
      } else if (responsePicker.assets && responsePicker.assets.length > 0) {
        console.log('User selected: ', responsePicker.assets[0]);
        const asset = responsePicker.assets[0];
        if (asset.uri) {
          console.log('Asset URI: ', asset.uri);
          const selectedFile: FileObject = {
            uri: asset.uri
          };
          setFile(selectedFile);
        } else {
          Alert.alert('Error', 'Invalid file selected');
        }
      }
    });
  };

  /**
   * Initiates the file upload process.
   */
  const uploadFile = async () => {
    if (!file) {
      Alert.alert('No File Selected', 'Please select a file to upload.');
      return;
    }

    setUploading(true);
    setProgress(0);
    setResponse(null);

    try {
      const serverResponse: UploadResponse = await uploadService.uploadFile(file, setProgress);
      setResponse(serverResponse);
      Alert.alert('Success', 'File uploaded successfully!');
    } catch (error: any) {
      console.error('Upload Error:', error);
      Alert.alert('Upload Failed', typeof error === 'string' ? error : 'There was an error uploading the file.');
    } finally {
      setUploading(false);
    }

    if (requiresPostProgressing && uploadStatusService && response?.upload_id) {
      setPostProcessing(true);
      setPostProgress(0);
      
      try {
        const fileStatus: FileUploadStatus = {
          fileId: response!.upload_id,
        };
    
        const checkProgression = async () => {
          try {
            const postProcessingResponse: FileUploadStatusResponse = await uploadStatusService.checkStatusFile(fileStatus, setPostProgress);
    
            if (postProcessingResponse.has_error) {
              clearInterval(intervalId);
              Alert.alert('Post Processing Failed', postProcessingResponse.error_message);
              setPostProcessing(false);
              setPostProcessingResponse(postProcessingResponse);
            }
    
            if (postProcessingResponse.has_completed) {
              clearInterval(intervalId);
              Alert.alert('Success', 'File post-processing completed!');
              setPostProcessing(false);
              setPostProcessingResponse(postProcessingResponse);
            }
          } catch (error: any) {
            clearInterval(intervalId);
            console.error('Post Processing Error:', error);
            Alert.alert('Post Processing Failed', typeof error === 'string' ? error : 'There was an error post-processing the file.');
            setPostProcessing(false);
          }
        };
    
        const intervalId = setInterval(checkProgression, 1000); // Check every second
    
      } catch (error: any) {
        console.error('Post Processing Error:', error);
        Alert.alert('Post Processing Failed', typeof error === 'string' ? error : 'There was an error initiating post-processing.');
        setPostProcessing(false);
      }
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity style={styles.selectButton} onPress={selectFile}>
        {file ? (
          <Image source={{ uri: file.uri }} style={styles.image} />
        ) : (
          <Text style={styles.buttonText}>📁 Select Image</Text>
        )}
      </TouchableOpacity>

      {file && !uploading && (
        <TouchableOpacity style={styles.uploadButton} onPress={uploadFile}>
          <Text style={styles.buttonText}>⬆️ Upload</Text>
        </TouchableOpacity>
      )}

      {uploading && (
        <View style={styles.progressContainer}>
          <ActivityIndicator size="small" color="#0000ff" />
          <Text style={styles.progressText}>{progress}%</Text>
        </View>
      )}

      {postProcessing && (
        <View style={styles.progressContainer}>
          <ActivityIndicator size="small" color="#0000ff" />
          <Text style={styles.progressText}>{postProgress}%</Text>
        </View>
      )}

      {postProcessingResponse && (
        <View style={styles.responseContainer}>
          <Text style={styles.responseText}>Post Processing Response:</Text>
          {postProcessingResponse.has_error ? (
            <Text style={styles.responseContent}>{postProcessingResponse.error_message}</Text>
          ) : (
            <Text style={styles.responseContent}>Post processing completed successfully!</Text>
          )}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    margin: 20,
  },
  selectButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 10,
    marginVertical: 10,
    width: 150,
    alignItems: 'center',
  },
  uploadButton: {
    backgroundColor: '#2196F3',
    padding: 15,
    borderRadius: 10,
    marginVertical: 10,
    width: 150,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
  },
  image: {
    width: 100,
    height: 100,
    borderRadius: 10,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  progressText: {
    marginLeft: 10,
    fontSize: 16,
  },
  responseContainer: {
    marginTop: 20,
    alignItems: 'center',
    paddingHorizontal: 10,
  },
  responseText: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  responseContent: {
    textAlign: 'center',
    fontSize: 14,
  },
});

export default FileUploader;
