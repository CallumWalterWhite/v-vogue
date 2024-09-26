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

interface FileUploaderProps {
  uploadService: IUploadService;
}

const FileUploader: React.FC<FileUploaderProps> = ({ uploadService }) => {
  const [file, setFile] = useState<FileObject | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [response, setResponse] = useState<UploadResponse | null>(null);

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

      {response && (
        <View style={styles.responseContainer}>
          <Text style={styles.responseText}>Upload Response:</Text>
          <Text style={styles.responseContent}>
            Filename: {response.filename}{'\n'}
            Correlation ID: {response.correlation_id}{'\n'}
            Upload ID: {response.upload_id}
          </Text>
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
