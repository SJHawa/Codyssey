INPUT_FILE_PATH = 'week09/password.txt'
OUTPUT_FILE_PATH = 'week09/result.txt'
MAX_SHIFT = 26
DICTIONARY_WORDS = [
    'mars',
    'base',
    'door',
    'open',
    'storage',
    'emergency',
]


def shift_character(character, shift_value):
    if 'a' <= character <= 'z':
        base_code = ord('a')
        return chr((ord(character) - base_code - shift_value) % MAX_SHIFT + base_code)

    if 'A' <= character <= 'Z':
        base_code = ord('A')
        return chr((ord(character) - base_code - shift_value) % MAX_SHIFT + base_code)

    return character


def contains_dictionary_word(decoded_text, dictionary_words):
    lowered_text = decoded_text.lower()

    for word in dictionary_words:
        if word in lowered_text:
            return True

    return False


def caesar_cipher_decode(target_text):
    decoded_results = []
    matched_result = None

    for shift_value in range(MAX_SHIFT):
        decoded_characters = []

        for character in target_text:
            decoded_characters.append(
                shift_character(character, shift_value)
            )

        decoded_text = ''.join(decoded_characters)
        decoded_results.append((shift_value, decoded_text))
        print(f'{shift_value}번째 자리수 해독 결과: {decoded_text}')

        if contains_dictionary_word(decoded_text, DICTIONARY_WORDS):
            matched_result = (shift_value, decoded_text)
            print('사전 단어가 발견되어 반복을 중단합니다.')
            print(f'자동 후보 자리수: {shift_value}')
            break

    return decoded_results, matched_result


def read_password_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {file_path}')
    except PermissionError:
        print(f'파일을 읽을 권한이 없습니다: {file_path}')
    except OSError as error:
        print(f'파일을 읽는 중 오류가 발생했습니다: {error}')

    return None


def save_result_file(file_path, decoded_text):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(decoded_text)
    except PermissionError:
        print(f'파일을 저장할 권한이 없습니다: {file_path}')
        return False
    except OSError as error:
        print(f'파일을 저장하는 중 오류가 발생했습니다: {error}')
        return False

    print(f'해독 결과가 저장되었습니다: {file_path}')
    return True


def prompt_shift_value(decoded_results, matched_result):
    available_shifts = {shift_value: decoded_text for shift_value, decoded_text in decoded_results}

    if matched_result is not None:
        suggested_shift, suggested_text = matched_result
        print(f'자동 후보 해독 결과: {suggested_text}')
        print(f'추천 자리수: {suggested_shift}')

    while True:
        user_input = input('해독이 완료된 자리수를 입력하세요 (0-25): ').strip()

        try:
            shift_value = int(user_input)
        except ValueError:
            print('숫자만 입력해야 합니다.')
            continue

        if shift_value not in available_shifts:
            print('0부터 25 사이의 자리수를 입력해야 합니다.')
            continue

        return shift_value, available_shifts[shift_value]


def main():
    password_text = read_password_file(INPUT_FILE_PATH)

    if not password_text:
        print('해독할 문자열이 없습니다.')
        return

    decoded_results, matched_result = caesar_cipher_decode(password_text)
    shift_value, decoded_text = prompt_shift_value(decoded_results, matched_result)

    print(f'선택한 자리수: {shift_value}')
    print(f'최종 해독 결과: {decoded_text}')
    save_result_file(OUTPUT_FILE_PATH, decoded_text)


if __name__ == '__main__':
    main()
