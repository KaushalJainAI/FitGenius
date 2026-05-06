import React, { useEffect, useState } from 'react';
import { Dumbbell, ArrowRight, User, Mail, Lock, Activity } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../lib/api';
import { useTheme } from '../contexts/ThemeContext';
import { displayHeight, displayWeight, heightUnit, inputHeight, inputWeight, weightUnit } from '../lib/units';

export default function Register() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [step, setStep] = useState(1);
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [age, setAge] = useState(25);
  const [weight, setWeight] = useState(68);
  const [height, setHeight] = useState(170);
  const [fitnessGoal, setFitnessGoal] = useState("weight_gain");
  const [experienceLevel, setExperienceLevel] = useState("intermediate");
  const navigate = useNavigate();
  const { register, login } = useAuth();
  const { measurementSystem } = useTheme();

  useEffect(() => {
    api.profileDefaults()
      .then((defaults) => {
        const profileDefaults = defaults as { age?: number; weight?: number; height?: number; fitness_goal?: string; experience_level?: string };
        if (profileDefaults.age) setAge(profileDefaults.age);
        if (profileDefaults.weight) setWeight(profileDefaults.weight);
        if (profileDefaults.height) setHeight(profileDefaults.height);
        if (profileDefaults.fitness_goal) setFitnessGoal(profileDefaults.fitness_goal);
        if (profileDefaults.experience_level) setExperienceLevel(profileDefaults.experience_level);
      })
      .catch(() => {});
  }, []);

  const handleNext = (e: React.MouseEvent) => {
    e.preventDefault();
    setStep(2);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setIsLoading(true);
    setError("");
    try {
      const [firstName, ...rest] = fullName.trim().split(/\s+/);
      const cleanUsername = username.trim().toLowerCase();
      const cleanEmail = email.trim().toLowerCase();

      await register({
        username: cleanUsername,
        email: cleanEmail,
        password,
        password2: confirmPassword,
        first_name: firstName || cleanUsername,
        last_name: rest.join(" "),
        phone,
        date_of_birth: dateOfBirth || null,
      });
      await login(cleanEmail, password);
      await api.saveProfile({
        age,
        weight,
        height,
        gender: "other",
        fitness_goal: fitnessGoal,
        experience_level: experienceLevel,
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
        preferred_workout_type: "mixed",
        available_equipment: "full_gym",
      });
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 py-12 relative overflow-hidden bg-background">
      {/* Background decorations */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/20 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-2xl bg-card border border-border shadow-2xl rounded-3xl overflow-hidden relative z-10 animate-fade-in-up">
        <div className="flex border-b border-border/50">
           <div className={`flex-1 p-4 text-center font-bold text-sm tracking-wider uppercase transition-colors ${step === 1 ? 'bg-primary/10 text-primary border-b-2 border-primary' : 'text-muted-foreground bg-muted/20'}`}>
              Step 1: Account
           </div>
           <div className={`flex-1 p-4 text-center font-bold text-sm tracking-wider uppercase transition-colors ${step === 2 ? 'bg-primary/10 text-primary border-b-2 border-primary' : 'text-muted-foreground bg-muted/20'}`}>
              Step 2: Bio Data
           </div>
        </div>

        <div className="p-8 sm:p-10">
           <div className="flex flex-col items-center mb-8">
             <div className="h-14 w-14 bg-primary/10 rounded-2xl flex items-center justify-center text-primary mb-4 shadow-inner">
               <Dumbbell size={32} />
             </div>
             <h1 className="text-2xl font-bold tracking-tight text-foreground">
               {step === 1 ? 'Create Your Account' : 'Define Your Matrix Constraints'}
             </h1>
             <p className="text-muted-foreground text-sm mt-2 text-center max-w-sm">
               {step === 1
                 ? 'Join FitGenius AI to unlock hyper-personalized workout routines.'
                 : 'We need this data to accurately calculate your baseline intensity levels for the recommender logic.'}
             </p>
           </div>

           <form onSubmit={handleRegister} className="space-y-6">

             {step === 1 && (
                <div className="space-y-5 animate-slide-in-right">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Full Name</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                      <input
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        type="text"
                        placeholder="Sarah Connor"
                        required
                        className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Username</label>
                    <div className="relative">
                      <Activity className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                      <input
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        type="text"
                        placeholder="sarah_connor"
                        required
                        className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Email Address</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                      <input
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        type="email"
                        placeholder="sarah@example.com"
                        required
                        className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Phone</label>
                      <input
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        type="tel"
                        placeholder="+91 98765 43210"
                        className="w-full bg-background border border-border rounded-xl px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Date of Birth</label>
                      <input
                        value={dateOfBirth}
                        onChange={(e) => setDateOfBirth(e.target.value)}
                        type="date"
                        className="w-full bg-background border border-border rounded-xl px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                      <input
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        type="password"
                        placeholder="••••••••"
                        required
                        className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Confirm Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                      <input
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        type="password"
                        placeholder="••••••••"
                        required
                        className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium"
                      />
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleNext}
                    className="w-full relative overflow-hidden rounded-xl bg-gradient-hero text-white font-semibold py-3.5 shadow-elegant hover-glow transition-all flex items-center justify-center gap-2 mt-8"
                  >
                    Continue to Profile Setup <ArrowRight size={18} />
                  </button>
                </div>
             )}

             {step === 2 && (
                <div className="space-y-6 animate-slide-in-right">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Age</label>
                      <input type="number" value={age} onChange={(e) => setAge(Number(e.target.value))} required className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Weight</label>
                      <div className="relative">
                        <input type="number" value={displayWeight(weight, measurementSystem)} onChange={(e) => setWeight(inputWeight(e.target.value === "" ? "" : Number(e.target.value), measurementSystem) || 0)} required className="w-full bg-background border border-border rounded-lg pl-3 pr-8 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">{weightUnit(measurementSystem)}</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Height</label>
                      <div className="relative">
                        <input type="number" value={displayHeight(height, measurementSystem)} onChange={(e) => setHeight(inputHeight(e.target.value === "" ? "" : Number(e.target.value), measurementSystem) || 0)} required className="w-full bg-background border border-border rounded-lg pl-3 pr-9 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">{heightUnit(measurementSystem)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Primary Goal</label>
                      <select value={fitnessGoal} onChange={(e) => setFitnessGoal(e.target.value)} required className="w-full bg-background border border-border rounded-lg px-3 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium appearance-none">
                        <option value="weight_loss">Weight Loss</option>
                        <option value="weight_gain">Weight Gain</option>
                        <option value="maintenance">Maintenance</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Prior Experience</label>
                      <select value={experienceLevel} onChange={(e) => setExperienceLevel(e.target.value)} required className="w-full bg-background border border-border rounded-lg px-3 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium appearance-none">
                        <option value="advanced">Advanced</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="beginner">Beginner</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex gap-4 pt-4 mt-auto border-t border-border/50">
                    {error && <div className="basis-full rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive-foreground whitespace-pre-line">{error}</div>}
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="px-6 py-3.5 text-sm font-semibold text-muted-foreground hover:text-foreground transition-colors"
                    >
                      Back
                    </button>
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="flex-1 relative overflow-hidden rounded-xl bg-gradient-hero text-white font-semibold py-3.5 shadow-elegant hover-glow transition-all disabled:opacity-80 flex items-center justify-center gap-2"
                    >
                      {isLoading ? (
                         <>
                           <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                           <span>Initializing AI Models...</span>
                         </>
                      ) : (
                         <>
                           <Activity size={18} />
                           <span>Complete Registration</span>
                         </>
                      )}
                    </button>
                  </div>
                </div>
             )}
           </form>

           {step === 1 && (
              <div className="mt-8 text-center animate-slide-in-right">
                <p className="text-sm text-muted-foreground">
                  Already mapped your constraints?{' '}
                  <Link to="/login" className="font-semibold text-foreground hover:text-primary transition-colors">
                    Sign in here
                  </Link>
                </p>
              </div>
           )}
        </div>
      </div>
    </div>
  );
}
