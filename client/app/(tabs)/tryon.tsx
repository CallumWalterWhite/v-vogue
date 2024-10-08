// HomeScreen.tsx

import React from 'react';
import { Image, StyleSheet } from 'react-native';

import ParallaxScrollView from '@/components/ParallaxScrollView';
import { GetModelService } from '@/services/models/GetModelService';
import { GetGarmentService } from '@/services/models/GetGarmentService';
import { VTryOnSubmitService } from '@/services/vtryon/VTryOnSubmitService';
import DualFileSelector from '@/components/media/DuelFileSelector';

export default function TryOnScreen() {
  const modelUploadService = new GetModelService();
  const garmentUploadService = new GetGarmentService();
  const vTryOnSubmitService = new VTryOnSubmitService();

  const handleSubmission = (selectedModel1: string | null, selectedModel2: string | null) => {
    if (selectedModel1 && selectedModel2) {
      vTryOnSubmitService
        .createSubmission({
            model_upload_id: selectedModel1,
            cloth_upload_id: selectedModel2,
        })
        .then((response) => {
          console.log(response);
        });
    }
  };

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
        <DualFileSelector model1Service={modelUploadService} model2Service={garmentUploadService} onSubmit={handleSubmission} />
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
