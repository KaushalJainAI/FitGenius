"""
Safety and Context module for the recommendation engine.
Handles medical safety filters, health notes, and daily context adjustments.
"""

def checkin_context_score(checkin) -> dict:
    """
    Derive context flags from a DailyCheckIn for plan adjustments.
    Returns a dict of boolean flags.
    """
    return {
        'low_energy': checkin.energy_level <= 2 if checkin else False,
        'high_soreness': checkin.soreness_level >= 4 if checkin else False,
        'poor_sleep': (checkin.sleep_hours or 8) < 6 if checkin else False,
        'high_stress': checkin.stress_level >= 4 if checkin else False,
        'injury_present': checkin.pain_or_injury if checkin else False,
        'injury_area': (checkin.injury_area or '').lower() if checkin else '',
        'low_available_minutes': (checkin.available_minutes or 60) < 30 if checkin else False,
        'low_steps': (checkin.daily_steps or 8000) < 4000 if checkin else False,
        'high_steps': (checkin.daily_steps or 0) > 15000 if checkin else False,
        'preferred_low': (checkin.preferred_intensity == 'low') if checkin else False,
        'preferred_high': (checkin.preferred_intensity == 'high') if checkin else False,
    }


def apply_medical_safety_filter(exercise_plan: list, checkin, profile) -> tuple:
    """
    Apply hard medical safety constraints to an exercise plan.
    Returns (filtered_plan, extra_notes, removed_reasons).
    """
    extra_notes = []
    removed_reasons = []

    for day in exercise_plan:
        kept_exercises = []
        for ex in day.get('exercises', []):
            exclude = False
            reason = ''

            name_lower = ex.get('name', '').lower()
            muscle_lower = ex.get('muscle', '').lower()

            # Injury area exclusion
            if checkin and checkin.pain_or_injury and checkin.injury_area:
                injury_area = checkin.injury_area.lower()
                injury_keywords = {
                    'knee': ['quads', 'hamstrings', 'glutes', 'calves', 'knee', 'leg press', 'squat', 'lunge'],
                    'shoulder': ['chest', 'shoulders', 'triceps', 'overhead', 'press', 'pull-up'],
                    'back': ['back', 'deadlift', 'row', 'pull-up', 'lat', 'lats'],
                    'wrist': ['curl', 'wrist', 'press', 'push-up'],
                    'ankle': ['calves', 'jump', 'box', 'run'],
                }
                keywords = injury_keywords.get(injury_area, [])
                if keywords and any(k in name_lower or k in muscle_lower for k in keywords):
                    exclude = True
                    reason = f"Skipped '{ex['name']}' — targets injured area ({checkin.injury_area})."

            # High BMI: avoid high-impact
            if profile.bmi and profile.bmi >= 35:
                high_impact = ['burpee', 'box jump', 'jump squat', 'mountain climber', 'jumping']
                if any(h in name_lower for h in high_impact):
                    exclude = True
                    reason = f"Replaced high-impact '{ex['name']}' with low-impact alternative."

            # Hypertension: avoid heavy isometric holds
            if profile.hypertension:
                isometric = ['plank hold', 'wall sit', 'isometric']
                if any(i in name_lower for i in isometric) and ex.get('reps', '') == '60s':
                    ex = dict(ex)
                    ex['reps'] = '30s'
                    reason = "Shortened plank hold for hypertension."

            if exclude:
                removed_reasons.append(reason)
            else:
                kept_exercises.append(ex)

        day['exercises'] = kept_exercises

    # Add medical notes
    if profile.diabetes:
        extra_notes.append(
            "⚠️ Diabetes: Monitor blood sugar before/after workouts. "
            "Keep fast-acting carbs available. Prioritize complex carbs."
        )
    if profile.hypertension:
        extra_notes.append(
            "⚠️ Hypertension: Avoid heavy isometric holds. "
            "Keep intensity moderate. Monitor BP before/after exercise."
        )
    if profile.bmi and profile.bmi >= 35:
        extra_notes.append(
            "⚠️ High BMI (≥35): Prefer low-impact exercises (cycling, swimming, walking). "
            "Avoid high-impact plyometrics. Focus on dietary changes."
        )

    chronic = (profile.chronic_disease or '').lower()
    if 'heart' in chronic:
        extra_notes.append(
            "⚠️ Heart condition flagged: Consult your cardiologist before starting. "
            "Begin with zone 2 steady-state cardio. Avoid HIIT initially."
        )
    if profile.smoking_habit:
        extra_notes.append(
            "⚠️ Smoking detected: Cardiovascular capacity may be reduced. "
            "Start with lower intensity and progress gradually."
        )

    return exercise_plan, extra_notes, removed_reasons


def apply_context_adjustments(exercise_plan: list, checkin, profile) -> list:
    """
    Adjust workout plan based on daily check-in context flags.
    Returns adjusted exercise plan.
    """
    if not checkin:
        return exercise_plan

    ctx = checkin_context_score(checkin)
    adjusted_plan = []

    for day in exercise_plan:
        day_copy = dict(day)
        exercises = []

        for ex in day.get('exercises', []):
            ex_copy = dict(ex)

            # Low energy / poor sleep: reduce sets and reps
            if ctx['low_energy'] or ctx['poor_sleep']:
                reps_val = ex_copy.get('reps', '')
                if isinstance(reps_val, str) and '-' in reps_val:
                    parts = reps_val.split('-')
                    try:
                        low = max(5, int(parts[0]) - 3)
                        high = max(8, int(parts[1]) - 3)
                        ex_copy['reps'] = f"{low}-{high}"
                    except ValueError:
                        pass
                sets_val = ex_copy.get('sets', 3)
                if isinstance(sets_val, int) and sets_val > 2:
                    ex_copy['sets'] = sets_val - 1

            # High soreness: switch to mobility/recovery
            if ctx['high_soreness']:
                ex_copy['reps'] = '12'
                ex_copy['sets'] = 2
                # Add note to focus area
                if 'focus' in day_copy:
                    day_copy['focus'] = 'Recovery / ' + day_copy['focus']

            exercises.append(ex_copy)

        day_copy['exercises'] = exercises

        # If low available minutes, return only the first day/shorter variant
        if ctx['low_available_minutes'] and len(adjusted_plan) == 0:
            # Keep only the first day's exercises, reduce volume
            short_day = dict(day_copy)
            short_day['focus'] = 'Quick Session (Short Workout)'
            short_exercises = []
            for ex in short_day['exercises'][:4]:  # max 4 exercises
                short_ex = dict(ex)
                short_ex['sets'] = min(2, short_ex.get('sets', 3))
                short_ex['reps'] = '10'
                short_exercises.append(short_ex)
            short_day['exercises'] = short_exercises
            return [short_day]

        adjusted_plan.append(day_copy)

    return adjusted_plan


def generate_health_notes(profile) -> str:
    """Generate health-aware notes based on medical conditions."""
    notes = []

    if profile.hypertension:
        notes.append(
            "⚠️ Hypertension detected: Avoid heavy isometric holds and Valsalva maneuver. "
            "Keep intensity moderate. Monitor blood pressure before/after workouts. "
            "Reduce sodium intake in diet plan."
        )
    if profile.diabetes:
        notes.append(
            "⚠️ Diabetes detected: Monitor blood sugar before and after exercise. "
            "Keep a fast-acting carb source available during workouts. "
            "Prefer complex carbs over simple sugars in meals."
        )
    if profile.cholesterol and profile.cholesterol > 200:
        notes.append(
            "⚠️ Elevated cholesterol: Prioritize cardio sessions. "
            "Reduce saturated fat intake. Include omega-3 rich foods (salmon, walnuts, flaxseed)."
        )
    if profile.smoking_habit:
        notes.append(
            "⚠️ Smoking habit: Expect reduced cardiovascular capacity. "
            "Start with lower intensity and gradually increase. "
            "Consider breathing exercises as part of warm-up."
        )
    if profile.bmi and profile.bmi >= 35:
        notes.append(
            "⚠️ High BMI (≥35): Start with low-impact exercises (swimming, cycling, walking). "
            "Avoid high-impact jumping movements. Focus on dietary changes first."
        )

    chronic = (profile.chronic_disease or '').lower()
    if 'heart' in chronic:
        notes.append(
            "⚠️ Heart disease flagged: Consult cardiologist before starting any program. "
            "Avoid high-intensity interval training initially. Keep heart rate in zone 2."
        )

    if not notes:
        notes.append("✅ No medical contraindications detected. Standard programming applies.")

    return '\n\n'.join(notes)
