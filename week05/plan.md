# Implementation Plan: Week05 MissionComputer System Info And Load

## Overview
이번 작업은 `week04/mars_mission_computer.py`의 `MissionComputer` 클래스를 기반으로, 시스템 상태를 확인하는 두 개의 메소드 `get_mission_computer_info()`와 `get_mission_computer_load()`를 추가하고, 이를 호출하는 실행 진입점까지 포함한 `week05/mars_mission_computer.py`를 완성하는 것이다. 필수 요구사항은 시스템 정보와 실시간 부하 정보를 JSON 형식으로 출력하는 것이며, 예외 처리와 스타일 가이드 준수까지 함께 만족해야 한다.

## Architecture Decisions
- `MissionComputer`의 기존 구조는 재사용하고, 주차별 산출물 분리를 위해 `week05/mars_mission_computer.py`에 독립 복사 후 확장한다.
- 정적 시스템 정보는 표준 라이브러리인 `platform`, `os`, `json` 중심으로 수집하는 방향을 우선 검토한다.
- 실시간 CPU 및 메모리 사용량은 표준 라이브러리만으로는 정확하고 이식성 있는 구현이 까다로우므로, 요구사항 허용 범위 안에서 `psutil` 사용 가능성을 먼저 검토한다.
- 출력 형식은 기존 주차와 일관되게 사람이 읽기 쉬운 JSON pretty print 형태로 통일한다.
- 시스템 정보 조회부는 실패 가능성이 있으므로 메소드 내부에서 예외를 처리하고, 실패한 항목도 JSON에 반영할 수 있도록 설계한다.

## Task List

### Phase 1: Foundation
- [ ] Task 1: 기존 `MissionComputer` 코드와 week05 요구사항의 차이를 정리하고 재사용 범위를 확정한다.
- [ ] Task 2: `week05/mars_mission_computer.py` 파일을 만들고, week04 기반 클래스 뼈대를 옮긴 뒤 이번 문제에 필요 없는 센서 루프 로직의 유지 여부를 결정한다.

### Checkpoint: Foundation
- [ ] week05 산출물 파일 경로와 클래스 이름, 실행 진입점 구조가 확정되어 있다.
- [ ] 구현 대상 메소드와 재사용 대상 코드가 분리되어 있다.

### Phase 2: Core Features
- [ ] Task 3: `get_mission_computer_info()`를 구현해 운영체계, 운영체계 버전, CPU 타입, CPU 코어 수, 메모리 크기를 수집하고 JSON으로 출력한다.
- [ ] Task 4: `get_mission_computer_load()`를 구현해 CPU 실시간 사용량과 메모리 실시간 사용량을 수집하고 JSON으로 출력한다.
- [ ] Task 5: 각 메소드에 예외 처리와 항목별 fallback 값을 추가해 조회 실패 시에도 프로그램이 중단되지 않게 한다.

### Checkpoint: Core Features
- [ ] 두 메소드가 모두 독립 호출 가능하다.
- [ ] 정상 경로와 예외 경로 모두 JSON 출력 형식이 유지된다.

### Phase 3: Runtime And Verification
- [ ] Task 6: `runComputer = MissionComputer()` 인스턴스를 생성하고 두 메소드를 순서대로 호출하는 실행 코드를 추가한다.
- [ ] Task 7: 문자열 스타일, 네이밍, 공백, 들여쓰기, import 구성을 정리해 명세와 PEP 8을 만족시킨다.
- [ ] Task 8: 로컬 실행으로 출력 결과를 확인하고, 필요하면 플랫폼별 차이를 반영해 보정한다.

### Checkpoint: Complete
- [ ] `week05/mars_mission_computer.py` 실행 시 시스템 정보와 부하 정보가 JSON으로 출력된다.
- [ ] 예외 처리, 파일 위치, 인스턴스 이름 요구사항까지 충족한다.

## Detailed Tasks

## Task 1: Reuse baseline and define scope

**Description:**  
`week04/mars_mission_computer.py`의 현재 구조를 검토해 이번 문제에서 유지할 부분과 제거 또는 단순화할 부분을 정한다. 특히 센서 수집 중심 로직이 이번 시스템 정보 조회 문제와 직접 관련이 있는지 판단해, 불필요한 코드 이식으로 복잡도가 커지지 않도록 범위를 확정한다.

**Acceptance criteria:**
- [ ] `MissionComputer` 클래스의 재사용 범위가 정리되어 있다.
- [ ] week05 구현 파일 생성 전략이 결정되어 있다.
- [ ] 실행 진입점에서 요구하는 인스턴스 이름 `runComputer` 사용이 계획에 반영되어 있다.

**Verification:**
- [ ] 수동 확인: [week04/mars_mission_computer.py](/Users/simjeonghwa/Documents/GitHub/Codyssey/week04/mars_mission_computer.py:1) 구조와 [week05/q1.md](/Users/simjeonghwa/Documents/GitHub/Codyssey/week05/q1.md:1) 요구사항 차이를 비교한다.
- [ ] 수동 확인: week05 산출물이 신규 파일 생성인지 기존 파일 수정인지 명확히 결정한다.

**Dependencies:** None

**Files likely touched:**
- `week05/mars_mission_computer.py`
- `week05/plan.md`

**Estimated scope:** Small

## Task 2: Create the week05 runtime skeleton

**Description:**  
week05 전용 파이썬 파일을 만들고 `MissionComputer` 클래스, 공통 JSON 출력 헬퍼, 실행 진입점을 구성한다. 이 단계에서는 메소드 시그니처와 파일 구조를 먼저 고정해 이후 정보 수집 로직이 안정적으로 들어갈 수 있게 한다.

**Acceptance criteria:**
- [ ] `week05/mars_mission_computer.py`가 생성되어 있다.
- [ ] `MissionComputer` 클래스와 `runComputer` 실행 진입점이 정의되어 있다.
- [ ] `get_mission_computer_info()`와 `get_mission_computer_load()` 시그니처가 준비되어 있다.

**Verification:**
- [ ] 수동 확인: 파일에 클래스와 `if __name__ == '__main__':` 블록이 존재한다.
- [ ] 실행 확인: `python3 week05/mars_mission_computer.py` 실행 시 메소드 미구현 오류 없이 최소한의 구조가 동작한다.

**Dependencies:** Task 1

**Files likely touched:**
- `week05/mars_mission_computer.py`

**Estimated scope:** Small

## Task 3: Implement system information collection

**Description:**  
정적 시스템 정보 조회 메소드 `get_mission_computer_info()`를 구현한다. 운영체계 이름, 운영체계 버전, CPU 타입, CPU 코어 수, 메모리 크기를 수집하고, 결과를 딕셔너리로 정리한 뒤 JSON으로 출력한다.

**Acceptance criteria:**
- [ ] 운영체계 이름이 출력된다.
- [ ] 운영체계 버전이 출력된다.
- [ ] CPU 타입이 출력된다.
- [ ] CPU 코어 수가 출력된다.
- [ ] 메모리 크기가 출력된다.
- [ ] 결과가 JSON 형식으로 출력된다.

**Verification:**
- [ ] 실행 확인: `python3 week05/mars_mission_computer.py`에서 시스템 정보 JSON이 출력된다.
- [ ] 수동 확인: JSON 키 이름과 값이 요구사항 5개 항목을 모두 포함한다.

**Dependencies:** Task 2

**Files likely touched:**
- `week05/mars_mission_computer.py`

**Estimated scope:** Medium

## Task 4: Implement live load collection

**Description:**  
실시간 시스템 부하 조회 메소드 `get_mission_computer_load()`를 구현한다. CPU 실시간 사용량과 메모리 실시간 사용량을 조회하고, 결과를 JSON 형식으로 출력한다. 정확도와 구현 복잡도를 고려해 표준 라이브러리 우선 검토 후, 필요 시 `psutil` 사용을 반영한다.

**Acceptance criteria:**
- [ ] CPU 실시간 사용량이 출력된다.
- [ ] 메모리 실시간 사용량이 출력된다.
- [ ] 결과가 JSON 형식으로 출력된다.
- [ ] 사용한 수집 방식이 현재 환경에서 실행 가능하다.

**Verification:**
- [ ] 실행 확인: `python3 week05/mars_mission_computer.py`에서 부하 정보 JSON이 출력된다.
- [ ] 수동 확인: 출력 값이 숫자 또는 해석 가능한 문자열 형태로 표시된다.

**Dependencies:** Task 2

**Files likely touched:**
- `week05/mars_mission_computer.py`

**Estimated scope:** Medium

## Task 5: Add defensive exception handling

**Description:**  
시스템 정보 및 부하 조회 과정에서 플랫폼 차이, 권한 문제, 라이브러리 부재 등으로 실패할 수 있는 지점을 예외 처리한다. 프로그램 전체가 종료되지 않도록 보호하고, 실패한 항목은 `N/A` 또는 오류 메시지 형태로 일관되게 반환한다.

**Acceptance criteria:**
- [ ] 정보 조회 실패 시 프로그램이 비정상 종료하지 않는다.
- [ ] 예외 상황에서도 JSON 출력 형식이 유지된다.
- [ ] 실패한 항목의 fallback 표현이 일관된다.

**Verification:**
- [ ] 수동 확인: try/except가 메소드 내부에 포함되어 있다.
- [ ] 수동 확인: 조회 실패 분기에서도 반환 구조가 유지된다.

**Dependencies:** Task 3, Task 4

**Files likely touched:**
- `week05/mars_mission_computer.py`

**Estimated scope:** Small

## Task 6: Wire the required runtime flow

**Description:**  
문제 명세대로 `MissionComputer` 클래스를 `runComputer`라는 이름으로 인스턴스화하고, `get_mission_computer_info()`와 `get_mission_computer_load()`를 호출하는 실행 흐름을 완성한다. 사용자가 파일을 직접 실행했을 때 요구된 출력이 바로 보이도록 마무리한다.

**Acceptance criteria:**
- [ ] `runComputer = MissionComputer()` 코드가 존재한다.
- [ ] `runComputer.get_mission_computer_info()` 호출이 존재한다.
- [ ] `runComputer.get_mission_computer_load()` 호출이 존재한다.
- [ ] 직접 실행 시 두 JSON 출력이 순서대로 나타난다.

**Verification:**
- [ ] 실행 확인: `python3 week05/mars_mission_computer.py`
- [ ] 수동 확인: 인스턴스 변수명이 명세와 동일하게 `runComputer`다.

**Dependencies:** Task 5

**Files likely touched:**
- `week05/mars_mission_computer.py`

**Estimated scope:** Small

## Task 7: Final style and spec compliance pass

**Description:**  
문자열 작은따옴표 사용, 공백 규칙, import 정리, 함수명과 변수명, 주석 최소화 등 스타일 요구사항을 최종 점검한다. 동시에 외부 패키지 사용 여부가 명세와 충돌하지 않는지도 다시 확인한다.

**Acceptance criteria:**
- [ ] 문자열 표현이 가이드에 맞게 정리되어 있다.
- [ ] PEP 8 기준에서 눈에 띄는 위반이 없다.
- [ ] 명세와 충돌하는 불필요한 코드가 제거되어 있다.

**Verification:**
- [ ] 수동 확인: 파일 전반의 문자열, 공백, 들여쓰기를 점검한다.
- [ ] 실행 확인: 스타일 정리 후에도 `python3 week05/mars_mission_computer.py`가 정상 실행된다.

**Dependencies:** Task 6

**Files likely touched:**
- `week05/mars_mission_computer.py`

**Estimated scope:** Small

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| CPU 실시간 사용량을 표준 라이브러리만으로 정확히 구하기 어렵다 | High | `psutil` 사용 가능 여부를 먼저 검토하고, 불가 시 플랫폼 종속 구현 또는 제한사항을 명시한다 |
| 메모리 크기/사용량 조회 방식이 운영체제별로 다르다 | Medium | 공통 API 우선 사용 후, 실패 시 fallback 값과 예외 처리를 둔다 |
| week04 코드를 그대로 가져오면 불필요한 센서 기능이 남아 복잡해질 수 있다 | Medium | 이번 요구사항과 직접 관련 없는 로직은 분리 또는 제거한다 |
| 외부 라이브러리 사용 조건 해석이 모호하다 | Medium | 구현 전 “시스템 정보 조회 부분은 별도 라이브러리 사용 가능” 문장을 기준으로 사용 범위를 최소화한다 |

## Open Questions
- `psutil` 같은 외부 라이브러리를 실제 제출 환경에서 사용할 수 있는지 확인이 필요하다.
- 기존 week04 센서 관련 기능을 week05 파일에 함께 유지할지, 이번 문제 요구사항만 남긴 단순 버전으로 구성할지 결정이 필요하다.
- 메모리 크기와 사용량의 단위를 바이트, MB, GB 중 무엇으로 통일할지 구현 전에 정하는 것이 좋다.
