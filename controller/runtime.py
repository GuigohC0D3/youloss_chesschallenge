"""Opções UCI de runtime do engine (spec seção 6)."""
from __future__ import annotations

import ctypes
import os
import re
import subprocess
import sys
from pathlib import Path

MOVE_OVERHEAD_MS = 1500
HASH_CAP_MB = 16 * 1024
SYZYGY_PROBE_LIMIT = 5  # Conservative project assumption; organizer permission is unconfirmed.


def _darwin_free_mb() -> int:
    # macOS não tem SC_AVPHYS_PAGES. "Disponível" como no Monitor de Atividade:
    # páginas livres + inativas + especulativas (reaproveitáveis sem swap).
    out = subprocess.run(["vm_stat"], capture_output=True, text=True, check=True).stdout
    page = int(re.search(r"page size of (\d+) bytes", out).group(1))

    def pages(name: str) -> int:
        return int(re.search(rf"^Pages {name}:\s+(\d+)", out, re.M).group(1))

    return (pages("free") + pages("inactive") + pages("speculative")) * page // 2**20


def free_memory_mb() -> int:
    if sys.platform == "darwin":
        return _darwin_free_mb()
    if sys.platform != "win32":
        return os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") // 2**20

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx falhou")
    return status.ullAvailPhys // 2**20


def has_syzygy(path: Path) -> bool:
    return path.is_dir() and any(path.glob("*.rtbw"))


def _sysctl_int(name: str) -> int | None:
    try:
        out = subprocess.run(
            ["sysctl", "-n", name], capture_output=True, text=True, check=True
        ).stdout
        return int(out.strip())
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def profile_for(perf: int, eff: int, total_mb: int, free_mb: int) -> tuple[int, int]:
    """Threads e Hash para Apple Silicon, iguais em qualquer M4/M5 com a mesma RAM.

    Threads: todos os núcleos P + 1/3 dos E. Em 4P+6E dá 6, o perfil medido em
    docs/evidence/2026-10-06-m4-thermal-thread-profile.md (8 threads perderam 23%
    de NPS por calor em 20 s; 10 threads rendem menos que 8).
    Hash: 1/8 da RAM (2 GiB em 16 GB), nunca mais que metade da memória livre.
    """
    threads = max(1, perf + eff // 3)
    hash_mb = max(16, min(total_mb // 8, free_mb // 2))
    return threads, hash_mb


def auto_profile() -> tuple[int | None, int | None]:
    """Perfil automático no macOS; (None, None) mantém o padrão de runtime_options."""
    if sys.platform != "darwin":
        return None, None
    perf = _sysctl_int("hw.perflevel0.physicalcpu")
    eff = _sysctl_int("hw.perflevel1.physicalcpu") or 0
    memsize = _sysctl_int("hw.memsize")
    if perf is None or memsize is None:
        return None, None
    return profile_for(perf, eff, memsize // 2**20, free_memory_mb())


def runtime_options(
    syzygy_dir: Path,
    threads: int | None = None,
    hash_mb: int | None = None,
    cpus: int | None = None,
    free_mb: int | None = None,
) -> dict[str, int | str]:
    if threads is None:
        threads = max(1, (cpus if cpus is not None else os.cpu_count() or 2) - 1)
    if hash_mb is None:
        free = free_mb if free_mb is not None else free_memory_mb()
        hash_mb = max(16, min(HASH_CAP_MB, free // 2))
    opts: dict[str, int | str] = {
        "Threads": threads,
        "Hash": hash_mb,
        "Move Overhead": MOVE_OVERHEAD_MS,
        "SyzygyProbeLimit": SYZYGY_PROBE_LIMIT,
    }
    if has_syzygy(Path(syzygy_dir)):
        opts["SyzygyPath"] = str(Path(syzygy_dir).resolve())
    return opts
