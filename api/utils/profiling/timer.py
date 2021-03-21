from dataclasses import dataclass, field
import time
from typing import Any, Callable, ClassVar, Dict, Optional


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


@dataclass
class Timer:
    timers: ClassVar[Dict[str, float]] = dict()
    name: Optional[str] = None
    text: str = "[{}] Elapsed: {:0.5f} sec (avg {:0.5f}, min {:0.5f},\
 max {:0.5f} after {} round(s), percentage ~{:0.1f}%)"
    report_every: int = 5
    logger: Optional[Callable[[str], None]] = print
    _start_time: Optional[float] = field(default=None, init=False, repr=False)
    _rounds: int = field(default=0, init=False, repr=False)
    _min: Optional[float] = field(default=None, init=False, repr=False)
    _max: float = field(default=0.0, init=False, repr=False)
    _last_reported: Optional[float] = field(default=None, init=False, repr=False)
    _timer_since_reported: float = field(default=0.0, init=False, repr=False)

    def __post_init__(self) -> None:
        """Add timer to dict of timers after initialization"""
        if self.name is not None:
            self.timers.setdefault(self.name, 0)

    def start(self) -> None:
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer {self.name} is running. Use .stop() to stop it")

        self._start_time = self._last_reported = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        # Record statistics for multiple runs
        self._rounds += 1
        if self._rounds == 1 or elapsed_time > self._max:
            self._max = elapsed_time
        if self._min is None or elapsed_time < self._min:
            self._min = elapsed_time

        # Report elapsed time
        if self.name:
            self.timers[self.name] += elapsed_time
            self._timer_since_reported += elapsed_time
        if self.logger:
            current_time = time.time()
            if self._last_reported == self._start_time or current_time >= self._last_reported + self.report_every:
                avg = self.timers[self.name] / self._rounds
                time_since_last_report = current_time - self._last_reported
                self._last_reported = current_time
                percentage = self._timer_since_reported / time_since_last_report * 100
                self.logger(self.text.format(
                    self.name,
                    elapsed_time,
                    avg,
                    self._min,
                    self._max,
                    self._rounds,
                    percentage,
                ))
                self._timer_since_reported = 0.0

        return elapsed_time
