# Medical Safety Guardrails

## Purpose

Exercise and diet recommendations are medically sensitive. FitGenius therefore treats the LLM and ranking models as advisory components, not as the authority that decides whether a plan is safe.

The backend applies deterministic safety checks before personalized plans or chat answers are returned.

## Core Rule

Safety overrides personalization.

If a user profile, check-in, uploaded note, or chat message indicates a red-flag condition, the backend withholds personalized workout and diet plans and advises qualified medical review.

## Safety Levels

### `ok`
No known safety flag was detected. Standard recommendation logic may run.

### `caution`
The plan may be generated, but must stay conservative. Examples:

- diabetes or hypertension flags
- reported pain or injury without emergency terms
- high soreness
- high BMI requiring low-impact programming

The system adds caution notes, reduces or removes risky exercises, and avoids pain-provoking movements.

### `clinician_review`
The system does not generate a personalized workout or diet plan. Examples:

- kidney or renal disease
- heart disease flags
- pregnancy or postpartum concerns
- eating disorder risk
- diabetes or blood-pressure medication dosing questions
- swelling, joint locking, inability to bear weight, or worsening pain

The response provides general education only and recommends review by a physician, registered dietitian, or physiotherapist.

### `emergency`
The system does not generate a plan and advises urgent medical care. Examples:

- chest pain or chest tightness
- fainting or passing out
- severe dizziness
- suspected fracture or serious injury
- blood glucose emergency
- shortness of breath at rest

## Backend Implementation

The shared safety layer lives in:

- `Backend/recommendations/safety.py`

Important functions:

- `assess_medical_safety(profile, checkin, text)`
- `build_safety_only_recommendation(profile, checkin, assessment)`
- `apply_medical_safety_filter(exercise_plan, checkin, profile)`
- `guard_chat_response(message, answer, profile, checkin)`

Recommendation generation calls the safety assessment before template selection, KNN aggregation, reranking, calorie estimation, and RAG explanation. If the assessment blocks a plan, a saved recommendation record is still returned, but its `algorithm_used` is `safety_guard`, with no exercise plan and no personalized macro prescription.

Chat calls the same safety assessment before the NVIDIA LLM. If the user asks for unsafe medical guidance, the model is bypassed and a deterministic safety message is returned.

## Product Boundaries

FitGenius may:

- provide general fitness and nutrition education
- explain an existing plan
- suggest low-risk substitutions
- recommend lower intensity, rest, or professional review
- cite trusted guidance sources used in RAG

FitGenius must not:

- diagnose disease
- prescribe medication
- adjust medication dosages
- provide medical nutrition therapy for kidney disease, pregnancy complications, eating disorder risk, or diabetes emergencies
- recommend exercise through red-flag symptoms
- promise outcomes

## Testing Expectations

Safety tests should cover:

- chest pain in chat returns urgent-care guidance only
- kidney disease blocks personalized diet/macros
- eating disorder language blocks calorie-deficit planning
- knee injury removes squats, lunges, jumps, and other pain-provoking lower-body movements
- hypertension avoids heavy isometric holds and warns against breath-holding
- diabetes medication questions are escalated to clinician review
