'''Load Mars weather CSV data into MySQL.'''

import csv
import sys
from datetime import datetime
from pathlib import Path

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:  # pragma: no cover - depends on local environment
    mysql = None
    Error = Exception


CREATE_TABLE_QUERY = '''
CREATE TABLE IF NOT EXISTS mars_weather (
    weather_id INT PRIMARY KEY AUTO_INCREMENT,
    mars_date DATETIME NOT NULL,
    temp INT,
    storm INT
)
'''

INSERT_WEATHER_QUERY = '''
INSERT INTO mars_weather (mars_date, temp, storm)
VALUES (%s, %s, %s)
'''

COUNT_QUERY = 'SELECT COUNT(*) FROM mars_weather'
PREVIEW_QUERY = '''
SELECT weather_id, mars_date, temp, storm
FROM mars_weather
ORDER BY weather_id
LIMIT 5
'''

DEFAULT_CSV_PATH = Path(__file__).with_name('mars_weathers_data.CSV')
# MySQL Workbench에서 확인한 접속 정보를 기준으로 설정한다.
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'hawa',
    'password': '663567',
    'database': 'hawa',
}


class MySQLHelper:
    '''Wrap basic MySQL connection and query operations.'''

    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None

    def connect(self):
        '''Open the MySQL connection.'''
        if mysql is None:
            raise RuntimeError(
                'mysql-connector-python is not installed. '
                'Install it before running this script.'
            )

        self.connection = mysql.connector.connect(**self.db_config)

    def execute(self, query, params=None):
        '''Execute a write query.'''
        if self.connection is None:
            raise RuntimeError('MySQL connection is not open.')

        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params)
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        '''Execute a read query and return all rows.'''
        if self.connection is None:
            raise RuntimeError('MySQL connection is not open.')

        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cursor.close()

    def commit(self):
        '''Commit the current transaction.'''
        if self.connection is None:
            raise RuntimeError('MySQL connection is not open.')

        self.connection.commit()

    def close(self):
        '''Close the MySQL connection.'''
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()

def create_mars_weather_table(helper):
    '''Create the target table if it does not exist.'''
    # 테이블이 없을 때만 생성되므로 여러 번 실행해도 안전하다.
    helper.execute(CREATE_TABLE_QUERY)
    helper.commit()


def read_weather_rows(csv_path):
    '''Read all rows from the CSV file.'''
    print(f'CSV 파일을 읽습니다: {csv_path}')

    with csv_path.open('r', encoding='utf-8', newline='') as csv_file:
        # 첫 줄 헤더를 기준으로 각 행을 dict 형태로 읽는다.
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    print(f'CSV 파일 읽기 완료: 총 {len(rows)}개의 데이터를 찾았습니다.')
    return rows


def preview_weather_rows(rows, limit=5):
    '''Print the first few CSV rows for verification.'''

    for row in rows[:limit]:
        print(row)

    print(f'총 CSV 데이터 개수: {len(rows)}')


def convert_row(raw_row):
    '''Validate and convert one CSV row for insertion.'''
    mars_date_text = raw_row['mars_date'].strip()

    if not mars_date_text:
        raise ValueError('mars_date is required.')

    # weather_id는 AUTO_INCREMENT를 사용하므로 형식만 확인한다.
    int(raw_row['weather_id'])

    # CSV의 날짜 문자열을 DATETIME 형식으로 바꾸기 위해 파싱한다.
    mars_date = datetime.strptime(mars_date_text, '%Y-%m-%d')

    # temp는 CSV에 소수로 들어 있으므로 테이블 스키마에 맞게 정수로 변환한다.
    temp = int(float(raw_row['temp']))

    # CSV 헤더의 stom 값을 storm 컬럼에 저장한다.
    storm = int(raw_row['stom'])

    return (
        mars_date.strftime('%Y-%m-%d 00:00:00'),
        temp,
        storm,
    )


def insert_weather_rows(helper, rows):
    '''Insert rows one by one into the target table.'''
    inserted_count = 0

    print('CSV 데이터를 MySQL 테이블에 삽입합니다.')

    for row in rows:
        converted_row = convert_row(row)
        # 과제 조건에 맞게 executemany() 대신 한 줄씩 INSERT 한다.
        helper.execute(INSERT_WEATHER_QUERY, converted_row)
        inserted_count += 1

        if inserted_count <= 5:
            print(f'{inserted_count}번째 데이터 삽입 완료: {converted_row}')
        elif inserted_count % 100 == 0:
            print(f'{inserted_count}개의 데이터 삽입 완료')

    helper.commit()
    print('모든 INSERT 쿼리 실행 후 commit을 완료했습니다.')
    return inserted_count


def print_insert_results(helper):
    '''Print row count and sample rows after insertion.'''
    # 저장이 끝난 뒤 건수와 일부 데이터를 다시 조회해 결과를 확인한다.
    count_rows = helper.fetch_all(COUNT_QUERY)
    preview_rows = helper.fetch_all(PREVIEW_QUERY)

    print(f'mars_weather 테이블 전체 행 수: {count_rows[0][0]}')
    print('테이블에 저장된 상위 5개 데이터를 확인합니다.')

    for row in preview_rows:
        print(row)


def main():
    '''Run the Mars weather import workflow.'''
    csv_path = DEFAULT_CSV_PATH

    if not csv_path.exists():
        print(f'CSV file not found: {csv_path}')
        return 1

    helper = MySQLHelper(DB_CONFIG)

    try:
        # 전체 실행 순서:
        # MySQL 연결 -> 테이블 확인 -> CSV 읽기 -> 데이터 변환
        # -> 반복 INSERT -> commit -> 결과 조회
        print('MySQL 데이터 적재 작업을 시작합니다.')
        print('현재 DB 접속 정보:')
        print(DB_CONFIG)

        helper.connect()
        print('MySQL 연결에 성공했습니다.')
        create_mars_weather_table(helper)
        print('mars_weather 테이블 생성 또는 존재 여부를 확인했습니다.')

        rows = read_weather_rows(csv_path)
        preview_weather_rows(rows)

        inserted_count = insert_weather_rows(helper, rows)
        print(f'이번 실행에서 삽입한 데이터 개수: {inserted_count}')

        print_insert_results(helper)
        print('모든 작업이 완료되었습니다.')
        return 0
    except RuntimeError as error:
        print(f'실행 오류: {error}')
        return 1
    except Error as error:
        print(f'MySQL 오류가 발생했습니다: {error}')
        return 1
    except ValueError as error:
        print(f'데이터 변환 오류가 발생했습니다: {error}')
        return 1
    finally:
        helper.close()
        print('MySQL 연결을 종료했습니다.')


if __name__ == '__main__':
    sys.exit(main())
