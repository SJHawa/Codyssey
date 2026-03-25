#week01-문제 3 인화 물질을 찾아라
def main():
    # 1. 파일 경로 변수
    file_path_read = 'Mars_Base_Inventory_List.csv'
    file_path_danger = 'Mars_Base_Inventory_danger.csv'
    file_path_bin = 'Mars_Base_Inventory_List.bin'
    
    inventory_list = []
    header = []

    # [과제 1 & 2] 파일 읽기 및 리스트 객체로 변환
    try:
        with open(file_path_read, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            print('--- 원본 CSV 파일 내용 ---')
            for line in lines:
                print(line.strip())
            
            # 첫 번째 줄 제목(Header) 분리
            header = lines[0].strip().split(',')
            
            # 두 번째 줄(데이터) 반복문 실행
            for line in lines[1:]:
                row = line.strip().split(',')
                
                # 데이터가 5개 열로 잘 들어있는지 확인
                if len(row) >= 5:
                    try:
                        # Flammability(인화성)= 5번째(인덱스 4) str -> float 변환
                        row[4] = float(row[4])
                        inventory_list.append(row)
                    except ValueError:
                        # 숫자로 바꿀 수 없는 이상한 데이터는 무시하고 넘어감 (예외 처리)
                        pass
            
            #리스트 예: inventory_list = ['Alcohol', '0.789', '0.79', 'Very weak', 0.85]
    
    except FileNotFoundError:
        print('파일을 찾을 수 없습니다')
        return

    # [과제 3] 인화성이 높은 순으로 정렬 (내림차순)
    # x[4] -> 5번째 값인 Flammability를 기준으로 정렬
    inventory_list.sort(key=lambda x: x[4], reverse=True)

    # [과제 4] 인화성 지수가 0.7 이상인 목록 추출 및 출력
    danger_list = []
    print('\n--- 인화성 지수 0.7 이상 위험 물질 목록 ---')
    for item in inventory_list:
        if item[4] >= 0.7:
            danger_list.append(item)
            print(item)

    # [과제 5] 위험 물질 목록을 CSV 포맷으로 저장
    try:
        with open(file_path_danger, 'w', encoding='utf-8') as f:
            # 제목 먼저 파일에 쓰기
            f.write(', '.join(header) + '\n')
            
            for item in danger_list:
                # 파일 입력을 위해 float -> str 변환 , 쉼표로 연결
                str_row = [str(x) for x in item]
                #item 리스트 안에 있는 요소(x)을 하나씩 꺼내서 전부 문자열(str)로 바꿈
                #join은 리스트 안에 있는 글자들을 하나로 합쳐줌. 앞에 있는 ','는 합칠 때 중간에 쉼표 추가하게함
                
                f.write(','.join(str_row) + '\n')
                
    except Exception as e:
        print('에러 발생', e)

    # [보너스 1] 인화성 순서로 정렬된 배열의 내용을 이진 파일형태로 저장
    try:
        with open(file_path_bin, 'wb') as f:
            #'wb' (Write Binary): 이진 파일 쓰기 모드
            for item in inventory_list:
                str_row = ', '.join([str(x) for x in item]) + '\n'
                #item 리스트 안에 있는 요소(x)을 하나씩 꺼내서 전부 문자열(str)로 바꿈
                #join은 리스트 안에 있는 글자들을 하나로 합쳐줌. 앞에 있는 ','는 합칠 때 중간에 쉼표 추가하게함
                
                f.write(str_row.encode('utf-8'))
                # 이진 파일에는 문자열 그대로 쓸 수 없으므로 encode('utf-8')로 바이트로 변환
                
        print('이진 파일(bin)로 저장')
    except Exception as e:
        print('에러 발생', e)

    # [보너스 2] 저장된 이진 파일을 다시 읽어 들여서 화면에 출력
    try:
        with open(file_path_bin, 'rb') as f:
            #'rb' (Read Binary): 이진 파일 읽기 모드
            bin_data = f.read()
            
            print('\n--- 이진 파일(bin) 결과 ---')
            
            print(bin_data.decode('utf-8'))
            # 바이트 데이터를 다시 사람이 읽을 수 있는 문자로 decode
            
    except Exception as e:
        print('에러 발생', e)
        
if __name__ == '__main__':
    main()
