import React, { useState } from 'react';
import { View, Button, Alert } from 'react-native';
import FileSelector from './FileSelector'; 
import { IGetModelService } from '@/services/models/IGetModelService';

interface DualFileSelectorProps {
  model1Service: IGetModelService;
  model2Service: IGetModelService;
  onSubmit: (selectedModel1: string | null, selectedModel2: string | null) => void;
}

const DualFileSelector: React.FC<DualFileSelectorProps> = ({ model1Service, model2Service, onSubmit }) => {
  const [selectedModel1, setSelectedModel1] = useState<string | null>(null);
  const [selectedModel2, setSelectedModel2] = useState<string | null>(null);

  const handleFileSelect1 = (modelId: string | null) => {
    setSelectedModel1(modelId);
  };

  const handleFileSelect2 = (modelId: string | null) => {
    setSelectedModel2(modelId);
  };

  const handleSubmit = () => {
    if (selectedModel1 && selectedModel2) {
      onSubmit(selectedModel1, selectedModel2);
    } else {
      Alert.alert('Error', 'Please select a file from both selectors.');
    }
  };

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <FileSelector modelService={model1Service} onSelect={handleFileSelect1} />
      <FileSelector modelService={model2Service} onSelect={handleFileSelect2} />
      
      <Button title="Submit" onPress={handleSubmit} />
    </View>
  );
};

export default DualFileSelector;
