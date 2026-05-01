# Implementation Plan: 문제1 비밀번호 XXXXXX

## Overview
`emergency_storage_key.zip`의 6자리 비밀번호를 숫자와 소문자 조합으로 브루트포스하여 찾고, 이를 `unlock_zip()` 함수로 구현한다. 구현 결과물은 `door_hacking.py`에 저장하며, 실행 중 시작 시간, 반복 횟수, 진행 시간 등의 상태를 출력하고, 성공 시 찾은 비밀번호를 `password.txt`에 기록해야 한다. 표준 라이브러리만 사용하며, 특히 ZIP 처리와 파일 입출력에는 예외 처리를 포함해야 한다.

## Architecture Decisions
- 브루트포스 조합 생성에는 표준 라이브러리 `itertools.product`를 사용한다. 6중 반복문보다 코드가 짧고 조합 규칙이 명확하다.
- 시간 측정과 진행 로그는 `time` 모듈로 처리한다. 시작 시각, 경과 시간, 시도 횟수를 일정 주기마다 출력해 긴 실행 시간을 추적할 수 있게 한다.
- ZIP 비밀번호 검증은 `zipfile.ZipFile`과 `extractall()` 또는 테스트 추출 방식으로 처리한다. 성공 여부 판단이 명확하고 외부 패키지가 필요 없다.
- 파일 관련 동작(`zip` 열기, 압축 해제, `password.txt` 저장)은 모두 `try/except`로 감싸 예외 발생 시 프로그램이 이유를 설명하고 종료되도록 한다.

## Task List

### Phase 1: Requirement Framing
- [x] Task 1: 입력/출력 흐름과 제약사항 정리
- [x] Task 2: 브루트포스 전략과 로그 정책 설계

### Checkpoint: Foundation
- [x] 함수 시그니처, 입출력 파일, 예외 처리 범위가 문서로 정리되어 있다.

### Phase 2: Core Implementation
- [x] Task 3: `unlock_zip()` 함수와 비밀번호 탐색 로직 구현
- [x] Task 4: 성공/실패 처리, 로그 출력, 결과 파일 저장 구현

### Checkpoint: Core Features
- [x] `door_hacking.py`가 실행 가능하며 요구된 출력과 저장 동작을 수행한다.

### Phase 3: Validation and Polish
- [x] Task 5: 예외 상황 점검 및 코드 스타일 정리
- [ ] Task 6: 실행 검증 및 제출물 최종 확인

### Checkpoint: Complete
- [ ] 과제 요구사항이 모두 충족된다.
- [x] 제출 파일이 경고 없이 실행 가능하다.

## Task Details

## Task 1: 입력/출력 흐름과 제약사항 정리

**Description:** 문제 문서에서 구현에 직접 영향을 주는 요구사항을 추출해 개발 기준으로 정리한다. 대상 파일명, 함수명, 허용 문자 집합, 출력 요구사항, 저장 산출물, 예외 처리 의무를 명확히 고정한다.

**Acceptance criteria:**
- [ ] 비밀번호 조건이 `숫자 + 소문자`, 길이 `6`으로 정리되어 있다.
- [ ] 최종 산출물이 `door_hacking.py`와 `password.txt`임이 명시되어 있다.
- [ ] ZIP 처리와 파일 입출력에 예외 처리가 필요하다는 점이 정리되어 있다.

**Verification:**
- [ ] 문제 문서와 계획 문서를 대조해 누락된 요구사항이 없다.
- [ ] 구현 전에 함수명 `unlock_zip()`과 대상 ZIP 파일명이 확정되어 있다.

**Dependencies:** None

**Files likely touched:**
- `week08/problem.md`
- `week08/plan.md`

**Estimated scope:** XS

## Task 2: 브루트포스 전략과 로그 정책 설계

**Description:** 가능한 모든 6자리 조합을 어떤 순서로 생성할지와, 진행 상황을 얼마나 자주 출력할지 결정한다. 긴 실행 시간 동안 사용자가 멈춘 것으로 오해하지 않도록 로그 주기를 정하고, 성공 시 즉시 종료하는 흐름을 설계한다.

**Acceptance criteria:**
- [ ] 문자 집합이 `0123456789abcdefghijklmnopqrstuvwxyz`로 정의되어 있다.
- [ ] 조합 생성 방식과 성공 시 조기 종료 방식이 정리되어 있다.
- [ ] 시작 시간, 시도 횟수, 경과 시간을 출력하는 정책이 정해져 있다.

**Verification:**
- [ ] 설계상 각 조합이 중복 없이 한 번씩만 검사된다.
- [ ] 로그 주기가 과도한 출력으로 성능을 크게 떨어뜨리지 않도록 정의되어 있다.

**Dependencies:** Task 1

**Files likely touched:**
- `week08/plan.md`
- `week08/door_hacking.py`

**Estimated scope:** S

## Task 3: `unlock_zip()` 함수와 비밀번호 탐색 로직 구현

**Description:** `door_hacking.py`에 `unlock_zip()` 함수를 만들고, ZIP 파일을 열어 가능한 비밀번호를 순차적으로 시도하는 핵심 로직을 구현한다. 성공하면 해당 비밀번호를 반환하고, 끝까지 찾지 못하면 실패 상태를 반환하도록 한다.

**Acceptance criteria:**
- [ ] `unlock_zip()` 함수가 정의되어 있다.
- [ ] ZIP 파일을 열고 각 후보 비밀번호를 적용하는 루프가 구현되어 있다.
- [ ] 비밀번호가 맞는 경우 즉시 탐색을 종료하고 결과를 반환한다.
- [ ] ZIP 파일 열기 및 해제 과정에 예외 처리가 포함되어 있다.

**Verification:**
- [ ] `python3 week08/door_hacking.py` 실행 시 문법 오류가 없다.
- [ ] 올바른 비밀번호를 발견하면 함수가 성공 결과를 반환한다.
- [ ] ZIP 파일이 없거나 손상된 경우 예외 메시지가 출력된다.

**Dependencies:** Task 2

**Files likely touched:**
- `week08/door_hacking.py`

**Estimated scope:** M

## Task 4: 성공/실패 처리, 로그 출력, 결과 파일 저장 구현

**Description:** 탐색 시작 시각, 현재까지의 시도 횟수, 경과 시간을 출력하고, 비밀번호를 찾았을 때 `password.txt`에 저장하는 흐름을 완성한다. 실패 시에도 사용자에게 결과를 명확히 알리도록 출력 메시지를 구성한다.

**Acceptance criteria:**
- [ ] 프로그램 시작 시 시작 시간 정보가 출력된다.
- [ ] 탐색 중 반복 횟수와 진행 시간이 주기적으로 출력된다.
- [ ] 비밀번호를 찾으면 `password.txt`에 정확한 값이 저장된다.
- [ ] 결과 파일 저장 과정에 예외 처리가 포함되어 있다.

**Verification:**
- [ ] 성공 시 `password.txt` 내용이 찾은 비밀번호와 일치한다.
- [ ] 저장 실패 상황에서도 프로그램이 오류 원인을 출력한다.
- [ ] 출력 메시지만 보고 현재 진행 상태를 파악할 수 있다.

**Dependencies:** Task 3

**Files likely touched:**
- `week08/door_hacking.py`
- `week08/password.txt`

**Estimated scope:** S

## Task 5: 예외 상황 점검 및 코드 스타일 정리

**Description:** 파일 누락, 잘못된 ZIP, 저장 실패 등 예외 케이스를 다시 점검하고, PEP 8 가이드에 맞게 코드 스타일을 정리한다. 불필요한 전역 상태나 중복 코드를 줄여 제출용 코드로 다듬는다.

**Acceptance criteria:**
- [ ] 파일 처리 관련 주요 예외 케이스가 모두 다뤄진다.
- [ ] 들여쓰기, 공백, 문자열 표기 등 스타일이 일관된다.
- [ ] 경고 없이 읽기 쉬운 형태로 코드가 정리되어 있다.

**Verification:**
- [ ] 코드 리뷰 관점에서 요구사항 대비 누락된 예외 처리가 없다.
- [ ] `python3 -m py_compile week08/door_hacking.py`가 성공한다.

**Dependencies:** Task 4

**Files likely touched:**
- `week08/door_hacking.py`

**Estimated scope:** S

## Task 6: 실행 검증 및 제출물 최종 확인

**Description:** 최종 파일 구성을 확인하고 실제 실행 흐름을 점검한다. 필요 시 보너스 과제용 최적화 아이디어를 별도 메모로 남기되, 기본 요구사항 충족 여부를 우선 검증한다.

**Acceptance criteria:**
- [ ] 제출 대상 파일이 예상 위치에 존재한다.
- [ ] 기본 요구사항 5개가 모두 충족되었는지 체크 완료되어 있다.
- [ ] 보너스 과제 적용 여부를 명확히 결정할 수 있다.

**Verification:**
- [ ] `week08` 폴더에 `problem.md`, `plan.md`, `door_hacking.py`가 존재한다.
- [ ] 성공 시 `password.txt` 생성 여부를 확인한다.
- [ ] 과제 요구사항 체크리스트를 다시 읽고 완료 여부를 대조한다.

**Dependencies:** Task 5

**Files likely touched:**
- `week08/plan.md`
- `week08/door_hacking.py`
- `week08/password.txt`

**Estimated scope:** XS

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| 36진수 6자리 전체 탐색으로 실행 시간이 길어짐 | High | 진행 로그를 주기적으로 출력하고, 성공 즉시 종료하도록 구현한다. |
| ZIP 처리 방식이 환경에 따라 예외를 다르게 발생시킬 수 있음 | Medium | `zipfile` 예외를 포함해 넓게 예외 처리하고 메시지를 명확히 출력한다. |
| 지나친 로그 출력으로 성능 저하 발생 | Medium | 매 시도마다 출력하지 않고 일정 횟수마다만 진행 상황을 표시한다. |
| 결과 파일 저장 실패 | Low | `password.txt` 쓰기 작업에 예외 처리를 추가하고 실패 원인을 안내한다. |

## Open Questions
- 실제 제출 시 `password.txt`를 미리 포함해야 하는지, 아니면 실행 결과물로 생성되면 되는지 확인이 필요하다.
- 보너스 과제까지 포함할지, 기본 요구사항만 우선 제출할지 범위를 결정할 필요가 있다.
