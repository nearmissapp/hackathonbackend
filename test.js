import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, FlatList } from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';


// 타입 정의
type ResponseDataItem = {
  id: number; // 고유 ID
  comment: string; // 댓글 내용
  created_at: string; // 생성일시
  status: string; // 상태 (completed/in-progress)
  image_compressed_base64 : string;
};


export default function MainManScreen() {
  const router = useRouter();
  const { email } = useLocalSearchParams(); // 로그인 시 전달받은 email
  const [reports, setReports] = useState<ResponseDataItem[]>([]); // 신고 내역 상태


  useEffect(() => {
    // 신고 내역 API 호출
    const fetchReports = async () => {
      try {
        const formData = new FormData();
        formData.append('manager', email as string);


        const response = await fetch('https://charmed-hare-scarcely.ngrok-free.app/list-manager', {
          method: 'POST',
          body: formData,
        });


        const data = await response.json();


        if (response.ok && data.data) {
          setReports(data.data); // 신고 내역 설정
        } else {
          setReports([]); // 데이터가 없을 경우 초기화
        }
      } catch (error) {
        console.error('Failed to fetch reports:', error);
        setReports([]); // 오류 발생 시 초기화
      }
    };


    fetchReports();
  }, [email]);


  const renderReportItem = ({ item }: { item: ResponseDataItem }) => (
    <View style={styles.card}>
      <View style={styles.contentContainer}>
        <View style={styles.textContainer}>
          <Text style={styles.reportTitle}>{item.comment}</Text>
          <Text style={styles.reportDate}>
            {new Date(item.created_at).toLocaleDateString('ko-KR')}
          </Text>
        </View>
        {item.image_compressed_base64 && (
          <Image
            source={{ uri: `data:image/jpeg;base64,${item.image_compressed_base64}` }}
            style={styles.reportImage}
          />
        )}
      </View>
      <Text
        style={[
          styles.statusBadge,
          item.status === 'completed' ? styles.completed : styles.inProgress,
        ]}
      >
        {item.status === 'completed' ? '완료' : '진행중'}
      </Text>
    </View>
  );


  return (
    <View style={styles.container}>
      {/* 상단바 */}
      <View style={styles.topBar}>
        <TouchableOpacity>
          <Image source={require('../../assets/images/chick.png')} style={styles.icon} />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => router.push('/')}>
          <Image source={require('../../assets/images/chick.png')} style={styles.icon} />
        </TouchableOpacity>
      </View>


      {/* 병아리 이미지 및 텍스트 */}
      <View style={styles.profileSection}>
        <Image source={require('../../assets/images/chick.png')} style={styles.chickImage} />
        <Text style={styles.levelText}>Lv. 2 조치자 페이지</Text>
        {/* 게이지 */}
        <View style={styles.levelBarContainer}>
          <View style={styles.levelBarBackground} />
          <View style={[styles.levelBarProgress, { width: '75%' }]} />
        </View>
      </View>


      {/* 등록한 위험요인 */}
      <Text style={styles.sectionTitle}>등록한 위험요인</Text>
      {reports.length > 0 ? (
        <FlatList
          data={reports}
          renderItem={renderReportItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
        />
      ) : (
        <Text style={styles.noDataText}>등록된 신고 내역이 없습니다.</Text>
      )}


      {/* 플로팅 버튼 */}
      <TouchableOpacity
        style={styles.floatingButton}
        onPress={() => router.push('/test')}
      >
        <Text style={styles.floatingButtonText}>+</Text>
      </TouchableOpacity>
    </View>
  );
}


const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#ffffff',
  },
  icon: { width: 24, height: 24 },
  profileSection: {
    alignItems: 'center',
    marginVertical: 20,
  },
  chickImage: {
    width: 120,
    height: 120,
  },
  levelText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
    marginVertical: 10,
  },
  levelBarContainer: {
    width: '60%',
    height: 15,
    marginTop: 10,
    position: 'relative',
    backgroundColor: '#E0E0E0',
    borderRadius: 10,
    overflow: 'hidden',
  },
  levelBarBackground: {
    backgroundColor: '#E0E0E0',
    width: '100%',
    height: '100%',
    borderRadius: 10,
  },
  levelBarProgress: {
    backgroundColor: '#4CAF50',
    height: '100%',
    position: 'absolute',
    left: 0,
    top: 0,
  },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', marginVertical: 15, paddingHorizontal: 10 },
  listContainer: {
    paddingHorizontal: 10,
  },
  card: {
    padding: 10,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    marginBottom: 10,
    elevation: 2,
  },
  contentContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  textContainer: {
    flex: 1,
    marginRight: 10,
  },
  reportImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
  },
  reportTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  reportDate: {
    fontSize: 14,
    color: '#777',
  },
  statusBadge: {
    fontSize: 12,
    fontWeight: 'bold',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  completed: {
    backgroundColor: '#4CAF50',
    color: '#fff',
  },
  inProgress: {
    backgroundColor: '#FF6347',
    color: '#fff',
  },
  noDataText: {
    textAlign: 'center',
    color: '#777',
    marginVertical: 20,
    fontSize: 16,
  },
  floatingButton: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    backgroundColor: '#FF6347',
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  floatingButtonText: { fontSize: 24, color: '#ffffff' },
});




