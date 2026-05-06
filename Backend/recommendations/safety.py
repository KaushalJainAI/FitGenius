"""
Safety and Context module for the recommendation engine.
Handles medical safety filters, health notes, and daily context adjustments.
"""

import re


EMERGENCY_MESSAGE = (
    "I cannot safely generate a workout or diet recommendation for this situation. "
    "Your message or health status includes possible red-flag symptoms. Please seek urgent medical care "
    "or contact a qualified clinician before exercising or changing your diet."
)

CLINICIAN_REVIEW_MESSAGE = (
    "I cannot safely generate a personalized workout or diet plan for this situation without clinician review. "
    "This may require individualized medical guidance from a physician, registered dietitian, or physiotherapist. "
    "I can still provide general education and help you prepare questions for a professional."
)

GENERAL_SAFETY_DISCLAIMER = (
    "FitGenius provides general fitness and nutrition education, not medical diagnosis, treatment, "
    "medication advice, or medical nutrition therapy."
)


def assess_medical_safety(profile=None, checkin=None, text="") -> dict:
    """
    Deterministic safety triage shared by recommendations and chat.
    Returns level: ok, caution, clinician_review, or emergency.
    """
    haystack_parts = [text or ""]
    if profile:
        haystack_parts.extend([
            getattr(profile, "chronic_disease", "") or "",
            getattr(profile, "blood_pressure", "") or "",
            getattr(profile, "fitness_goal", "") or "",
        ])
    if checkin:
        haystack_parts.extend([
            getattr(checkin, "injury_area", "") or "",
            getattr(checkin, "notes", "") or "",
            getattr(checkin, "preferred_intensity", "") or "",
        ])

    haystack = " ".join(haystack_parts).lower()
    reasons = []
    level = "ok"

    emergency_patterns = [
        r"\b(chest pain|chest tightness|heart attack)\b",
        r"\b(fainting|fainted|passed out|blackout)\b",
        r"\b(severe dizziness|cannot breathe|shortness of breath at rest)\b",
        r"\b(blood glucose emergency|hypoglycemia|hyperglycemia|diabetic ketoacidosis)\b",
        r"\b(suspected fracture|broken bone|serious injury)\b",
    ]
    clinician_patterns = [
        r"\b(pregnan|postpartum|eating disorder|anorexia|bulimia|purging|binge eating)\b",
        r"\b(kidney disease|renal disease|dialysis|ckd)\b",
        r"\b(diabetes medication|insulin dose|metformin dose|blood pressure medication)\b",
        r"\b(swelling|joint locking|locked knee|cannot bear weight|worsening pain)\b",
    ]

    for pattern in emergency_patterns:
        if re.search(pattern, haystack):
            reasons.append("Possible red-flag symptom or emergency.")
            level = "emergency"
            break

    if level != "emergency":
        for pattern in clinician_patterns:
            if re.search(pattern, haystack):
                reasons.append("Situation may require individualized clinician guidance.")
                level = "clinician_review"
                break

    if profile and level not in ("emergency", "clinician_review"):
        chronic = (getattr(profile, "chronic_disease", "") or "").lower()
        if "heart" in chronic or "kidney" in chronic or "renal" in chronic:
            reasons.append("Chronic condition requires clinician-aware plan review.")
            level = "clinician_review"
        elif getattr(profile, "hypertension", False) or getattr(profile, "diabetes", False):
            reasons.append("Medical flag detected; recommendations must stay conservative.")
            level = "caution"

    if checkin and level not in ("emergency", "clinician_review"):
        if getattr(checkin, "pain_or_injury", False):
            reasons.append("Pain or injury reported; avoid pain-provoking exercise.")
            level = "caution"
        if (getattr(checkin, "soreness_level", 0) or 0) >= 4:
            reasons.append("High soreness reported; reduce intensity and volume.")
            level = "caution"

    message = GENERAL_SAFETY_DISCLAIMER
    if level == "emergency":
        message = EMERGENCY_MESSAGE
    elif level == "clinician_review":
        message = CLINICIAN_REVIEW_MESSAGE
    elif level == "caution":
        message = (
            f"{GENERAL_SAFETY_DISCLAIMER} Because your profile/check-in has safety flags, "
            "keep activity low to moderate, avoid pain-provoking movements, and consult a qualified professional if symptoms worsen."
        )

    return {
        "level": level,
        "reasons": sorted(set(reasons)),
        "message": message,
        "blocks_plan": level in ("emergency", "clinician_review"),
    }


def build_safety_only_recommendation(profile, checkin, assessment: dict) -> dict:
    """Return a persisted recommendation-shaped response when a plan is unsafe."""
    snapshot = {
        'age': getattr(profile, 'age', None),
        'gender': getattr(profile, 'gender', ''),
        'height': getattr(profile, 'height', None),
        'weight': getattr(profile, 'weight', None),
        'bmi': getattr(profile, 'bmi', None),
        'fitness_goal': getattr(profile, 'fitness_goal', ''),
        'activity_level': getattr(profile, 'activity_level', ''),
        'experience_level': getattr(profile, 'experience_level', ''),
        'equipment': getattr(profile, 'available_equipment', ''),
        'dietary_preference': getattr(profile, 'dietary_preference', ''),
        'hypertension': getattr(profile, 'hypertension', False),
        'diabetes': getattr(profile, 'diabetes', False),
        'chronic_disease': getattr(profile, 'chronic_disease', ''),
    }
    reasons = assessment.get("reasons") or ["Safety guard triggered."]
    explanation = "Safety guard blocked personalized plan generation:\n" + "\n".join(
        f"- {reason}" for reason in reasons
    )
    return {
        'status': 'completed',
        'confidence': 'low',
        'algorithm_used': 'safety_guard',
        'workout_split': 'Clinician review required',
        'exercise_plan': [],
        'workout_days_per_week': 0,
        'diet_plan': {
            'guidance': 'Personalized diet plan withheld pending qualified medical review.',
        },
        'daily_calorie_target': None,
        'macro_split': {},
        'health_notes': assessment.get("message", GENERAL_SAFETY_DISCLAIMER),
        'llm_recommendation': assessment.get("message", GENERAL_SAFETY_DISCLAIMER),
        'rag_context_chunks': reasons,
        'profile_snapshot': snapshot,
        'similar_profiles_count': 0,
        'avg_similarity_score': None,
        'explanation': explanation,
    }


def guard_chat_response(message, answer, profile=None, checkin=None) -> str:
    """Clamp chat output when the user asks for unsafe medical guidance."""
    assessment = assess_medical_safety(profile=profile, checkin=checkin, text=message)
    if assessment["blocks_plan"]:
        return assessment["message"]
    if assessment["level"] == "caution":
        return f"{answer}\n\nSafety note: {assessment['message']}"
    return answer

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
