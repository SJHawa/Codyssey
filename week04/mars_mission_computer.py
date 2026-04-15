import importlib.util
import json
import threading
import time
from collections import deque
from pathlib import Path


def load_dummy_sensor_class():
    sensor_path = Path(__file__).resolve().parent.parent / 'week03' / 'mars_mission_computer.py'
    spec = importlib.util.spec_from_file_location('week03_mars_mission_computer', sensor_path)

    if spec is None or spec.loader is None:
        raise ImportError('DummySensor module could not be loaded.')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DummySensor


DummySensor = load_dummy_sensor_class()


class MissionComputer:
    POLL_INTERVAL_SECONDS = 5
    AVERAGE_INTERVAL_SECONDS = 300
    STOP_COMMAND = 'q'
    STOP_MESSAGE = 'System stopped....'
    ENV_KEYS = (
        'mars_base_internal_temperature',
        'mars_base_external_temperature',
        'mars_base_internal_humidity',
        'mars_base_external_illuminance',
        'mars_base_internal_co2',
        'mars_base_internal_oxygen',
    )

    def __init__(self):
        self.env_values = {key: 0.0 for key in self.ENV_KEYS}
        self.ds = DummySensor()
        self.stop_requested = False
        self._samples = deque()
        self._next_average_time = time.time() + self.AVERAGE_INTERVAL_SECONDS
        self._input_thread = None

    def _start_input_listener(self):
        if self._input_thread is not None:
            return

        self._input_thread = threading.Thread(
            target=self._listen_for_stop_command,
            daemon=True,
        )
        self._input_thread.start()

    def _listen_for_stop_command(self):
        while not self.stop_requested:
            try:
                user_input = input().strip().lower()
            except EOFError:
                return

            if user_input == self.STOP_COMMAND:
                self.stop_requested = True
                return

    def _sync_env_values(self, sensor_values):
        for key in self.ENV_KEYS:
            self.env_values[key] = sensor_values.get(key, 0.0)

    def _print_json(self, label, payload):
        print(f'[{label}]')
        print(json.dumps(payload, indent=2))

    def _record_sample(self, current_time):
        self._samples.append((current_time, dict(self.env_values)))
        cutoff_time = current_time - self.AVERAGE_INTERVAL_SECONDS

        while self._samples and self._samples[0][0] < cutoff_time:
            self._samples.popleft()

    def _build_average_payload(self):
        if not self._samples:
            return {key: 0.0 for key in self.ENV_KEYS}

        averages = {}
        sample_count = len(self._samples)

        for key in self.ENV_KEYS:
            total = sum(sample[key] for _, sample in self._samples)
            averages[key] = round(total / sample_count, 4)

        return averages

    def _print_average_if_needed(self, current_time):
        if current_time < self._next_average_time:
            return

        average_values = self._build_average_payload()
        self._print_json('5-Minute Average', average_values)

        while self._next_average_time <= current_time:
            self._next_average_time += self.AVERAGE_INTERVAL_SECONDS

    def get_sensor_data(self):
        self._start_input_listener()
        print(f'Type {self.STOP_COMMAND} and press Enter to stop.')

        while not self.stop_requested:
            self.ds.set_env()
            sensor_values = dict(self.ds.env_values)
            current_time = time.time()

            self._sync_env_values(sensor_values)
            self._print_json('Current Environment', self.env_values)
            self._record_sample(current_time)
            self._print_average_if_needed(current_time)

            for _ in range(self.POLL_INTERVAL_SECONDS):
                if self.stop_requested:
                    break
                time.sleep(1)

        print(self.STOP_MESSAGE)


if __name__ == '__main__':
    RunComputer = MissionComputer()

    try:
        RunComputer.get_sensor_data()
    except KeyboardInterrupt:
        print(MissionComputer.STOP_MESSAGE)
