# Implementation Plan: Week07 Calculator Core And UI Integration

## Overview
이번 작업은 지난 주차에 만든 계산기 UI를 기반으로, 실제 계산을 담당하는 `Calculator` 코어를 설계하고 UI 버튼과 연결해 완전하게 동작하는 계산기를 만드는 것이다. 필수 범위는 사칙연산, 상태 초기화, 부호 전환, 퍼센트 처리, 소수점 입력, 결과 계산, 예외 처리까지이며, 최종 산출물은 `calculator.py`다.

## Architecture Decisions
- 이전 주차의 UI 코드는 재사용하되, 화면 위젯 중심 구조와 계산 상태 관리 로직을 분리해 유지보수성을 높인다.
- `Calculator` 클래스는 현재 입력값, 이전 값, 선택된 연산자, 새 입력 시작 여부, 오류 상태 같은 계산 상태를 인스턴스 변수로 관리한다.
- 숫자 표시와 내부 계산은 분리한다. 화면에는 문자열을 유지하고, 실제 연산 시에만 숫자 변환을 수행해 소수점 입력 흐름을 안정적으로 다룬다.
- `0으로 나누기`와 처리 가능한 숫자 범위 초과는 사용자에게 이해 가능한 오류 표시로 처리하고, 오류 후에는 `reset()`으로 정상 흐름에 복귀할 수 있게 한다.
- 결과 출력 형식은 정수면 정수처럼, 실수면 필요할 때만 소수점을 유지하되, 보너스 요구사항에 맞춰 소수점 6자리 반올림 규칙을 적용하는 방향을 우선 검토한다.
- 산출물 파일은 제출 단위를 분리하기 위해 `week07/calculator.py`로 관리하는 방안을 우선 사용한다.

## Task List

### Phase 1: Foundation
- [ ] Task 1: week06 UI 구조와 week07 요구사항 차이를 정리하고 재사용 범위를 확정한다.
- [ ] Task 2: 계산기 상태 모델과 메소드 책임을 설계한다.

### Checkpoint: Foundation
- [ ] UI 재사용 범위와 신규 구현 범위가 구분되어 있다.
- [ ] `Calculator`가 관리할 상태 값과 핵심 메소드 목록이 정리되어 있다.

### Phase 2: Core Engine
- [ ] Task 3: 사칙연산 메소드 `add()`, `subtract()`, `multiply()`, `divide()`를 구현한다.
- [ ] Task 4: 상태 제어 메소드 `reset()`, `negative_positive()`, `percent()`를 구현한다.
- [ ] Task 5: 숫자 및 소수점 입력 누적 로직을 구현한다.
- [ ] Task 6: `equal()`과 연산자 선택 흐름을 구현한다.

### Checkpoint: Core Engine
- [ ] 숫자 입력, 연산자 선택, 결과 계산이 클래스 단위에서 독립적으로 동작한다.
- [ ] 기본 예외 상황에서도 계산기가 비정상 종료하지 않는다.

### Phase 3: UI Integration And Verification
- [ ] Task 7: UI 버튼을 계산 코어 메소드와 연결해 전체 입력 흐름을 완성한다.
- [ ] Task 8: 표시 형식, 오류 처리, 동적 폰트 조절 같은 마무리 요소를 정리한다.
- [ ] Task 9: 실행 테스트와 예외 케이스 검증을 수행한다.

### Checkpoint: Complete
- [ ] `week07/calculator.py`가 실행 가능하다.
- [ ] 필수 요구사항과 주요 보너스 요구사항 충족 여부가 확인되었다.

## Detailed Tasks

## Task 1: Reuse the existing UI safely

**Description:**  
`week06/calculator.py`의 화면 구성, 버튼 배치, 입력 이벤트 구조를 검토해 이번 주차에서 그대로 가져갈 부분과 교체할 부분을 정한다. 특히 현재 구현이 문자열 누적 중심이라 실제 계산기 코어로 확장하기 어려운 부분을 찾아, 어디서 상태 관리 계층을 분리할지 결정한다.

**Acceptance criteria:**
- [ ] `week06/calculator.py`의 재사용 대상이 정리되어 있다.
- [ ] 버튼 레이아웃, 디스플레이 위젯, 이벤트 연결 방식 유지 여부가 결정되어 있다.
- [ ] `week07/calculator.py`를 신규 산출물로 둘지 확정되어 있다.

**Verification:**
- [ ] 수동 확인: [week06/calculator.py](/Users/simjeonghwa/Documents/GitHub/Codyssey/week06/calculator.py:1)의 UI 구조와 [week07/problem.md](/Users/simjeonghwa/Documents/GitHub/Codyssey/week07/problem.md:1) 요구사항을 비교한다.
- [ ] 수동 확인: 계산 로직과 UI 로직의 분리 지점을 문서 또는 구현 메모로 정리한다.

**Dependencies:** None

**Files likely touched:**
- `week07/plan.md`
- `week07/calculator.py`

**Estimated scope:** Small

## Task 2: Define calculator state and method contracts

**Description:**  
실제 계산에 필요한 상태를 설계한다. 현재 화면 문자열, 누적 계산값, 대기 중인 연산자, 다음 입력이 새 숫자로 시작되는지 여부, 오류 상태, 폰트 크기 갱신 기준 등을 정리하고, 각 메소드가 어떤 상태를 읽고 쓰는지 계약을 만든다.

**Acceptance criteria:**
- [ ] 상태 변수 목록이 정리되어 있다.
- [ ] `add()`, `subtract()`, `multiply()`, `divide()`, `reset()`, `negative_positive()`, `percent()`, `equal()`의 책임이 구분되어 있다.
- [ ] 입력 메소드와 연산 메소드 간 호출 순서가 정의되어 있다.

**Verification:**
- [ ] 수동 확인: 상태 전이 흐름을 숫자 입력, 연산자 입력, `=` 입력, 초기화 흐름 기준으로 설명할 수 있다.
- [ ] 수동 확인: 연산자 연속 입력, `=` 연속 입력, 소수점 중복 입력에 대한 처리 방침이 정해져 있다.

**Dependencies:** Task 1

**Files likely touched:**
- `week07/calculator.py`

**Estimated scope:** Small

## Task 3: Implement arithmetic operations

**Description:**  
사칙연산 메소드 `add()`, `subtract()`, `multiply()`, `divide()`를 구현한다. 이 메소드들은 계산 결과를 반환하거나 상태를 갱신할 수 있도록 일관된 인터페이스를 가져야 하며, 특히 `divide()`는 0으로 나누기와 숫자 범위 검사를 함께 처리할 수 있어야 한다.

**Acceptance criteria:**
- [ ] `add()`가 두 값의 합을 계산한다.
- [ ] `subtract()`가 두 값의 차를 계산한다.
- [ ] `multiply()`가 두 값의 곱을 계산한다.
- [ ] `divide()`가 두 값의 나눗셈을 계산한다.
- [ ] `divide()`에 0 입력 시 예외 또는 오류 상태가 일관되게 처리된다.

**Verification:**
- [ ] 실행 확인: 각 메소드가 대표 입력값에 대해 기대 결과를 반환한다.
- [ ] 수동 확인: `0`으로 나누기 시 프로그램이 종료되지 않고 오류 상태로 전환된다.
- [ ] 수동 확인: 매우 큰 값 연산 시 범위 초과 처리 기준이 적용된다.

**Dependencies:** Task 2

**Files likely touched:**
- `week07/calculator.py`

**Estimated scope:** Medium

## Task 4: Implement reset and state-changing helpers

**Description:**  
`reset()`, `negative_positive()`, `percent()`를 구현한다. 이 메소드들은 현재 화면 값과 내부 상태를 함께 다뤄야 하므로, 단순 문자열 변경이 아니라 계산기 전체 흐름과 맞물리게 설계한다.

**Acceptance criteria:**
- [ ] `reset()`이 화면 값과 내부 상태를 초기 상태로 되돌린다.
- [ ] `negative_positive()`가 현재 입력값의 부호를 전환한다.
- [ ] `percent()`가 현재 입력값을 백분율 값으로 변환한다.
- [ ] 오류 상태에서도 `reset()`으로 복구할 수 있다.

**Verification:**
- [ ] 실행 확인: 초기 화면이 `0`으로 복원된다.
- [ ] 수동 확인: 양수와 음수 입력 모두에서 부호 전환이 정상 동작한다.
- [ ] 수동 확인: `percent()` 적용 결과가 화면과 내부 계산값에 일관되게 반영된다.

**Dependencies:** Task 2

**Files likely touched:**
- `week07/calculator.py`

**Estimated scope:** Medium

## Task 5: Build robust number and decimal input handling

**Description:**  
숫자키와 소수점 입력이 요구사항대로 누적되도록 구현한다. 입력 중인 숫자를 별도로 관리해 선행 `0`, 연산자 직후 입력, 소수점 중복 입력, `=` 직후 새 숫자 입력 같은 상황에서 자연스럽게 동작하도록 만든다.

**Acceptance criteria:**
- [ ] 숫자 버튼 입력 시 현재 값이 누적된다.
- [ ] 첫 입력이 `0`일 때 불필요한 `0` 중복이 생기지 않는다.
- [ ] 소수점은 숫자당 한 번만 입력된다.
- [ ] 연산자 직후 소수점 입력 시 `0.` 형태로 시작된다.
- [ ] 결과 출력 후 숫자를 누르면 새 입력이 시작된다.

**Verification:**
- [ ] 실행 확인: `1`, `2`, `3` 입력 시 화면이 `123`으로 표시된다.
- [ ] 실행 확인: `1`, `.`, `2`, `.` 입력 시 두 번째 소수점이 무시된다.
- [ ] 수동 확인: `+` 직후 `.` 입력 시 `0.` 또는 동등한 정상 표시가 나온다.

**Dependencies:** Task 2

**Files likely touched:**
- `week07/calculator.py`

**Estimated scope:** Medium

## Task 6: Implement operator flow and equal evaluation

**Description:**  
연산자 버튼 입력 시 이전 값과 현재 값을 저장하고, `equal()` 호출 시 대기 중인 연산을 수행하도록 구현한다. 연산자 연속 입력, `=` 연속 입력, 중간 계산 결과 이어가기 같은 실제 사용 흐름을 포함해 처리 규칙을 정리한다.

**Acceptance criteria:**
- [ ] 연산자 입력 시 계산 대기 상태가 저장된다.
- [ ] `equal()`이 현재 연산자와 피연산자를 사용해 결과를 계산한다.
- [ ] 연속 계산 흐름에서 이전 결과를 다음 계산에 재사용할 수 있다.
- [ ] 연산자 연속 입력 시 마지막 선택 연산자로 갱신되거나 정의된 규칙대로 처리된다.

**Verification:**
- [ ] 실행 확인: `7 + 3 =` 결과가 `10`이다.
- [ ] 실행 확인: `8 / 2 =` 결과가 `4`다.
- [ ] 수동 확인: `5 + - * 2 =` 같은 연산자 연속 입력이 비정상 문자열을 만들지 않는다.
- [ ] 수동 확인: `=`을 연속으로 눌렀을 때의 동작이 정의된 규칙과 일치한다.

**Dependencies:** Task 3, Task 4, Task 5

**Files likely touched:**
- `week07/calculator.py`

**Estimated scope:** Medium

## Task 7: Connect the UI to the calculator core

**Description:**  
버튼 클릭 이벤트가 직접 문자열을 수정하지 않고 계산 코어의 메소드들을 호출하도록 구조를 정리한다. 숫자, 연산자, 기능 버튼별 입력 분기를 다듬고, 계산 결과가 항상 디스플레이에 반영되도록 UI 업데이트 흐름을 통일한다.

**Acceptance criteria:**
- [ ] 모든 버튼이 계산 코어의 적절한 메소드와 연결되어 있다.
- [ ] 버튼 클릭 후 화면이 일관된 방식으로 갱신된다.
- [ ] UI가 직접 계산 규칙을 중복 구현하지 않는다.
- [ ] 기존 버튼 레이아웃과 기본 사용감이 유지된다.

**Verification:**
- [ ] 실행 확인: 마우스로 주요 버튼을 눌러 전체 계산 흐름이 동작한다.
- [ ] 수동 확인: 입력 처리 로직이 한 곳에 모여 있어 유지보수가 쉬운 구조다.

**Dependencies:** Task 6

**Files likely touched:**
- `week07/calculator.py`

**Estimated scope:** Medium

## Task 8: Polish formatting, display, and bonus behavior

**Description:**  
출력 표시 형식을 다듬고, 필요 시 보너스 과제인 동적 폰트 조절과 소수점 6자리 반올림을 적용한다. 정수 표시, 불필요한 후행 `0` 제거, 긴 결과값 축소 표시, 오류 메시지 길이 조정 등을 함께 정리한다.

**Acceptance criteria:**
- [ ] 결과값이 읽기 좋은 형식으로 표시된다.
- [ ] 소수점 결과가 6자리를 넘으면 반올림 규칙이 적용된다.
- [ ] 결과 길이에 따라 폰트 크기 조절 또는 동등한 표시 보정이 적용된다.
- [ ] 스타일 가이드와 PEP 8 요구사항을 충족한다.

**Verification:**
- [ ] 실행 확인: 긴 숫자 결과가 화면을 넘치지 않는다.
- [ ] 실행 확인: `1 / 3 =` 결과가 정의한 소수점 정책에 맞게 표시된다.
- [ ] 수동 확인: 문자열 작은따옴표, 공백, 들여쓰기가 가이드에 맞다.

**Dependencies:** Task 7

**Files likely touched:**
- `week07/calculator.py`

**Estimated scope:** Small

## Task 9: Run end-to-end verification

**Description:**  
완성된 계산기를 실행해 핵심 시나리오와 예외 케이스를 점검한다. 기본 연산, 초기화, 부호 전환, 퍼센트, 소수점 입력, 0으로 나누기, 큰 수 처리, 실행 경고 여부를 확인해 제출 가능 상태로 마무리한다.

**Acceptance criteria:**
- [ ] 프로그램이 경고 없이 실행된다.
- [ ] 필수 기능이 모두 수동 시나리오에서 동작한다.
- [ ] 예외 상황 처리 결과가 사용자 입장에서 이해 가능하다.
- [ ] 최종 산출물 경로와 파일명이 요구사항과 일치한다.

**Verification:**
- [ ] 실행 확인: `python3 week07/calculator.py`
- [ ] 수동 확인: `AC`, `+/-`, `%`, `.`, `=`, `+`, `-`, `*`, `/` 버튼 동작을 각각 점검한다.
- [ ] 수동 확인: `8 / 0 =` 입력 시 오류 상태가 정상 표시되고 앱이 유지된다.

**Dependencies:** Task 8

**Files likely touched:**
- `week07/calculator.py`

**Estimated scope:** Small

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| 기존 UI 코드가 문자열 누적 방식에 강하게 묶여 있어 계산 코어 분리가 어색할 수 있다 | High | 입력 처리 전용 메소드와 실제 연산 메소드를 분리하고, 화면 갱신은 마지막 단계에만 수행한다 |
| `+/-`와 `%`가 현재 입력값 기준인지 전체 식 기준인지 혼동될 수 있다 | Medium | 아이폰 계산기와 유사하게 “현재 표시값 기준”으로 동작 규칙을 먼저 고정한다 |
| 실수 연산 결과의 부동소수점 오차가 사용자에게 그대로 보일 수 있다 | Medium | 출력 전 포맷팅 단계에서 소수점 6자리 반올림과 후행 `0` 제거를 적용한다 |
| 매우 큰 수 처리 기준이 불명확하면 overflow 또는 화면 깨짐이 생길 수 있다 | Medium | 내부 허용 범위를 정하고 초과 시 `Error` 또는 범위 초과 메시지로 처리한다 |
| 보너스 기능까지 한 번에 넣다가 필수 기능 안정성이 떨어질 수 있다 | Medium | 필수 연산과 예외 처리 완료 후에 표시 보정 기능을 별도 마무리 단계에서 넣는다 |

## Open Questions
- 최종 제출 파일을 `week07/calculator.py`로 둘지, 루트 또는 다른 경로의 `calculator.py`로 둘지 과제 운영 기준 확인이 필요하다.
- `=` 연속 입력 시 직전 연산 반복까지 구현할지, 한 번 계산 후 대기 상태만 유지할지 동작 규칙을 정하면 구현이 더 명확해진다.
- 숫자 범위 초과 기준을 자릿수 기준으로 둘지, `float` 변환 가능 범위 기준으로 둘지 결정이 필요하다.
