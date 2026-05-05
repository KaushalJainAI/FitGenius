export type HealthProfile = {
  age: number;
  gender: string;
  height: number;
  weight: number;
  chronic_disease: string;
  hypertension: boolean;
  diabetes: boolean;
  blood_pressure_systolic: number | "";
  blood_pressure_diastolic: number | "";
  cholesterol: number | "";
  genetic_risk: string;
  activity_level: string;
  exercise_frequency: number;
  daily_steps: number | "";
  sleep_quality: string;
  smoking_habit: boolean;
  alcohol_consumption: string;
  avg_heart_rate: number | "";
  dietary_preference: string;
  caloric_intake: number | "";
  protein_intake: number | "";
  carbohydrate_intake: number | "";
  fat_intake: number | "";
  cuisine_preference: string;
  food_aversion: string;
  fitness_goal: string;
  experience_level: string;
  preferred_workout_type: string;
  available_equipment: string;
};

export type DailyCheckIn = {
  date: string;
  current_weight: number | "";
  sleep_quality: string;
  sleep_hours: number | "";
  daily_steps: number | "";
  energy_level: number;
  soreness_level: number;
  stress_level: number;
  resting_heart_rate: number | "";
  workout_completed: boolean;
  pain_or_injury: boolean;
  injury_area: string;
  available_minutes: number | "";
  preferred_intensity: string;
  notes: string;
};

export type Recommendation = {
  status: string;
  confidence: string;
  algorithm_used: string;
  workout_split: string;
  workout_days_per_week: number;
  exercise_plan: Array<{
    day: string;
    focus: string;
    exercises: Array<{ name: string; muscle: string; equipment: string; sets: number; reps: string }>;
  }>;
  diet_plan: Record<string, string>;
  daily_calorie_target: number;
  macro_split: { protein_g: number; carbs_g: number; fat_g: number };
  health_notes: string;
  llm_recommendation: string;
  explanation: string;
  similar_profiles_count: number;
  avg_similarity_score: number;
  created_at: string;
};

const profileKey = "fitgenius.healthProfile";
const checkinKey = "fitgenius.dailyCheckIn";
const recommendationKey = "fitgenius.latestRecommendation";

export const defaultProfile: HealthProfile = {
  age: 25,
  gender: "female",
  height: 170,
  weight: 68,
  chronic_disease: "",
  hypertension: false,
  diabetes: false,
  blood_pressure_systolic: "",
  blood_pressure_diastolic: "",
  cholesterol: "",
  genetic_risk: "low",
  activity_level: "moderate",
  exercise_frequency: 3,
  daily_steps: 8000,
  sleep_quality: "good",
  smoking_habit: false,
  alcohol_consumption: "none",
  avg_heart_rate: "",
  dietary_preference: "no_preference",
  caloric_intake: "",
  protein_intake: "",
  carbohydrate_intake: "",
  fat_intake: "",
  cuisine_preference: "",
  food_aversion: "",
  fitness_goal: "muscle_gain",
  experience_level: "intermediate",
  preferred_workout_type: "mixed",
  available_equipment: "full_gym",
};

export const defaultCheckIn: DailyCheckIn = {
  date: new Date().toISOString().slice(0, 10),
  current_weight: "",
  sleep_quality: "good",
  sleep_hours: 7.5,
  daily_steps: 8000,
  energy_level: 3,
  soreness_level: 1,
  stress_level: 2,
  resting_heart_rate: "",
  workout_completed: false,
  pain_or_injury: false,
  injury_area: "",
  available_minutes: 60,
  preferred_intensity: "moderate",
  notes: "",
};

export function loadStored<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? { ...fallback, ...JSON.parse(raw) } : fallback;
  } catch {
    return fallback;
  }
}

export function getProfile() {
  return loadStored(profileKey, defaultProfile);
}

export function saveProfile(profile: HealthProfile) {
  localStorage.setItem(profileKey, JSON.stringify(profile));
}

export function getCheckIn() {
  return loadStored(checkinKey, defaultCheckIn);
}

export function saveCheckIn(checkin: DailyCheckIn) {
  localStorage.setItem(checkinKey, JSON.stringify(checkin));
}

export function getRecommendation() {
  return loadStored(recommendationKey, buildRecommendation(getProfile(), getCheckIn()));
}

export function saveRecommendation(recommendation: Recommendation) {
  localStorage.setItem(recommendationKey, JSON.stringify(recommendation));
}

export function bmi(profile: HealthProfile) {
  return profile.height ? Number((profile.weight / ((profile.height / 100) ** 2)).toFixed(1)) : 0;
}

export function bmiLabel(value: number) {
  if (value < 18.5) return "Underweight";
  if (value < 25) return "Normal";
  if (value < 30) return "Overweight";
  return "Obese";
}

export function buildRecommendation(profile: HealthProfile, checkin: DailyCheckIn): Recommendation {
  const split = profile.fitness_goal === "muscle_gain" ? "Push/Pull/Legs" : profile.fitness_goal === "endurance" ? "Cardio Strength Hybrid" : "Full Body";
  const calories = Math.round((10 * profile.weight + 6.25 * profile.height - 5 * profile.age + (profile.gender === "male" ? 5 : -161)) * 1.55 + (profile.fitness_goal === "weight_loss" ? -500 : profile.fitness_goal === "muscle_gain" ? 300 : 0));
  const short = Number(checkin.available_minutes || 60) < 30;
  const recovery = checkin.energy_level <= 2 || checkin.soreness_level >= 4 || Number(checkin.sleep_hours || 8) < 6;
  const volume = profile.experience_level === "beginner" || recovery ? 2 : profile.experience_level === "advanced" ? 4 : 3;
  const days = [
    {
      day: "Day 1",
      focus: recovery ? "Recovery / Push" : "Push (Chest, Shoulders, Triceps)",
      exercises: [
        { name: "Dumbbell Bench Press", muscle: "Chest", equipment: "Dumbbells", sets: volume, reps: recovery ? "8-10" : "10-12" },
        { name: "Shoulder Press", muscle: "Shoulders", equipment: profile.available_equipment === "bodyweight" ? "Bodyweight" : "Dumbbells", sets: volume, reps: "10-12" },
        { name: "Incline Push-Up", muscle: "Chest", equipment: "Bodyweight", sets: 2, reps: "12" },
      ],
    },
    {
      day: "Day 2",
      focus: "Legs & Core",
      exercises: [
        { name: "Goblet Squat", muscle: "Quads/Glutes", equipment: "Dumbbell", sets: volume, reps: recovery ? "8" : "10-12" },
        { name: "Romanian Deadlift", muscle: "Hamstrings", equipment: "Dumbbells", sets: volume, reps: "10" },
        { name: "Dead Bug", muscle: "Core", equipment: "Bodyweight", sets: 2, reps: "12/side" },
      ],
    },
    {
      day: "Day 3",
      focus: "Pull (Back, Biceps)",
      exercises: [
        { name: "One-Arm Row", muscle: "Back", equipment: "Dumbbell", sets: volume, reps: "10-12" },
        { name: "Band Pull-Apart", muscle: "Rear Delts", equipment: "Resistance Band", sets: 2, reps: "15" },
        { name: "Hammer Curl", muscle: "Biceps", equipment: "Dumbbells", sets: volume, reps: "12" },
      ],
    },
  ];

  const exercise_plan = short ? [{ ...days[0], focus: "Quick Session", exercises: days[0].exercises.slice(0, 2) }] : days.slice(0, profile.exercise_frequency);

  return {
    status: "completed",
    confidence: "high",
    algorithm_used: "hybrid",
    workout_split: split,
    workout_days_per_week: profile.exercise_frequency,
    exercise_plan,
    diet_plan: {
      breakfast: profile.dietary_preference === "vegetarian" ? "Paneer bhurji with multigrain toast" : "Eggs with oats and fruit",
      lunch: "Protein bowl with rice, vegetables, and healthy fats",
      dinner: "Lean protein with complex carbs and greens",
      snacks: "Greek yogurt, fruit, nuts, or a protein shake",
    },
    daily_calorie_target: calories,
    macro_split: {
      protein_g: Math.round((calories * 0.3) / 4),
      carbs_g: Math.round((calories * 0.45) / 4),
      fat_g: Math.round((calories * 0.25) / 9),
    },
    health_notes: [
      profile.hypertension ? "Hypertension: keep intensity moderate and avoid heavy breath-holding." : "",
      profile.diabetes ? "Diabetes: monitor blood sugar around sessions and keep fast carbs available." : "",
      checkin.pain_or_injury ? `Injury context: avoid loading ${checkin.injury_area || "the painful area"} today.` : "",
    ].filter(Boolean).join("\n\n") || "No medical contraindications detected. Standard programming applies.",
    llm_recommendation: `Your ${split} plan is tuned for ${profile.fitness_goal.replace("_", " ")} with ${profile.available_equipment.replace("_", " ")} access, ${profile.exercise_frequency} training days, and today's readiness context.`,
    explanation: `Matched the backend pipeline shape: stable profile features set the template, medical fields apply safety rules, and today's check-in adjusts volume, intensity, and session length.`,
    similar_profiles_count: 14,
    avg_similarity_score: 0.82,
    created_at: new Date().toISOString(),
  };
}

export const storageKeys = { profileKey, checkinKey, recommendationKey };
