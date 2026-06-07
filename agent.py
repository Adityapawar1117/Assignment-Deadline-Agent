"""
Assignment Deadline Management Agent
=====================================
Agent Type  : Utility-Based Agent
Problem     : Optimize assignment deadlines
Goal        : Reduce student overload
AI Techniques: Heuristic Search + Scheduling
"""

import heapq
import math
from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import List, Optional


# ─────────────────────────────────────────────
#  DATA MODEL
# ─────────────────────────────────────────────

@dataclass
class Assignment:
    id: int
    subject: str
    title: str
    deadline: date
    estimated_hours: float
    difficulty: int          # 1=Easy, 2=Medium, 3=Hard
    assignment_type: str
    status: str = "pending"  # pending | done

    def slack_days(self) -> int:
        """Days remaining until deadline (can be negative if overdue)."""
        return (self.deadline - date.today()).days

    def urgency_label(self) -> str:
        s = self.slack_days()
        if s < 0:   return "OVERDUE"
        if s <= 1:  return "CRITICAL"
        if s <= 3:  return "HIGH"
        if s <= 7:  return "MEDIUM"
        return "LOW"

    def __repr__(self):
        return f"[{self.subject}] {self.title} | Due: {self.deadline} | {self.estimated_hours}h | Diff: {self.difficulty}"


# ─────────────────────────────────────────────
#  UTILITY FUNCTION  (core of utility-based agent)
# ─────────────────────────────────────────────

class UtilityFunction:
    """
    Computes U(a) = w1*(1/max(slack,1)) + w2*difficulty_norm + w3*hours_norm
    Higher utility → agent schedules / processes this task first.
    """
    W1 = 0.50   # urgency weight
    W2 = 0.30   # difficulty weight
    W3 = 0.20   # workload weight

    @staticmethod
    def compute(a: Assignment) -> float:
        slack      = max(a.slack_days(), 1)
        urgency    = 1.0 / slack
        diff_norm  = a.difficulty / 3.0
        hours_norm = min(a.estimated_hours / 12.0, 1.0)
        return (UtilityFunction.W1 * urgency
              + UtilityFunction.W2 * diff_norm
              + UtilityFunction.W3 * hours_norm)

    @staticmethod
    def score_to_100(u: float) -> int:
        """Maps raw utility to 0-100 priority score."""
        return min(100, int(u * 120))


# ─────────────────────────────────────────────
#  HEURISTIC SEARCH  (Greedy Best-First Scheduling)
# ─────────────────────────────────────────────

@dataclass(order=True)
class SearchNode:
    priority: float
    assignment: Assignment = field(compare=False)


class HeuristicScheduler:
    """
    Greedy Best-First Search over the assignment space.
    Heuristic h(a) = utility score (higher → expand first).
    Builds a daily schedule that keeps workload ≤ threshold.
    """
    DAILY_THRESHOLD = 6.0   # hours/day overload limit

    def __init__(self, assignments: List[Assignment]):
        self.assignments = [a for a in assignments if a.status == "pending"]
        self.schedule: dict[date, float]          = {}   # date → total hours
        self.task_slots: dict[int, date]          = {}   # assignment.id → recommended start date
        self.recommendations: List[dict]          = []
        self.log: List[str]                       = []
        self.utility_scores: dict[int, float]     = {}

    def _build_priority_queue(self) -> list:
        pq = []
        for a in self.assignments:
            u = UtilityFunction.compute(a)
            self.utility_scores[a.id] = u
            heapq.heappush(pq, SearchNode(priority=-u, assignment=a))  # max-heap via negation
        return pq

    def _available_days(self, deadline: date) -> List[date]:
        """Return days from today up to (deadline - 1) with remaining capacity."""
        today = date.today()
        days = []
        d = today
        while d < deadline:
            load = self.schedule.get(d, 0.0)
            if load < self.DAILY_THRESHOLD:
                days.append(d)
            d += timedelta(days=1)
        return days

    def run(self) -> List[dict]:
        self.log.clear()
        self.recommendations.clear()
        self.schedule.clear()
        self.task_slots.clear()

        self.log.append("► [INIT] Utility-based agent started.")
        self.log.append(f"► [LOAD] {len(self.assignments)} pending assignments found.")

        pq = self._build_priority_queue()

        self.log.append("► [HEURISTIC] Building priority queue using U(a) = 0.5/slack + 0.3·diff + 0.2·hrs")
        order = sorted(self.assignments, key=lambda a: -self.utility_scores[a.id])
        self.log.append(f"► [QUEUE] Order: {' → '.join(a.subject for a in order)}")
        self.log.append("─" * 55)

        while pq:
            node = heapq.heappop(pq)
            a = node.assignment
            u = self.utility_scores[a.id]
            score100 = UtilityFunction.score_to_100(u)
            deadline_load = self.schedule.get(a.deadline, 0.0)

            self.log.append(f"[EXPAND] {a.subject}: '{a.title}'")
            self.log.append(f"         Utility={u:.3f}  Score={score100}/100  Slack={a.slack_days()}d")

            overload = deadline_load + a.estimated_hours > self.DAILY_THRESHOLD

            if overload and a.slack_days() > 1:
                free_days = self._available_days(a.deadline)
                if free_days:
                    chosen = free_days[0]
                    self.schedule[chosen] = self.schedule.get(chosen, 0.0) + a.estimated_hours
                    self.task_slots[a.id] = chosen

                    peak_reduction = round((deadline_load + a.estimated_hours) - self.DAILY_THRESHOLD, 1)
                    rec = {
                        "id": a.id,
                        "subject": a.subject,
                        "title": a.title,
                        "original_deadline": a.deadline,
                        "recommended_start": chosen,
                        "hours": a.estimated_hours,
                        "score": score100,
                        "reason": (
                            f"Deadline day overloaded "
                            f"({round(deadline_load + a.estimated_hours, 1)}h > {self.DAILY_THRESHOLD}h). "
                            f"Start on {chosen} to reduce peak by {peak_reduction}h."
                        ),
                        "action": "RESCHEDULE",
                    }
                    self.recommendations.append(rec)
                    self.log.append(f"  ↳ [RESCHEDULE] Moved start → {chosen}  (peak -{peak_reduction}h)")
                else:
                    self.schedule[a.deadline] = deadline_load + a.estimated_hours
                    rec = {
                        "id": a.id,
                        "subject": a.subject,
                        "title": a.title,
                        "original_deadline": a.deadline,
                        "recommended_start": a.deadline,
                        "hours": a.estimated_hours,
                        "score": score100,
                        "reason": "No free slot before deadline. Consider splitting task or requesting extension.",
                        "action": "WARNING",
                    }
                    self.recommendations.append(rec)
                    self.log.append(f"  ↳ [WARNING] No free slot found. Overload persists on {a.deadline}.")
            else:
                self.schedule[a.deadline] = deadline_load + a.estimated_hours
                self.task_slots[a.id] = a.deadline
                load_after = self.schedule[a.deadline]
                self.log.append(f"  ↳ [OK] Scheduled on deadline. Daily load: {round(load_after, 1)}h")

        self.log.append("─" * 55)
        avg_util = (sum(self.utility_scores.values()) / len(self.utility_scores)) if self.utility_scores else 0
        self.log.append(f"► [DONE] Optimization complete. Avg utility: {avg_util:.3f}")
        return self.recommendations

    def workload_forecast(self, days: int = 10) -> List[tuple]:
        """Returns list of (date, hours) for next `days` days."""
        result = []
        for i in range(days):
            d = date.today() + timedelta(days=i)
            result.append((d, round(self.schedule.get(d, 0.0), 1)))
        return result

    def overall_score(self) -> int:
        if not self.utility_scores:
            return 100
        avg = sum(self.utility_scores.values()) / len(self.utility_scores)
        overloaded = sum(1 for v in self.schedule.values() if v > self.DAILY_THRESHOLD)
        penalty = overloaded * 8
        return max(0, min(100, int(avg * 120) - penalty))
