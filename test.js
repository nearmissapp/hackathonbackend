import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Modal,
  Alert,
  Image,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';


export default function PhotoRegistration() {
  const [comment, setComment] = useState('');
  const [location, setLocation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRegistered, setIsRegistered] = useState(false);
  const router = useRouter();
  const { email } = useLocalSearchParams();


  if (!email) {
    Alert.alert('오류', '로그인 이메일이 전달되지 않았습니다.');
    router.back();
    return null;
  }


  const imageUri =
    Platform.OS === 'web'
      ? '/assets/images/chick.png'
      : Image.resolveAssetSource(require('../../assets/images/chick.png')).uri;


  const handleRegister = async () => {
    setIsLoading(true);

    try {
      const formData = new FormData();

      formData.append('reporter', email as string);
      formData.append('comment', comment);
      formData.append('location', location);

      if (Platform.OS === 'web') {
        const response = await fetch(imageUri);
        const blob = await response.blob();
        formData.append('image', blob, 'photo.jpg');
      } else {
        formData.append('image', {
          uri: imageUri,
          type: 'image/jpeg',
          name: 'photo.jpg',
        } as any);
      }

      const response = await fetch('https://charmed-hare-scarcely.ngrok-free.app/call-gpt', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
        body: formData,
      });

      if (response.ok) {
        setIsRegistered(true);
      } else {
        const errorText = await response.text();
        console.error('Server response:', errorText);
        Alert.alert('오류', '잠재위험을 등록하지 못했습니다.');
      }
    } catch (error) {
      console.error('Error:', error);
      Alert.alert('오류', '서버와의 연결에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>잠재위험 등록하기</Text>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={styles.backButton}>뒤로가기</Text>
        </TouchableOpacity>
      </View>


      <View style={styles.imagePlaceholder}>
        <Image source={require('../../assets/images/chick.png')} style={styles.previewImage} />
      </View>


      <View style={styles.inputContainer}>
        <TextInput
          style={styles.commentInput}
          placeholder="코멘트를 입력하세요"
          value={comment}
          onChangeText={setComment}
        />
      </View>


      <View style={styles.locationContainer}>
        <Text style={styles.infoLabel}>위치정보</Text>
        <TextInput
          style={styles.locationInput}
          placeholder="위치정보를 입력하세요"
          value={location}
          onChangeText={setLocation}
        />
      </View>


      <TouchableOpacity style={styles.submitButton} onPress={handleRegister}>
        <Text style={styles.submitButtonText}>잠재위험 등록</Text>
      </TouchableOpacity>


      <Modal visible={isLoading} animationType="fade" transparent={true}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>등록 중입니다...</Text>
          <ActivityIndicator size="large" color="#007BFF" />
        </View>
      </Modal>


      <Modal visible={isRegistered} animationType="slide" transparent={false}>
        <View style={styles.modalContainer}>
          <Text style={styles.modalText}>등록 완료 되었습니다!</Text>
          <TouchableOpacity
            style={styles.homeButton}
            onPress={() => {
              setIsRegistered(false);
              router.push('/main_user');
            }}
          >
            <Text style={styles.homeButtonText}>홈으로 가기</Text>
          </TouchableOpacity>
        </View>
      </Modal>
    </View>
  );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 40,
    marginBottom: 20,
  },
  backButton: {
    fontSize: 16,
    color: '#007BFF',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  imagePlaceholder: {
    width: '100%',
    height: 200,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    backgroundColor: '#f9f9f9',
  },
  previewImage: {
    width: '100%',
    height: '100%',
    borderRadius: 10,
  },
  inputContainer: {
    marginBottom: 20,
  },
  commentInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 10,
    padding: 10,
    fontSize: 16,
    color: '#333',
  },
  locationContainer: {
    marginBottom: 20,
  },
  infoLabel: {
    fontSize: 16,
    color: '#333',
    fontWeight: 'bold',
    marginBottom: 10,
  },
  locationInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 10,
    padding: 10,
    fontSize: 16,
    marginBottom: 10,
  },
  submitButton: {
    backgroundColor: '#FB514B',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  submitButtonText: {
    fontSize: 18,
    color: '#fff',
    fontWeight: 'bold',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FB514B',
  },
  loadingText: {
    fontSize: 22,
    color: '#fff',
    marginBottom: 20,
    textAlign: 'center',
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  modalText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  homeButton: {
    backgroundColor: '#FB514B',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 20,
  },
  homeButtonText: {
    fontSize: 18,
    color: '#fff',
    fontWeight: 'bold',
  },
});



