"""
Virdixt-Apex Memory & Execution Watchdog
Enforces strict SLA constraints on working-set RAM and latency for Intel i5 / 8GB RAM environments.
"""

import os
import time
import psutil
from dataclasses import dataclass
from typing import Optional, Callable, Any
from apex.config import CONFIG


class MemoryBudgetExceededError(RuntimeError):
    """Raised when process memory exceeds the strict hardware allocation limit."""
    pass


class LatencyBudgetExceededError(RuntimeError):
    """Raised when an operation exceeds its configured latency ceiling."""
    pass


@dataclass
class ExecutionMetrics:
    """Telemetry captured during a monitored execution window."""
    duration_ms: float
    start_memory_mb: float
    end_memory_mb: float
    peak_memory_mb: float
    memory_delta_mb: float


class MemoryWatchdog:
    """
    Real-time hardware resource auditor.
    Measures RSS (Resident Set Size) memory and execution latency.
    """

    def __init__(self, max_memory_mb: Optional[float] = None):
        self.max_memory_mb = max_memory_mb or CONFIG.hardware.max_memory_mb
        self.process = psutil.Process(os.getpid())

    def get_current_rss_mb(self) -> float:
        """Returns the current Resident Set Size (RSS) in Megabytes."""
        return self.process.memory_info().rss / (1024 * 1024)

    def assert_within_budget(self) -> float:
        """
        Validates that current memory does not exceed the hardware ceiling.
        Returns current memory in MB if valid, raises MemoryBudgetExceededError otherwise.
        """
        current_mb = self.get_current_rss_mb()
        if current_mb > self.max_memory_mb:
            raise MemoryBudgetExceededError(
                f"Memory ceiling breached: {current_mb:.2f} MB used (Ceiling: {self.max_memory_mb:.2f} MB)"
            )
        return current_mb

    def monitor(
        self,
        func: Callable[..., Any],
        *args: Any,
        max_duration_ms: Optional[float] = None,
        **kwargs: Any
    ) -> tuple[Any, ExecutionMetrics]:
        """
        Executes a callable while profiling duration, memory delta, and peak consumption.
        """
        start_mem = self.get_current_rss_mb()
        start_time = time.perf_counter()

        # Run target callable
        result = func(*args, **kwargs)

        end_time = time.perf_counter()
        end_mem = self.get_current_rss_mb()

        duration_ms = (end_time - start_time) * 1000.0
        peak_mem = max(start_mem, end_mem)
        delta_mem = end_mem - start_mem

        metrics = ExecutionMetrics(
            duration_ms=duration_ms,
            start_memory_mb=start_mem,
            end_memory_mb=end_mem,
            peak_memory_mb=peak_mem,
            memory_delta_mb=delta_mem,
        )

        # Budget checks
        if peak_mem > self.max_memory_mb:
            raise MemoryBudgetExceededError(
                f"Peak memory {peak_mem:.2f} MB exceeded ceiling of {self.max_memory_mb:.2f} MB"
            )

        if max_duration_ms and duration_ms > max_duration_ms:
            raise LatencyBudgetExceededError(
                f"Execution took {duration_ms:.2f} ms (Budget: {max_duration_ms:.2f} ms)"
            )

        return result, metrics
