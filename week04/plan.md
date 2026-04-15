# Implementation Plan: Week04 MissionComputer With Bonus Tasks

## Summary
- `MissionComputer`를 `week04/mars_mission_computer.py`에 구현한다.
- `DummySensor`는 `week03/mars_mission_computer.py`에서 재사용한다.
- 필수 요구사항과 보너스 과제인 종료 입력, 5분 평균 출력까지 모두 포함한다.

## Key Changes
- `MissionComputer` 클래스에 6개 환경 키를 가진 `env_values`를 둔다.
- `ds`로 `DummySensor` 인스턴스를 보관하고 `get_sensor_data()`에서 주기적으로 값을 갱신한다.
- 현재 환경값은 JSON 형태로 출력한다.
- 5초 간격 반복 루프를 유지한다.
- `q` 입력 시 반복을 중단하고 종료 메시지를 출력한다.
- 최근 5분 샘플 기준 평균값을 5분마다 별도로 출력한다.
- 실행 진입점에서 `RunComputer = MissionComputer()`를 만들고 `RunComputer.get_sensor_data()`를 호출한다.

## Task Breakdown
### Task 1: Reuse strategy and runtime constraints
- `DummySensor`를 표준 라이브러리 import 방식으로 재사용한다.
- 외부 패키지 없이 입력 감시와 평균 집계를 처리한다.

### Task 2: MissionComputer base structure
- `env_values`, `ds`, 종료 상태, 평균 계산용 샘플 저장소를 초기화한다.

### Task 3: Current sensor polling flow
- 센서 갱신, `env_values` 반영, JSON 출력, 샘플 적재, 주기 대기를 반복한다.

### Task 4: Stop input bonus behavior
- 별도 입력 감시 스레드에서 `q` 입력을 감지해 안전하게 루프를 종료한다.

### Task 5: Five-minute averaging bonus behavior
- 최근 5분 샘플만 유지하고, 5분마다 평균값을 계산해 출력한다.

### Task 6: Runtime entrypoint and graceful shutdown
- 직접 실행 시 루프가 시작되도록 하고, `KeyboardInterrupt`도 자연스럽게 종료 처리한다.

### Task 7: Style and spec compliance
- 작은따옴표, PEP 8, 기본 라이브러리 사용 조건을 지킨다.

## Test Plan
- `MissionComputer` 생성 시 6개 키가 모두 초기화되는지 확인한다.
- 실행 시 현재 환경값이 JSON으로 반복 출력되는지 확인한다.
- `q` 입력 시 루프가 중단되고 종료 메시지가 한 번 출력되는지 확인한다.
- 5분 경과 후 평균값이 별도로 출력되는지 확인한다.
- `DummySensor` 재사용 방식이 기존 `week03` 동작을 깨뜨리지 않는지 확인한다.

## Assumptions
- 종료 키는 `q`로 고정한다.
- 종료 메시지는 `System stopped....`를 사용한다.
- 평균은 최근 5분 동안 수집된 실제 샘플 기준으로 계산한다.
