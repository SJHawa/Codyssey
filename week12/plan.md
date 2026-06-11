# Week12 Mars Weather MySQL Plan

## Summary
`week12` 폴더에 `plan.md`와 `mars_weather_summary.py`를 제출한다. 과제 목표는 MySQL 서버와 MySQL Workbench를 준비하고, `mars_weather` 테이블을 만든 뒤 Python 코드로 CSV 데이터를 읽어 반복 `INSERT`로 적재하는 것이다. 보너스 과제로 `MySQLHelper` 클래스를 두어 연결과 쿼리 실행을 정리한다.

## Setup
1. MySQL Community Server를 설치한다.
2. MySQL Workbench를 설치한다.
3. MySQL 서버를 실행하고 사용할 데이터베이스를 1개 준비한다.
4. MySQL Workbench에서 로컬 서버 연결을 만든다.
5. Workbench에서 아래 확인을 수행한다.
   - 서버 연결 성공
   - 데이터베이스 선택 가능
   - `mars_weather` 테이블 생성 및 조회 가능
6. 결과 PNG는 최소 2장으로 저장한다.
   - Workbench 연결 성공 화면
   - `SELECT COUNT(*)` 또는 샘플 조회 결과 화면

## Table Definition
테이블 이름은 `mars_weather`로 고정한다.

```sql
CREATE TABLE mars_weather (
    weather_id INT PRIMARY KEY AUTO_INCREMENT,
    mars_date DATETIME NOT NULL,
    temp INT,
    storm INT
);
```

## Python Script Design
- 구현 파일은 `week12/mars_weather_summary.py`로 고정한다.
- CSV 파일은 실제 파일명인 `week12/mars_weathers_data.CSV`를 읽는다.
- CSV 헤더의 `stom`은 Python에서 `storm`으로 매핑한다.
- `temp`는 CSV 원본이 소수이므로 `float`로 읽은 뒤 `int()`로 변환한다.
- `weather_id`는 `AUTO_INCREMENT`를 사용하므로 `INSERT` 대상에서 제외한다.
- `INSERT`는 `executemany()`를 쓰지 않고 한 행씩 반복 실행한다.
- DB 연결 정보는 스크립트 상단의 `DB_CONFIG` 딕셔너리에서 직접 수정한다.

## Public Interfaces
- `MySQLHelper`
- `connect()`
- `execute(query, params=None)`
- `fetch_all(query, params=None)`
- `commit()`
- `close()`
- `create_mars_weather_table(helper)`
- `read_weather_rows(csv_path)`
- `preview_weather_rows(rows, limit=5)`
- `convert_row(raw_row)`
- `insert_weather_rows(helper, rows)`
- `main()`

## Execution Flow
1. MySQL 연결 정보를 읽는다.
2. MySQL 서버에 연결한다.
3. `mars_weather` 테이블을 생성한다.
4. CSV 파일을 읽고 앞부분 일부를 출력한다.
5. 각 행을 검증하고 변환한다.
6. 변환된 행을 반복 `INSERT` 한다.
7. 전체 적재 건수를 조회한다.
8. 연결을 종료한다.

## Validation Rules
- `weather_id`는 CSV 구조 검증용으로만 확인하고 DB에는 저장 시 사용하지 않는다.
- `mars_date`는 비어 있으면 안 된다.
- `mars_date`는 `YYYY-MM-DD 00:00:00` 형식으로 저장한다.
- `temp`는 `int(float(value))` 규칙으로 정수화한다.
- `stom`은 `storm`으로 이름을 바꿔 `int`로 저장한다.

## Re-run Note
- 스크립트는 적재 전에 `DELETE`를 수행하지 않는다.
- 이미 같은 `weather_id`가 들어 있으면 재실행 시 중복 키 오류가 날 수 있다.
- 재실행이 필요하면 Workbench에서 수동으로 테이블을 비우거나 테이블을 다시 생성한다.

## Run Example
```bash
python3 week12/mars_weather_summary.py
```

실행 전 `week12/mars_weather_summary.py` 상단의 `DB_CONFIG` 값을 실제 MySQL 접속 정보로 수정한다.

## Test Plan
- `python3 -m py_compile week12/mars_weather_summary.py`가 성공한다.
- 스크립트 실행 시 CSV 미리보기 5건이 출력된다.
- CSV 총 1000건이 읽힌다.
- `mars_weather` 테이블이 없으면 생성된다.
- 각 행이 반복 `INSERT`로 적재된다.
- 적재 후 `SELECT COUNT(*) FROM mars_weather` 결과가 1000이다.
- `storm` 컬럼에는 CSV의 `stom` 값이 들어간다.
- `temp`는 정수로 저장된다.
- MySQL 연결 라이브러리가 없으면 안내 메시지를 출력한다.

## Bonus
- `MySQLHelper` 클래스로 연결, 쿼리 실행, 조회, 커밋, 종료를 분리한다.
- SQL 실행부와 CSV 처리부를 함수로 나눠 재사용 가능하게 유지한다.
