import random

def placebo_schedule():
    # Generate randomized null windows or shuffled labels
    return {"placebo": True, "seed": random.getrandbits(64)}

def placebo_result():
    # Synthetic null outcome for comparison
    return {"pass": False, "p_value": 0.5, "effect": 0.0}
