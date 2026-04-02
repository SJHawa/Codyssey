# week01-문제 6 미션 컴퓨터 리턴즈

#1단계: 필요 모듈 임포트
import random
import datetime

#2단계: DummySensor 클래스 및 초기화 정의
class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

#3단계: set_env() 메소드 구현
#set_env() 메소드를 추가하여, 요구된 각 센서의 데이터 범위에 맞춰 무작위 실수(random.uniform())를 생성하고 env_values에 할당
    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = random.uniform(18.0, 30.0)
        self.env_values['mars_base_external_temperature'] = random.uniform(0.0, 21.0)
        self.env_values['mars_base_internal_humidity'] = random.uniform(50.0, 60.0)
        self.env_values['mars_base_external_illuminance'] = random.uniform(500.0, 715.0)
        self.env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)
        self.env_values['mars_base_internal_oxygen'] = random.uniform(4.0, 7.0)

#4단계: get_env() 메소드 및 보너스 과제(로그 기록) 구현
#get_env() 메소드는 env_values를 반환. 반환하기 전, datetime을 이용해 현재 시간을 구하고 센서 값들과 함께 텍스트 파일(sensor_log.txt)에 추가(append) 모드로 기록하는 로직을 구현
    def get_env(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # f-string 내부에서 홑따옴표 충돌을 막기 위해 변수로 먼저 분리
        t_in = self.env_values['mars_base_internal_temperature']
        t_out = self.env_values['mars_base_external_temperature']
        h_in = self.env_values['mars_base_internal_humidity']
        ill_out = self.env_values['mars_base_external_illuminance']
        co2_in = self.env_values['mars_base_internal_co2']
        o2_in = self.env_values['mars_base_internal_oxygen']
        
        # 파일 분리 없이 get_env() 호출 시 로그 형태로 터미널에 같이 출력
        log_message = f'[LOG] {now} | 화성 기지 내부 온도: {t_in:.2f} | 화성 기지 외부 온도: {t_out:.2f} | 화성 기지 내부 습도: {h_in:.2f} | 화성 기지 외부 광량: {ill_out:.2f} | 화성 기지 내부 이산화탄소 농도: {co2_in:.4f} | 화성 기지 내부 산소 농도: {o2_in:.2f}'
        print(log_message)
        print('-' * 60) # 선
            
        return self.env_values

#5단계: 인스턴스 생성 및 테스트
#클래스 외부에서 ds라는 인스턴스를 만들고, set_env()와 get_env()를 차례로 호출하여 결과를 화면에 출력
if __name__ == '__main__':
    ds = DummySensor()
    ds.set_env()
    
    current_environment = ds.get_env()
    
    # 터미널 출력
    for key, value in current_environment.items():
        print(f'{key}: {value:.2f}')