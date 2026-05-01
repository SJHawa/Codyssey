from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from queue import Empty
import json
import multiprocessing as mp
import os
import struct
import time
import zipfile
import zlib


CHARSET = '0123456789abcdefghijklmnopqrstuvwxyz'
PASSWORD_LENGTH = 6
BASE = len(CHARSET)
TOTAL_COMBINATIONS = BASE ** PASSWORD_LENGTH
PROGRESS_INTERVAL = 100000
COUNTER_FLUSH_INTERVAL = 5000
CHECKPOINT_SAVE_INTERVAL = 2.0


@dataclass(frozen=True)
class SearchConfig:
    zip_path: Path
    password_path: Path
    checkpoint_path: Path
    worker_count: int
    reverse: bool
    start_index: int
    end_index: int
    resume: bool


@dataclass(frozen=True)
class WorkerRange:
    start: int
    end: int


def format_elapsed_time(elapsed_seconds: float) -> str:
    minutes, seconds = divmod(int(elapsed_seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'


def print_progress(attempt_count: int, started_at: float) -> None:
    elapsed = time.time() - started_at
    print(
        f'Attempts: {attempt_count:,} | '
        f'Elapsed: {format_elapsed_time(elapsed)}',
        flush=True,
    )


def index_to_password(index: int) -> str:
    chars: list[str] = []
    current = index

    for _ in range(PASSWORD_LENGTH):
        current, remainder = divmod(current, BASE)
        chars.append(CHARSET[remainder])

    return ''.join(reversed(chars))


def password_to_index(password: str) -> int:
    if len(password) != PASSWORD_LENGTH:
        raise ValueError(
            f'Password boundary must be {PASSWORD_LENGTH} characters long.'
        )

    value = 0
    for char in password:
        try:
            digit = CHARSET.index(char)
        except ValueError as error:
            raise ValueError(
                'Password boundary must contain only digits and lowercase letters.'
            ) from error
        value = (value * BASE) + digit

    return value


def parse_boundary(value: str | None, default: int) -> int:
    if value is None:
        return default

    if len(value) == PASSWORD_LENGTH and all(char in CHARSET for char in value):
        return password_to_index(value)

    if value.isdigit():
        index = int(value)
        if not 0 <= index < TOTAL_COMBINATIONS:
            raise ValueError(
                f'Index boundary must be between 0 and {TOTAL_COMBINATIONS - 1}.'
            )
        return index

    return password_to_index(value)


def parse_args() -> SearchConfig:
    parser = ArgumentParser()
    parser.add_argument(
        'zip_path',
        nargs='?',
        default=None,
    )
    parser.add_argument(
        'password_path',
        nargs='?',
        default=None,
    )
    parser.add_argument('--start')
    parser.add_argument('--end')
    parser.add_argument('--reverse', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--checkpoint', default=None)
    parser.add_argument('--workers', type=int)
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    zip_path = (
        Path(args.zip_path).resolve()
        if args.zip_path is not None
        else script_dir / 'emergency_storage_key.zip'
    )
    password_path = (
        Path(args.password_path).resolve()
        if args.password_path is not None
        else script_dir / 'password.txt'
    )
    checkpoint_path = (
        Path(args.checkpoint).resolve()
        if args.checkpoint is not None
        else script_dir / 'checkpoint.json'
    )
    worker_count = args.workers or min(len(CHARSET), os.cpu_count() or 1)
    start_index = parse_boundary(args.start, 0)
    end_index = parse_boundary(args.end, TOTAL_COMBINATIONS - 1)

    if worker_count < 1:
        raise ValueError('Worker count must be at least 1.')
    if start_index > end_index:
        raise ValueError('Start boundary must not be greater than end boundary.')

    return SearchConfig(
        zip_path=zip_path,
        password_path=password_path,
        checkpoint_path=checkpoint_path,
        worker_count=worker_count,
        reverse=args.reverse,
        start_index=start_index,
        end_index=end_index,
        resume=args.resume,
    )


def try_password(
    archive: zipfile.ZipFile,
    file_info: zipfile.ZipInfo,
    candidate: str,
) -> bool:
    try:
        with archive.open(file_info, pwd=candidate.encode('utf-8')) as zipped_file:
            zipped_file.read()
        return True
    except (RuntimeError, zipfile.BadZipFile, zlib.error):
        return False


def get_header_check_byte(file_info: zipfile.ZipInfo) -> int:
    if file_info.flag_bits & 0x08:
        return (file_info._raw_time >> 8) & 0xFF

    return (file_info.CRC >> 24) & 0xFF


def load_encrypted_header(zip_path: Path, file_info: zipfile.ZipInfo) -> bytes:
    with zip_path.open('rb') as zip_file:
        zip_file.seek(file_info.header_offset)
        file_header = zip_file.read(zipfile.sizeFileHeader)
        header_fields = struct.unpack(zipfile.structFileHeader, file_header)
        filename_length = header_fields[zipfile._FH_FILENAME_LENGTH]
        extra_field_length = header_fields[zipfile._FH_EXTRA_FIELD_LENGTH]

        encrypted_header_offset = (
            file_info.header_offset
            + zipfile.sizeFileHeader
            + filename_length
            + extra_field_length
        )
        zip_file.seek(encrypted_header_offset)
        return zip_file.read(12)


def password_matches_header(
    encrypted_header: bytes,
    check_byte: int,
    candidate: str,
) -> bool:
    decrypter = zipfile._ZipDecrypter(candidate.encode('utf-8'))
    decrypted_header = decrypter(encrypted_header)
    return decrypted_header[11] == check_byte


def validate_zip_file(zip_path: Path) -> bool:
    try:
        with zipfile.ZipFile(zip_path) as archive:
            if not archive.infolist():
                print('ZIP archive is empty.')
                return False
    except FileNotFoundError:
        print(f'ZIP file not found: {zip_path}')
        return False
    except zipfile.BadZipFile:
        print(f'Invalid ZIP file: {zip_path}')
        return False
    except OSError as error:
        print(f'Failed to open ZIP file: {error}')
        return False

    return True


def choose_mp_context() -> mp.context.BaseContext:
    start_methods = mp.get_all_start_methods()
    if 'fork' in start_methods:
        return mp.get_context('fork')

    return mp.get_context('spawn')


def split_ranges(start_index: int, end_index: int, worker_count: int) -> list[WorkerRange]:
    total = end_index - start_index + 1
    actual_workers = min(worker_count, total)
    base_size, remainder = divmod(total, actual_workers)
    ranges: list[WorkerRange] = []
    cursor = start_index

    for worker_id in range(actual_workers):
        size = base_size + (1 if worker_id < remainder else 0)
        next_cursor = cursor + size
        ranges.append(WorkerRange(start=cursor, end=next_cursor))
        cursor = next_cursor

    return ranges


def make_checkpoint_payload(
    config: SearchConfig,
    ranges: list[WorkerRange],
    positions: list[int],
) -> dict:
    return {
        'zip_path': str(config.zip_path),
        'password_path': str(config.password_path),
        'reverse': config.reverse,
        'worker_count': len(ranges),
        'start_index': config.start_index,
        'end_index': config.end_index,
        'workers': [
            {
                'start': worker_range.start,
                'end': worker_range.end,
                'position': position,
            }
            for worker_range, position in zip(ranges, positions, strict=True)
        ],
    }


def save_checkpoint(
    checkpoint_path: Path,
    config: SearchConfig,
    ranges: list[WorkerRange],
    positions: list[int],
) -> None:
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    payload = make_checkpoint_payload(config, ranges, positions)
    checkpoint_path.write_text(
        json.dumps(payload, indent=2),
        encoding='utf-8',
    )


def load_checkpoint(config: SearchConfig) -> tuple[SearchConfig, list[WorkerRange], list[int]]:
    payload = json.loads(config.checkpoint_path.read_text(encoding='utf-8'))
    if payload['zip_path'] != str(config.zip_path):
        raise ValueError('Checkpoint ZIP path does not match the current ZIP path.')

    resume_config = SearchConfig(
        zip_path=config.zip_path,
        password_path=config.password_path,
        checkpoint_path=config.checkpoint_path,
        worker_count=payload['worker_count'],
        reverse=payload['reverse'],
        start_index=payload['start_index'],
        end_index=payload['end_index'],
        resume=config.resume,
    )
    ranges = [
        WorkerRange(start=item['start'], end=item['end'])
        for item in payload['workers']
    ]
    positions = [item['position'] for item in payload['workers']]
    return resume_config, ranges, positions


def default_positions(ranges: list[WorkerRange], reverse: bool) -> list[int]:
    if reverse:
        return [worker_range.end - 1 for worker_range in ranges]

    return [worker_range.start for worker_range in ranges]


def update_counter(counter: mp.Value, lock: mp.Lock, amount: int) -> None:
    if amount == 0:
        return

    with lock:
        counter.value += amount


def set_position(positions, worker_id: int, value: int) -> None:
    positions[worker_id] = value


def search_password_chunk(
    worker_id: int,
    zip_path: str,
    worker_range: WorkerRange,
    reverse: bool,
    start_position: int,
    encrypted_header: bytes,
    check_byte: int,
    found_event: mp.Event,
    result_queue: mp.Queue,
    counter: mp.Value,
    lock: mp.Lock,
    positions,
) -> None:
    local_attempts = 0

    try:
        with zipfile.ZipFile(zip_path) as archive:
            file_infos = archive.infolist()
            if not file_infos:
                return

            target_info = file_infos[0]
            step = -1 if reverse else 1
            stop = worker_range.start - 1 if reverse else worker_range.end
            index = start_position

            while index != stop:
                candidate = index_to_password(index)
                local_attempts += 1

                if password_matches_header(
                    encrypted_header,
                    check_byte,
                    candidate,
                ) and try_password(archive, target_info, candidate):
                    update_counter(counter, lock, local_attempts)
                    set_position(positions, worker_id, index)
                    result_queue.put(candidate)
                    found_event.set()
                    return

                next_index = index + step

                if local_attempts >= COUNTER_FLUSH_INTERVAL:
                    update_counter(counter, lock, local_attempts)
                    local_attempts = 0
                    set_position(positions, worker_id, next_index)
                    if found_event.is_set():
                        return

                index = next_index

            set_position(positions, worker_id, stop)
    except KeyboardInterrupt:
        return
    finally:
        update_counter(counter, lock, local_attempts)


def remove_checkpoint(checkpoint_path: Path) -> None:
    if checkpoint_path.exists():
        checkpoint_path.unlink()


def normalize_resumed_positions(
    ranges: list[WorkerRange],
    positions: list[int],
    reverse: bool,
) -> list[int]:
    normalized: list[int] = []

    for worker_range, position in zip(ranges, positions, strict=True):
        if reverse:
            if position < worker_range.start:
                normalized.append(worker_range.start - 1)
            else:
                normalized.append(min(position, worker_range.end - 1))
        else:
            if position >= worker_range.end:
                normalized.append(worker_range.end)
            else:
                normalized.append(max(position, worker_range.start))

    return normalized


def unlock_zip(config: SearchConfig) -> str | None:
    started_at = time.time()
    started_at_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'Start time: {started_at_text}')
    print(f'Target ZIP: {config.zip_path}')

    if not validate_zip_file(config.zip_path):
        return None

    with zipfile.ZipFile(config.zip_path) as archive:
        file_info = archive.infolist()[0]

    encrypted_header = load_encrypted_header(config.zip_path, file_info)
    check_byte = get_header_check_byte(file_info)

    if config.resume and config.checkpoint_path.exists():
        config, ranges, initial_positions = load_checkpoint(config)
        print(f'Resuming from checkpoint: {config.checkpoint_path}')
    else:
        ranges = split_ranges(
            config.start_index,
            config.end_index,
            config.worker_count,
        )
        initial_positions = default_positions(ranges, config.reverse)

    initial_positions = normalize_resumed_positions(
        ranges,
        initial_positions,
        config.reverse,
    )

    print(f'Worker count: {len(ranges)}')
    print(
        f'Search range: {index_to_password(config.start_index)} '
        f'to {index_to_password(config.end_index)}'
    )
    print(f'Reverse mode: {config.reverse}')

    context = choose_mp_context()
    found_event = context.Event()
    result_queue = context.Queue()
    counter = context.Value('Q', 0)
    lock = context.Lock()
    positions = context.Array('q', initial_positions)
    processes: list[mp.Process] = []
    next_progress_mark = PROGRESS_INTERVAL
    last_checkpoint_save = 0.0

    try:
        for worker_id, (worker_range, start_position) in enumerate(
            zip(ranges, initial_positions, strict=True)
        ):
            if config.reverse and start_position < worker_range.start:
                continue
            if not config.reverse and start_position >= worker_range.end:
                continue

            process = context.Process(
                target=search_password_chunk,
                args=(
                    worker_id,
                    str(config.zip_path),
                    worker_range,
                    config.reverse,
                    start_position,
                    encrypted_header,
                    check_byte,
                    found_event,
                    result_queue,
                    counter,
                    lock,
                    positions,
                ),
            )
            process.start()
            processes.append(process)

        password = None

        while True:
            try:
                password = result_queue.get_nowait()
                break
            except Empty:
                pass

            current_attempts = counter.value
            while current_attempts >= next_progress_mark:
                print_progress(next_progress_mark, started_at)
                next_progress_mark += PROGRESS_INTERVAL

            now = time.time()
            if now - last_checkpoint_save >= CHECKPOINT_SAVE_INTERVAL:
                save_checkpoint(
                    config.checkpoint_path,
                    config,
                    ranges,
                    list(positions),
                )
                last_checkpoint_save = now

            if not any(process.is_alive() for process in processes):
                break

            time.sleep(0.5)

        found_event.set()

        for process in processes:
            process.join()

        current_attempts = counter.value
        while current_attempts >= next_progress_mark:
            print_progress(next_progress_mark, started_at)
            next_progress_mark += PROGRESS_INTERVAL

        if password is None:
            try:
                password = result_queue.get_nowait()
            except Empty:
                password = None

        elapsed = time.time() - started_at
        if password is None:
            save_checkpoint(
                config.checkpoint_path,
                config,
                ranges,
                list(positions),
            )
            print('Password not found.')
            print(f'Total elapsed time: {format_elapsed_time(elapsed)}')
            return None

        remove_checkpoint(config.checkpoint_path)
        print_progress(current_attempts, started_at)
        print(f'Password found: {password}')
        print(f'Total elapsed time: {format_elapsed_time(elapsed)}')
        return password
    except KeyboardInterrupt:
        save_checkpoint(
            config.checkpoint_path,
            config,
            ranges,
            list(positions),
        )
        print('\nUnlock process interrupted.')
        print(f'Checkpoint saved to: {config.checkpoint_path}')
        return None
    finally:
        found_event.set()
        for process in processes:
            if process.is_alive():
                process.terminate()
            process.join()


def save_password(password_path: Path, password: str) -> bool:
    try:
        password_path.write_text(f'{password}\n', encoding='utf-8')
        print(f'Password saved to: {password_path}')
        return True
    except OSError as error:
        print(f'Failed to save password: {error}')
        return False


def main() -> None:
    config = parse_args()
    password = unlock_zip(config)
    if password is None:
        print('Unlock process finished without success.')
        return

    if save_password(config.password_path, password):
        print('Unlock process completed successfully.')
    else:
        print('Unlock process found the password, but saving failed.')


if __name__ == '__main__':
    main()
