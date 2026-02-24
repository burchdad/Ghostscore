from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional
import copy

@dataclass
class GoalPreferences:
    avoid_new_accounts: bool = True
    avoid_hard_inquiries: bool = True
    prefer_paydown_over_settlement: bool = True

@dataclass
class GoalRequest:
    target_score: int
    budget: float
    timeline_weeks: int
    risk_tolerance: str = "medium"
    preferences: GoalPreferences = field(default_factory=GoalPreferences)

class GoalSolver:
    def __init__(self, engine, optimizer, scenario_analyzer, timeline_engine):
        self.engine = engine
        self.optimizer = optimizer
        self.scenario_analyzer = scenario_analyzer
        self.timeline_engine = timeline_engine

    def solve(self, profile: Dict[str, Any], req: GoalRequest) -> Dict[str, Any]:
        from scoring.snapshot_engine import SnapshotEngine
        from scoring.model_registry import ModelRegistry
        current_score, _ = self.engine.score(profile)

        # 1) candidate actions from optimizer
        actions = self.optimizer.get_actions(profile)

        # 2) filter actions based on preferences
        actions = self._apply_preferences(actions, req)

        # 3) build candidate plans (beam search)
        plans = self._beam_search(profile, actions, req, beam_width=25, max_depth=8)

        # 4) score plans
        scored_plans = [self._evaluate_plan(profile, plan, req) for plan in plans]
        scored_plans.sort(key=lambda x: (x["success_probability"], x["expected_score_end"]), reverse=True)

        best = scored_plans[0] if scored_plans else None
        alts = scored_plans[1:4] if len(scored_plans) > 1 else []

        # Save snapshot (profile_id if available)
        profile_id = profile.get('id', None)
        if profile_id:
            snapshot_engine = SnapshotEngine()
            snapshot_engine.save_snapshot(profile_id, profile, current_score)

        # Composite optimization by default
        features = self.engine._to_dict(profile)
        model_scores = {}
        for model_name in ["fico8", "fico9", "fico10"]:
            model = ModelRegistry.get(model_name)[0]
            model_scores[model_name] = model.score(features)
        composite = int(model_scores.get("fico8", 0) * 0.4 + model_scores.get("fico9", 0) * 0.3 + model_scores.get("fico10", 0) * 0.3)

        return {
            "current_score": current_score,
            "composite": composite,
            "model_scores": model_scores,
            "best_plan": best,
            "alternatives": alts,
        }

    def _apply_preferences(self, actions: List[Dict[str, Any]], req: GoalRequest) -> List[Dict[str, Any]]:
        filtered = []
        for a in actions:
            if req.preferences.avoid_new_accounts and a["type"] == "new_account":
                continue
            if req.preferences.avoid_hard_inquiries and a.get("hard_inquiry", False):
                continue
            filtered.append(a)
        return filtered

    def _beam_search(self, profile, actions, req, beam_width=25, max_depth=8):
        # Each node: (plan_actions, budget_used)
        beam = [([], 0.0)]
        for _ in range(max_depth):
            candidates = []
            for plan, spent in beam:
                for a in actions:
                    cost = float(a.get("cash_required", 0))
                    if spent + cost > req.budget:
                        continue
                    candidates.append((plan + [a], spent + cost))

            # heuristic: keep cheapest + highest estimated gain
            candidates = self._dedupe(candidates)
            candidates = sorted(candidates, key=lambda x: x[1])[: beam_width]
            beam = candidates

        return [p for p, _ in beam]

    def _evaluate_plan(self, profile, plan, req):
        import random
        import numpy as np
        sim_profile = copy.deepcopy(profile)

        # Apply multi-action scenario (you already have this)
        scenario_result = self.scenario_analyzer.run(sim_profile, plan)

        # Scenario returns score deltas + events; timeline engine builds curve
        timeline = self.timeline_engine.build_timeline(
            base_score=scenario_result["current_score"],
            events=scenario_result["timeline_events"],
            total_weeks=req.timeline_weeks
        )

        expected_end = timeline[-1]

        # Monte Carlo simulation for probability estimation
        n_sim = 200
        mc_scores = []
        for _ in range(n_sim):
            # Randomize action effectiveness (simulate uncertainty)
            sim_timeline = list(timeline)
            for i in range(1, len(sim_timeline)):
                # Add noise: +/- 5-15 points, more in early weeks
                noise = random.gauss(0, 7 + 8 * (1 - i/len(sim_timeline)))
                sim_timeline[i] = int(sim_timeline[i] + noise)
            mc_scores.append(sim_timeline[-1])
        mc_scores = np.array(mc_scores)
        success_prob = float((mc_scores >= req.target_score).sum() / n_sim)

        # Confidence intervals
        confidence = {
            "conservative": int(np.percentile(mc_scores, 10)),
            "realistic": int(np.percentile(mc_scores, 50)),
            "optimistic": int(np.percentile(mc_scores, 90)),
        }

        return {
            "actions": plan,
            "budget_used": sum(float(a.get("cash_required", 0)) for a in plan),
            "timeline": [{"week": i, "score": s} for i, s in enumerate(timeline)],
            "expected_score_end": expected_end,
            "success_probability": round(success_prob, 2),
            "confidence": confidence,
        }

    def _success_probability(self, expected_end, target, scenario_result):
        conf = scenario_result.get("confidence", {})
        conservative = conf.get("conservative", expected_end)
        optimistic = conf.get("optimistic", expected_end)

        if conservative >= target:
            return 0.9
        if optimistic < target:
            return 0.1
        # linear interpolation in between
        span = max(1, optimistic - conservative)
        return max(0.1, min(0.9, (expected_end - target + span) / span))

    def _dedupe(self, candidates):
        seen = set()
        out = []
        for plan, spent in candidates:
            key = tuple((a.get("type"), a.get("account_id"), a.get("target_balance")) for a in plan)
            if key in seen:
                continue
            seen.add(key)
            out.append((plan, spent))
        return out
