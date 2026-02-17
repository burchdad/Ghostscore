"""
Calibration Engine for GhostScore

Learns correction factors between estimated and actual scores for each user/profile.
Enables self-improving, adaptive scoring.
"""
from typing import Dict, Optional
import json
import os

# Simple file-based persistence for demo; replace with DB in production
CALIBRATION_FILE = os.environ.get("CALIBRATION_FILE", "calibration_profiles.json")

def load_calibration_profiles() -> Dict[str, float]:
    if not os.path.exists(CALIBRATION_FILE):
        return {}
    with open(CALIBRATION_FILE, "r") as f:
        return json.load(f)

def save_calibration_profiles(profiles: Dict[str, float]):
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(profiles, f)

def get_correction(profile_id: str) -> float:
    profiles = load_calibration_profiles()
    return profiles.get(profile_id, 0.0)

def update_correction(profile_id: str, estimated_score: float, actual_score: float):
    profiles = load_calibration_profiles()
    correction = actual_score - estimated_score
    profiles[profile_id] = correction
    save_calibration_profiles(profiles)

def apply_calibration(profile_id: str, estimated_score: float) -> float:
    correction = get_correction(profile_id)
    return estimated_score + correction

# Example usage:
# update_correction("profile123", 712, 728)
# corrected = apply_calibration("profile123", 700)  # returns 716
