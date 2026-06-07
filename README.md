# Assignment Deadline Management Agent
### College AI Project — Python

---

## Project Details

| Field            | Value |
|------------------|-------|
| **Agent Type**   | Utility-Based Agent |
| **Problem**      | Optimize assignment deadlines |
| **Goal**         | Reduce student overload |
| **AI Techniques**| Heuristic Search, Scheduling, Constraint Propagation, Deadline Relaxation |
| **Language**     | Python 3.8+ |
| **GUI**          | Tkinter (built-in — no install needed) |

---

## How to Run

```bash
# 1. Make sure Python 3.8+ is installed
python --version

# 2. Run the app (no pip installs needed)
python gui.py
```

---

## File Structure

```
assignment_agent/
├── agent.py     ← AI core: Utility function + Heuristic Scheduler
├── gui.py       ← Tkinter GUI (Dashboard, Add, Optimize, About)
└── README.md    ← This file
```

---

## AI Architecture

### Utility Function
```
U(a) = 0.5 × (1 / slack_days)
     + 0.3 × (difficulty / 3)
     + 0.2 × (estimated_hours / 12)
```
- Higher U → agent processes task first
- Weights: urgency (50%), difficulty (30%), workload (20%)

### Heuristic Search
- Algorithm: Greedy Best-First Search
- Priority queue ordered by U(a) (max-heap)
- Expands most urgent/difficult task first
- Heuristic h(a) = U(a)

### Scheduling Rules
1. Sort all assignments by utility (highest first)
2. For each assignment, check deadline day load
3. If load + new_hours > 6h threshold AND slack > 1 day:
   - Find earliest day before deadline with free capacity
   - Reschedule start date there (Deadline Relaxation)
4. If no free slot: issue WARNING
5. Otherwise: schedule on deadline day

---

## Features
- Dashboard with live stats + 7-day workload forecast
- Add assignments with subject, title, deadline, hours, difficulty
- Mark done / delete assignments
- One-click optimization with step-by-step agent log
- Utility score per assignment + overall schedule score
- Specific reschedule recommendations with reasoning
