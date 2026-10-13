from datetime import datetime
from pathlib import Path
from threading import Lock


class SessionLogger:
    TIME_FORMAT = "%d.%m.%Y %H:%M:%S"

    def __init__(self, login, file_path):
        self._login = login
        self._file_path = Path(file_path)
        self._time_in = datetime.now()
        self._time_out = None
        self._saved = False
        self._lock = Lock()

    @property
    def login(self):
        return self._login

    @property
    def time_in(self):
        return self._time_in

    @property
    def time_out(self):
        return self._time_out

    @property
    def file_path(self):
        return self._file_path

    def finish(self):
        with self._lock:
            if self._saved:
                return

            time_out = datetime.now()
            report = self._build_report(time_out)

            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with self.file_path.open("a", encoding="utf-8") as file:
                file.write(report)

            self._time_out = time_out
            self._saved = True

    def _build_report(self, time_out):
        login_width = max(10, len(self.login))
        time_width = 19

        border = (
            "+"
            + "-" * (login_width + 2)
            + "+"
            + "-" * (time_width + 2)
            + "+"
            + "-" * (time_width + 2)
            + "+\n"
        )

        header = (
            f"| {'login':<{login_width}} "
            f"| {'time_in':<{time_width}} "
            f"| {'time_out':<{time_width}} |\n"
        )

        row = (
            f"| {self.login:<{login_width}} "
            f"| {self.time_in.strftime(self.TIME_FORMAT)} "
            f"| {time_out.strftime(self.TIME_FORMAT)} |\n"
        )

        return border + header + border + row + border + "\n"