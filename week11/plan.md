# Week11 STT CSV Search Plan

## Summary
`week11` 폴더에 `plan.md`와 `javis.py`를 두고 제출한다. `javis.py`는 `week10/javis.py`의 녹음 및 기간 조회 기능을 유지하면서, `records` 폴더의 WAV 파일을 STT로 변환해 CSV로 저장하는 기능과 저장된 CSV를 키워드로 검색하는 기능을 추가한다.

## Key Changes
- `week11/javis.py`는 독립 실행 파일로 만든다.
- STT는 외부 도구 `whisper` CLI를 `subprocess.run()`으로 호출한다.
- STT 결과는 음성 파일명과 같은 이름의 `.csv` 파일로 저장한다.
- CSV 컬럼은 `time`, `text` 두 개로 고정한다.
- STT 출력은 `srt` 형식으로 받고, 시간 문자열 전체를 CSV에 저장한다.
- 보너스 기능은 저장된 모든 CSV를 대상으로 키워드 검색을 수행한다.

## Public Interfaces
- `ensure_records_directory()`
- `list_audio_files()`
- `detect_stt_backend()`
- `build_stt_command(audio_path, output_directory)`
- `transcribe_audio_file(audio_path)`
- `parse_srt_segments(srt_path)`
- `save_transcript_csv(audio_path, segments)`
- `convert_all_recordings_to_csv()`
- `search_keyword_in_csv(keyword)`
- `handle_transcript_conversion()`
- `handle_csv_keyword_search()`
- `main()`

## Test Plan
- WAV 파일이 있을 때 목록이 정상 조회된다.
- `3`번 메뉴 실행 시 WAV마다 같은 이름의 CSV가 생성된다.
- CSV 첫 줄에 `time,text` 헤더가 저장된다.
- 여러 줄 자막은 한 줄 텍스트로 합쳐 저장된다.
- WAV가 없으면 변환 안내 메시지만 출력한다.
- `whisper` CLI가 없으면 안내 메시지만 출력한다.
- 키워드 검색 시 일치 행만 `파일명 | 시간 | 텍스트` 형식으로 출력된다.
- 일치하는 내용이 없으면 안내 메시지를 출력한다.
- `python3 -m py_compile week11/javis.py`가 성공한다.

## Assumptions
- 제출 대상은 `week11/plan.md`, `week11/javis.py`이다.
- 녹음 원본은 WAV 형식만 처리한다.
- STT 언어는 한국어 기준으로 고정한다.
- CSV는 WAV와 같은 `records` 폴더에 저장한다.
- 키워드 검색은 날짜 필터 없이 모든 CSV를 대상으로 한다.
