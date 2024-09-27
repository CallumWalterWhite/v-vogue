// HomeScreen.tsx

import React, { useState } from 'react';
import { Image, StyleSheet, Platform, TouchableOpacity, Text, View } from 'react-native';

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import FileUploader from '@/components/media/FileUploader';
import { ModelUploadService } from '@/services/media/ModelUploadService';
import { UploadStatusService } from '@/services/media/UploadStatusService';
import { GarmentUploadService } from '@/services/media/GarmentUploadService';

export default function HomeScreen() {
  const [currentService, setCurrentService] = useState<'axios' | 'fetch'>('axios');
  const modelUploadService = new ModelUploadService();
  const garmentUploadService = new GarmentUploadService();
  const uploadStatusService = new UploadStatusService();
  const modelUploadRequriesPostProgressing: boolean = true;
  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#A1CEDC', dark: '#1D3D47' }}
      headerImage={
        <Image
          source={require('@/assets/images/partial-react-logo.png')}
          style={styles.reactLogo}
        />
      }
    >
      <FileUploader uploadService={modelUploadService} uploadStatusService={uploadStatusService} requiresPostProgressing={modelUploadRequriesPostProgressing} />
      <FileUploader uploadService={garmentUploadService} uploadStatusService={uploadStatusService} requiresPostProgressing={true} />
    </ParallaxScrollView>
  );
}

const styles = StyleSheet.create({
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  stepContainer: {
    gap: 8,
    marginBottom: 8,
  },
  reactLogo: {
    height: 178,
    width: 290,
    bottom: 0,
    left: 0,
    position: 'absolute',
  },
  toggleContainer: {
    flexDirection: 'row',
    marginVertical: 20,
    justifyContent: 'center',
  },
  toggleButton: {
    backgroundColor: '#E0E0E0',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 5,
    marginHorizontal: 10,
  },
  activeToggleButton: {
    backgroundColor: '#2196F3',
  },
  toggleButtonText: {
    color: '#fff',
    fontSize: 14,
  },
});
