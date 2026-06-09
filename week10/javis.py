from __future__ import annotations

import datetime
import shutil
import subprocess
from pathlib import Path


RECORDS_DIRECTORY_NAME = 'records'
TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'
DATE_FORMAT = '%Y%m%d'


def ensure_records_directory() -> Path:
    records_path = Path.cwd() / RECORDS_DIRECTORY_NAME
    records_path.mkdir(parents = True, exist_ok = True)
    return records_path


def get_timestamped_filename() -> str:
    timestamp = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    return f'{timestamp}.wav'


def detect_audio_backend() -> str | None:
    if shutil.which('ffmpeg'):
        return 'ffmpeg'

    if shutil.which('arecord'):
        return 'arecord'

    return None


def parse_ffmpeg_devices(output_text: str) -> list[dict[str, str]]:
    devices = []
    capture_audio_devices = False

    for raw_line in output_text.splitlines():
        line = raw_line.strip()

        if 'AVFoundation audio devices' in line:
            capture_audio_devices = True
            continue

        if not capture_audio_devices:
            continue

        if 'AVFoundation video devices' in line:
            continue

        if '[' not in line or ']' not in line:
            continue

        if '] ' not in line:
            continue

        content = line.split('] ', maxsplit = 1)[1]

        if '] ' not in content:
            continue

        index_text, device_name = content.split('] ', maxsplit = 1)
        index_text = index_text.strip().lstrip('[').rstrip(']')
        device_name = device_name.strip()

        if not index_text.isdigit():
            continue

        devices.append(
            {
                'backend': 'ffmpeg',
                'identifier': index_text,
                'name': device_name,
            }
        )

    return devices


def parse_arecord_devices(output_text: str) -> list[dict[str, str]]:
    devices = []

    for raw_line in output_text.splitlines():
        line = raw_line.strip()

        if not line.startswith('card '):
            continue

        card_text, remainder = line.split(':', maxsplit = 1)
        card_number = card_text.replace('card', '').split(',', maxsplit = 1)[0].strip()
        device_marker = 'device '
        device_start = remainder.find(device_marker)

        if device_start == -1:
            continue

        device_number_text = remainder[device_start + len(device_marker):]
        device_number = device_number_text.split(':', maxsplit = 1)[0].strip()

        if not card_number.isdigit() or not device_number.isdigit():
            continue

        devices.append(
            {
                'backend': 'arecord',
                'identifier': f'hw:{card_number},{device_number}',
                'name': line,
            }
        )

    return devices


def list_microphones() -> list[dict[str, str]]:
    backend = detect_audio_backend()

    if backend == 'ffmpeg':
        command = [
            'ffmpeg',
            '-f',
            'avfoundation',
            '-list_devices',
            'true',
            '-i',
            '',
        ]
        process = subprocess.run(
            command,
            capture_output = True,
            text = True,
            check = False,
        )
        output_text = process.stdout + process.stderr
        return parse_ffmpeg_devices(output_text)

    if backend == 'arecord':
        process = subprocess.run(
            ['arecord', '-l'],
            capture_output = True,
            text = True,
            check = False,
        )
        output_text = process.stdout + process.stderr
        return parse_arecord_devices(output_text)

    raise RuntimeError(
        '마이크를 조회할 수 있는 외부 도구를 찾지 못했습니다. '
        'ffmpeg 또는 arecord를 설치해 주세요.'
    )


def print_microphones(microphones: list[dict[str, str]]) -> None:
    print('사용 가능한 마이크 목록')

    for index, microphone in enumerate(microphones, start = 1):
        print(f'{index}. {microphone["name"]}')


def select_microphone(microphones: list[dict[str, str]]) -> dict[str, str]:
    selection_text = input('사용할 마이크 번호를 입력하세요: ').strip()

    if not selection_text.isdigit():
        raise ValueError('마이크 번호는 숫자로 입력해야 합니다.')

    selection_index = int(selection_text) - 1

    if selection_index < 0 or selection_index >= len(microphones):
        raise ValueError('선택한 마이크 번호가 목록 범위를 벗어났습니다.')

    return microphones[selection_index]


def get_recording_duration() -> int:
    duration_text = input('녹음 시간을 초 단위로 입력하세요: ').strip()

    if not duration_text.isdigit():
        raise ValueError('녹음 시간은 1 이상의 숫자로 입력해야 합니다.')

    duration = int(duration_text)

    if duration <= 0:
        raise ValueError('녹음 시간은 1초 이상이어야 합니다.')

    return duration


def build_record_command(
    microphone: dict[str, str],
    output_path: Path,
    duration: int,
) -> list[str]:
    backend = microphone['backend']
    identifier = microphone['identifier']

    if backend == 'ffmpeg':
        return [
            'ffmpeg',
            '-y',
            '-f',
            'avfoundation',
            '-i',
            f':{identifier}',
            '-t',
            str(duration),
            str(output_path),
        ]

    if backend == 'arecord':
        return [
            'arecord',
            '-D',
            identifier,
            '-d',
            str(duration),
            str(output_path),
        ]

    raise ValueError('지원하지 않는 녹음 백엔드입니다.')


def record_audio(microphone: dict[str, str], output_path: Path) -> None:
    duration = get_recording_duration()
    command = build_record_command(microphone, output_path, duration)
    print('녹음을 시작합니다.')

    process = subprocess.run(
        command,
        capture_output = True,
        text = True,
        check = False,
    )

    if process.returncode != 0:
        error_output = process.stderr.strip() or process.stdout.strip()
        raise RuntimeError(f'녹음에 실패했습니다. {error_output}')

    print('녹음이 완료되었습니다.')


def parse_recording_datetime(file_path: Path) -> datetime.datetime | None:
    try:
        return datetime.datetime.strptime(file_path.stem, TIMESTAMP_FORMAT)
    except ValueError:
        return None


def get_date_input(prompt_text: str) -> datetime.date:
    date_text = input(prompt_text).strip()

    try:
        return datetime.datetime.strptime(date_text, DATE_FORMAT).date()
    except ValueError as error:
        raise ValueError('날짜는 YYYYMMDD 형식으로 입력해야 합니다.') from error


def list_recordings_by_date(
    start_date: datetime.date,
    end_date: datetime.date,
) -> list[Path]:
    if start_date > end_date:
        raise ValueError('시작 날짜는 종료 날짜보다 늦을 수 없습니다.')

    records_path = ensure_records_directory()
    matched_files = []

    for file_path in sorted(records_path.glob('*.wav')):
        recorded_datetime = parse_recording_datetime(file_path)

        if recorded_datetime is None:
            continue

        recorded_date = recorded_datetime.date()

        if start_date <= recorded_date <= end_date:
            matched_files.append(file_path)

    return matched_files


def handle_recording() -> None:
    records_path = ensure_records_directory()
    microphones = list_microphones()

    if not microphones:
        print('사용 가능한 마이크를 찾지 못했습니다.')
        return

    print_microphones(microphones)
    selected_microphone = select_microphone(microphones)
    output_path = records_path / get_timestamped_filename()
    record_audio(selected_microphone, output_path)
    print(f'저장된 파일: {output_path}')


def handle_recording_search() -> None:
    start_date = get_date_input('조회 시작 날짜를 입력하세요 (YYYYMMDD): ')
    end_date = get_date_input('조회 종료 날짜를 입력하세요 (YYYYMMDD): ')
    matched_files = list_recordings_by_date(start_date, end_date)

    if not matched_files:
        print('해당 기간의 녹음 파일이 없습니다.')
        return

    print('조회된 녹음 파일 목록')

    for file_path in matched_files:
        print(file_path.name)


def print_menu() -> None:
    print('1. 음성 녹음')
    print('2. 기간별 녹음 파일 조회')
    print('3. 종료')


def main() -> None:
    ensure_records_directory()

    while True:
        print_menu()
        menu_text = input('원하는 메뉴 번호를 입력하세요: ').strip()

        try:
            if menu_text == '1':
                handle_recording()
            elif menu_text == '2':
                handle_recording_search()
            elif menu_text == '3':
                print('프로그램을 종료합니다.')
                break
            else:
                print('올바른 메뉴 번호를 입력하세요.')
        except (OSError, RuntimeError, ValueError) as error:
            print(error)

        print()


if __name__ == '__main__':
    main()
