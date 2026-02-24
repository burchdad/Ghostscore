from dataclasses import dataclass
from typing import List

@dataclass
class TimelineEvent:
    action_type: str
    score_delta: float
    delay_weeks: int
    ramp_weeks: int

class TimelineEngine:
    ACTION_DELAYS = {
        "paydown": (2, 6),
        "limit_increase": (4, 8),
        "new_account": (0, 12),
        "derogatory_removal": (4, 12),
        "inquiry": (0, 4)
    }

    def build_timeline(self, base_score: float, events: List[TimelineEvent], total_weeks: int = 16) -> List[float]:
        timeline = [base_score] * total_weeks

        for event in events:
            delay = event.delay_weeks
            ramp = event.ramp_weeks

            # Ramp up score delta gradually
            for i in range(delay, min(delay + ramp, total_weeks)):
                progress = (i - delay + 1) / ramp
                timeline[i] += event.score_delta * progress

            # After ramp, full impact
            for i in range(delay + ramp, total_weeks):
                timeline[i] += event.score_delta

        return [round(score) for score in timeline]
