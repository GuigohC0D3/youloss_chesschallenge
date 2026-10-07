# Apple Silicon M4 Thermal & Multi-Thread Profiling (2026-10-06)

## Purpose & Context
Under the official tournament regulations of Chess Challenge III (November 6, 2026), teams play 5 preliminary rounds of 25-minute games followed by playoffs and finals (Best of 3) over a 5–6 hour window. On a fanless Apple Silicon MacBook (M4 with 4 Performance cores and 6 Efficiency cores), running excessive threads causes thermal throttling and work-stealing stalls between asymmetric cores.

This empirical study measures sustained throughput (NPS), thermal degradation, and search depth across 4, 6, 8, and 10 threads under 512 MiB Hash on AC power.

---

## Hardware Environment
- **SoC:** Apple M4 (`machdep.cpu.brand_string: Apple M4`)
- **Total Cores:** 10 physical cores (`hw.ncpu: 10`)
- **Performance Cores (P-cores):** 4 (`hw.perflevel0.physicalcpu: 4`)
- **Efficiency Cores (E-cores):** 6 (`hw.perflevel1.physicalcpu: 6`)
- **Cooling:** Fanless chassis (chassis surface heat dissipation)
- **Power:** AC Power connected, battery > 90% charging.
- **Engine Binary:** `bin/youloss` (SHA-256: `c5ae79086977e2f0d6de3a115e7b3aa241d85bca44a8524a1422527211c38301`)

---

## Empirical Benchmark Results (Position: complex middlegame FEN, 512 MiB Hash)

| Threads | Core Mapping | Overall Avg NPS | Early NPS (0–10s) | Late NPS (10–20s) | Throttling Delta | Max Depth Reached |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **4** | 4 P-cores (100% P) | 2,160,801 | 2,179,465 | 2,011,486 | **-7.71%** | **Depth 27** |
| **6** | 4 P-cores + 2 E-cores | 3,026,587 | 3,076,987 | 2,640,186 | **-14.20%** | **Depth 25** |
| **8** | 4 P-cores + 4 E-cores | 3,682,707 | 3,751,863 | 2,887,415 | **-23.04%** | **Depth 26** |
| **10** | 4 P-cores + 6 E-cores (All) | 3,041,489 | 3,116,234 | 2,686,451 | **-13.79%** | **Depth 23** |

---

## Key Engineering Findings

1. **The 10-Thread Trap (Asymmetric Core Contention):**
   - Running all 10 threads yielded **lower overall NPS (3.04M vs 3.68M)** and significantly **lower search depth (Depth 23 vs Depth 27/26)** than running 8 or 4 threads.
   - *Root cause:* Stockfish's SMP search uses lazy SMP with shared TT. Saturating all 6 E-cores forces high-speed P-core threads to frequently synchronize with or wait for slower E-core helper threads, causing lock contention and degraded tree exploration.

2. **Severe 8-Thread Thermal Throttling:**
   - 8 threads starts fast (3.75M NPS) but drops by **-23.04%** to 2.88M NPS within 20 seconds. In a 25-minute game with consecutive rounds, 8 threads will heat-soak the fanless MacBook chassis and lead to aggressive clock gating.

3. **4-Thread Depth Superiority:**
   - 4 threads achieved the **deepest tactical search (Depth 27)** with minimal degradation (-7.71%). Running purely on the 4 P-cores eliminates E-core interference and thermal strain.

4. **Tournament Recommendation:**
   - **Recommended Tournament Profile:** **6 threads, Hash 512 MiB**.
   - Provides +40% NPS over 4 threads (3.03M NPS sustained) while avoiding the severe -23% thermal collapse of 8 threads and the core contention of 10 threads.
   - For long marathon rounds or high ambient room temperatures, **4 threads** is the safe fallback with maximum depth efficiency.
