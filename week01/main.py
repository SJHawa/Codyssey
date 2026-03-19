# week01-01 미션 컴퓨터를 복구하고 사고 원인을 파악해 보자

try:
    # 파일 읽기 (한 줄씩 리스트로 저장)
    with open('mission_computer_main.log', 'r', encoding = 'utf-8') as file:
        lines = file.readlines()

    # ===== 전체 로그 출력 =====
    print('===== 전체 로그 출력 =====')
    for line in lines:
        print(line, end = '')

    # ===== 시간 역순 정렬 =====
    reverse_lines = sorted(lines, reverse = True)

    print('\n===== 전체 로그 (시간 역순) =====')
    for line in reverse_lines:
        print(line, end = '')

    # ===== 문제 로그 필터링 =====
    problem_logs = []

    for line in lines:
        if 'unstable' in line or 'explosion' in line:
            problem_logs.append(line)

    # 🔥 문제 로그도 시간 역순 정렬
    reverse_problem_logs = sorted(problem_logs)

    # ===== 문제 로그 파일 저장 =====
    with open('error_log.txt', 'w', encoding = 'utf-8') as out_file:
        for line in reverse_problem_logs:
            out_file.write(line)

    print('\n===== 문제 로그 저장 완료 =====')

# ===== 예외 처리 =====
except FileNotFoundError:
    print('파일을 찾을 수 없습니다.')

except PermissionError:
    print('파일을 열 권한이 없습니다.')

except UnicodeDecodeError:
    print('파일 encoding 값을 다시 확인하세요.')

except Exception as e:
    print('파일 처리 중 알 수 없는 오류가 발생했습니다.')
    print(f'에러 내용: {e}')