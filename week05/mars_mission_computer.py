import json
import os
import platform
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None


class MissionComputer:
    INFO_LABEL = 'Mission Computer Info'
    LOAD_LABEL = 'Mission Computer Load'
    DEFAULT_SETTINGS = {
        'operating_system': True,
        'operating_system_version': True,
        'cpu_type': True,
        'cpu_core_count': True,
        'memory_size': True,
        'cpu_usage_percent': True,
        'memory_usage_percent': True,
    }

    def __init__(self):
        self.setting_path = Path(__file__).resolve().parent / 'setting.txt'
        self.settings = self._load_settings()

    def _print_json(self, label, payload):
        print(f'[{label}]')
        print(json.dumps(payload, indent=2))

    def _format_gigabytes(self, value_in_bytes):
        gibibyte = 1024 ** 3
        return f'{value_in_bytes / gibibyte:.2f} GB'

    def _load_settings(self):
        settings = dict(self.DEFAULT_SETTINGS)

        try:
            with self.setting_path.open('r', encoding='utf-8') as setting_file:
                for line in setting_file:
                    stripped_line = line.strip()

                    if not stripped_line or stripped_line.startswith('#'):
                        continue

                    if '=' not in stripped_line:
                        continue

                    key, value = stripped_line.split('=', 1)
                    key = key.strip()
                    value = value.strip().lower()

                    if key in settings:
                        settings[key] = value == 'true'
        except FileNotFoundError:
            return settings
        except OSError:
            return settings

        return settings

    def _filter_payload(self, payload):
        filtered_payload = {}

        for key, value in payload.items():
            if self.settings.get(key, True):
                filtered_payload[key] = value

        return filtered_payload

    def get_mission_computer_info(self):
        info = {
            'operating_system': 'N/A',
            'operating_system_version': 'N/A',
            'cpu_type': 'N/A',
            'cpu_core_count': 'N/A',
            'memory_size': 'N/A',
        }

        try:
            info['operating_system'] = platform.system()
        except Exception as error:
            info['operating_system'] = f'Error: {error}'

        try:
            info['operating_system_version'] = platform.version()
        except Exception as error:
            info['operating_system_version'] = f'Error: {error}'

        try:
            info['cpu_type'] = platform.processor() or platform.machine()
        except Exception as error:
            info['cpu_type'] = f'Error: {error}'

        try:
            info['cpu_core_count'] = os.cpu_count()
        except Exception as error:
            info['cpu_core_count'] = f'Error: {error}'

        try:
            if psutil is None:
                raise RuntimeError('psutil is not available.')

            info['memory_size'] = self._format_gigabytes(psutil.virtual_memory().total)
        except Exception as error:
            info['memory_size'] = f'Error: {error}'

        filtered_info = self._filter_payload(info)
        self._print_json(self.INFO_LABEL, filtered_info)
        return filtered_info

    def get_mission_computer_load(self):
        load = {
            'cpu_usage_percent': 'N/A',
            'memory_usage_percent': 'N/A',
        }

        try:
            if psutil is None:
                raise RuntimeError('psutil is not available.')

            load['cpu_usage_percent'] = psutil.cpu_percent(interval=1)
        except Exception as error:
            load['cpu_usage_percent'] = f'Error: {error}'

        try:
            if psutil is None:
                raise RuntimeError('psutil is not available.')

            load['memory_usage_percent'] = psutil.virtual_memory().percent
        except Exception as error:
            load['memory_usage_percent'] = f'Error: {error}'

        filtered_load = self._filter_payload(load)
        self._print_json(self.LOAD_LABEL, filtered_load)
        return filtered_load


if __name__ == '__main__':
    runComputer = MissionComputer()
    runComputer.get_mission_computer_info()
    runComputer.get_mission_computer_load()
