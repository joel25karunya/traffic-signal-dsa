# Detailed Algorithm Design: Intelligent Traffic Signal Management

## 1. Problem Statement & Mathematical Formulation

Urban intersections controlled by fixed-time (pre-timed) signal phases cause substantial vehicular delays, excessive idle emissions, and uncoordinated queue growth. When a major corridor encounters heavy commuter flow while cross streets have sparse traffic, fixed-time allocations squander valuable green time on empty approaches while traffic backs up on congested approaches.

This project implements an **Intelligent Traffic Signal Management System** utilizing **Data Structures and Algorithms (DSA)** to solve this multi-variable optimization challenge dynamically.

---

## 2. Core Data Structures

### A. First-In, First-Out (FIFO) Queues (`collections.deque`)
Each intersection approach ($d \in \{\text{North}, \text{East}, \text{South}, \text{West}\}$) maintains its own queue of waiting vehicles.

- **Choice of Structure:** Python's `collections.deque` is implemented internally as a doubly linked list of blocks, providing true $\mathcal{O}(1)$ amortized insertion at the tail and $\mathcal{O}(1)$ extraction from the head.
- **Fairness:** Strictly enforces that vehicles are served in the exact order they arrive within that lane.
- **Operations:**
  - `enqueue(vehicle)`: $\mathcal{O}(1)$
  - `dequeue()`: $\mathcal{O}(1)$
  - `peek()`: $\mathcal{O}(1)$
  - `len()`: $\mathcal{O}(1)$

### B. Priority Queue (`heapq`)
At the start of each decision cycle, candidate directions are ranked and prioritized using Python's `heapq` module.

- **Choice of Structure:** A binary min-heap where elements are stored as negative values to function as an efficient max-priority queue:
  $$\text{entry} = (-\text{Score}_d, \text{TieOrder}_d, \text{DirectionEnum})$$
- **Complexity:**
  - Heapify active directions: $\mathcal{O}(M)$ where $M=4$.
  - Pop highest priority approach: $\mathcal{O}(\log M)$.
- **Comparison with Linear Scan:** For $M=4$ directions, a linear scan requires 4 comparisons while a binary heap requires $\approx 2$ comparisons. While both are functionally constant time $\mathcal{O}(1)$ for $M=4$, the heap structure decouples event scheduling from intersection size, allowing the architecture to scale to complex multi-phase, multi-lane junctions with dozens of movements and scheduled public transit preemption events.

---

## 3. Priority Scoring Model

The priority score for an approach $d$ at simulated time $T$ is computed deterministically:

$$\text{Score}_d = (Q_d \times W_q) + (T_{w,d} \times W_w) + B_{emg} + B_{starv}$$

### Variable Definitions:
1. $Q_d \in \mathbb{N}_0$: Current number of vehicles waiting in the queue for approach $d$.
2. $W_q \in \mathbb{R}^+$: Queue length weighting factor (default: $1.0$).
3. $T_{w,d} \in \mathbb{R}^+$: Maximum waiting duration among all vehicles currently queued in approach $d$ ($T - \text{Arrival}_{front}$).
4. $W_w \in \mathbb{R}^+$: Waiting time weighting factor (default: $0.5$).
5. $B_{emg} \in \mathbb{R}^+$: Emergency vehicle bonus ($100.0$ if an emergency vehicle is waiting and emergency handling is enabled; $0.0$ otherwise).
6. $B_{starv} \in \mathbb{R}^+$: Starvation prevention bonus ($60.0$ if $T_{w,d} \ge T_{threshold}$; $0.0$ otherwise).

### Deterministic Tie-Breaking:
If two approaches evaluate to identical priority scores, ties are deterministically resolved according to a fixed index order:
$$\text{North } (0) \prec \text{East } (1) \prec \text{South } (2) \prec \text{West } (3)$$
This guarantees mathematical reproducibility across identical simulation seeds.

---

## 4. Starvation Prevention Guarantee

### The Risk of Pure Greedy Scheduling:
A naive greedy algorithm that only selects the longest queue would allow a busy 4-lane arterial road to hold the green signal continuously or repeatedly, starving a low-volume residential side street with only 1 or 2 vehicles.

### The Fairness Safeguard:
1. The system tracks the exact arrival timestamp of the vehicle at the head of each queue.
2. If $T_{w,d} \ge T_{starvation\_threshold}$ (e.g., 60 seconds), the starvation override bonus $B_{starv}$ is added to approach $d$.
3. This boosts the side street's priority score above typical heavy queues, guaranteeing an upper bound on maximum waiting time for all non-empty approaches.

---

## 5. Adaptive Green-Light Timing Formula

Rather than allocating a fixed interval, the green phase duration $G_d$ is tailored to the observed queue length:

$$G_d = \text{clamp}\left(G_{min} + \left\lfloor Q_d \times S_{rate} + 0.5 \right\rfloor, G_{min}, G_{max}\right)$$

Where:
- $G_{min}$: Minimum safe green time (default: $5$ seconds, allowing reaction time and clearance).
- $G_{max}$: Maximum allowable single-phase green time (default: $35$ seconds, preventing arterial dominance).
- $S_{rate}$: Vehicle service rate in seconds per departing vehicle (default: $2.0$ seconds/veh).
- $\text{clamp}(v, a, b) = \max(a, \min(b, v))$.

---

## 6. Algorithmic Complexity Summary

| Phase Step | Algorithm / DS | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- |
| Vehicle Enqueue | `collections.deque.append()` | $\mathcal{O}(1)$ amortized | $\mathcal{O}(N)$ |
| Priority Calculation | Linear evaluation over approaches | $\mathcal{O}(M)$ | $\mathcal{O}(M)$ |
| Priority Selection | `heapq.heapify` & `heappop` | $\mathcal{O}(M \log M)$ | $\mathcal{O}(M)$ |
| Adaptive Timing Math | Arithmetic clamping | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ |
| Vehicle Dequeue | `collections.deque.popleft()` | $\mathcal{O}(k)$ where $k \le \text{Capacity}$ | $\mathcal{O}(1)$ |
| Metric Aggregation | Running averages & counters | $\mathcal{O}(1)$ | $\mathcal{O}(H)$ history |
