import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, Image } from 'react-native';
import { IGetModelService, UploadedModelResponse } from '@/services/models/IGetModelService';

interface FileSelectorProps {
  modelService: IGetModelService;
  onSelect: (selectedModel: string | null) => void;
}

const FileSelector: React.FC<FileSelectorProps> = ({ modelService, onSelect }) => {
  const [models, setModels] = useState<UploadedModelResponse[]>([]);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);

  useEffect(() => {
    modelService.getAllModels().then((data) => {
      setModels(data);
    });
  }, [modelService]);

  const handleSelect = (uploadId: string) => {
    setSelectedModel(uploadId);
    onSelect(uploadId); // Notify parent about the selected model
  };

  const renderModelItem = ({ item }: { item: UploadedModelResponse }) => {
    return (
      <TouchableOpacity onPress={() => handleSelect(item.upload_id)} style={{ padding: 10 }}>
        <Image
          source={{ uri: item.url }}
          style={{
            width: 100,
            height: 100,
            borderColor: selectedModel === item.upload_id ? 'blue' : 'gray',
            borderWidth: 2,
          }}
        />
        <Text>{item.filename}</Text>
      </TouchableOpacity>
    );
  };

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <FlatList
        data={models}
        keyExtractor={(item) => item.upload_id}
        renderItem={renderModelItem}
        numColumns={2}
      />
    </View>
  );
};

export default FileSelector;
