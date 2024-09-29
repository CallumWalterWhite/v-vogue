import { IGetModelService, UploadedModelResponse } from '@/services/models/IGetModelService';
import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, Image, Modal } from 'react-native';

interface FileListProps {
    modelService: IGetModelService;
}

const FileList: React.FC<FileListProps> = ({ modelService }) => {
    const [models, setModels] = useState<UploadedModelResponse[]>([]);
    const [selectedImage, setSelectedImage] = useState<string | null>(null); 

    useEffect(() => {
        modelService.getAllModels().then((data) => {
            setModels(data);
        });
    }, [modelService]);

    const handlePreview = (imageUrl: string) => {
        setSelectedImage(imageUrl); 
    };

    const renderModelItem = ({ item }: { item: UploadedModelResponse }) => {
        return (
            <TouchableOpacity onPress={() => handlePreview(item.url)} style={{ padding: 10 }}>
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
            />
            {selectedImage && (
                <Modal
                    animationType="slide"
                    transparent={true}
                    visible={!!selectedImage}
                    onRequestClose={() => setSelectedImage(null)}
                >
                    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
                        <View style={{ width: '80%', height: '80%', backgroundColor: 'white', padding: 10 }}>
                            <Image
                                source={{ uri: selectedImage }}
                                style={{ width: '100%', height: '100%', resizeMode: 'contain' }}
                            />
                        </View>
                    </View>
                </Modal>
            )}
        </View>
    );
};

export default FileList;
