// HomeScreen.tsx

import React, { useState } from 'react';
import { Image, StyleSheet, Platform, TouchableOpacity, Text, View } from 'react-native';

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

// Import the FileUploader component and upload services
import FileUploader from '@/components/media/FileUploader';
import { ModelUploadService } from '@/services/media/ModelUploadService';

// Define the upload URL (Replace with your actual server URL)
const UPLOAD_URL = 'http://10.0.2.2:8000/uploadfile/person'; // For Android Emulator
// const UPLOAD_URL = 'http://localhost:8000/uploadfile/person'; // For iOS Simulator or web

export default function HomeScreen() {
  // State to manage the current upload service
  const [currentService, setCurrentService] = useState<'axios' | 'fetch'>('axios');

  // Instantiate the upload services
  const axiosUploadService = new ModelUploadService();
  const fetchUploadService = new ModelUploadService();

  // Select the appropriate service based on currentService state
  const selectedUploadService = currentService === 'axios' ? axiosUploadService : fetchUploadService;

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
      <ThemedView style={styles.titleContainer}>
        <ThemedText type="title">Hello!</ThemedText>
        <HelloWave />
      </ThemedView>

      {/* Toggle Buttons to Switch Upload Services */}
      <ThemedView style={styles.toggleContainer}>
        <TouchableOpacity
          style={[
            styles.toggleButton,
            currentService === 'axios' && styles.activeToggleButton,
          ]}
          onPress={() => setCurrentService('axios')}
        >
          <Text style={styles.toggleButtonText}>Use Axios</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.toggleButton,
            currentService === 'fetch' && styles.activeToggleButton,
          ]}
          onPress={() => setCurrentService('fetch')}
        >
          <Text style={styles.toggleButtonText}>Use Fetch</Text>
        </TouchableOpacity>
      </ThemedView>

      {/* FileUploader Component */}
      <FileUploader uploadService={selectedUploadService} />

      {/* Existing Step Containers */}
      <ThemedView style={styles.stepContainer}>
        <ThemedText type="subtitle">Step 1: Try it</ThemedText>
        <ThemedText>
          Edit <ThemedText type="defaultSemiBold">app/(tabs)/index.tsx</ThemedText> to see changes.
          Press{' '}
          <ThemedText type="defaultSemiBold">
            {Platform.select({ ios: 'cmd + d', android: 'cmd + m' })}
          </ThemedText>{' '}
          to open developer tools.
        </ThemedText>
      </ThemedView>
      <ThemedView style={styles.stepContainer}>
        <ThemedText type="subtitle">Step 2: Explore</ThemedText>
        <ThemedText>
          Tap the Explore tab to learn more about what's included in this starter app.
        </ThemedText>
      </ThemedView>
      <ThemedView style={styles.stepContainer}>
        <ThemedText type="subtitle">Step 3: Get a fresh start</ThemedText>
        <ThemedText>
          When you're ready, run{' '}
          <ThemedText type="defaultSemiBold">npm run reset-project</ThemedText> to get a fresh{' '}
          <ThemedText type="defaultSemiBold">app</ThemedText> directory. This will move the current{' '}
          <ThemedText type="defaultSemiBold">app</ThemedText> to{' '}
          <ThemedText type="defaultSemiBold">app-example</ThemedText>.
        </ThemedText>
      </ThemedView>
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
