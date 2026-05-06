import { Mail, Calendar, MapPin, Edit3, ShieldCheck, Activity, Target } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../lib/api';
import { bmi, bmiLabel, defaultProfile } from '../lib/recommendationData';
import type { HealthProfile } from '../lib/recommendationData';
import { useTheme } from '../contexts/ThemeContext';
import { displayHeight, displayWeight, heightUnit, weightUnit } from '../lib/units';

export default function UserAccount() {
  const { user } = useAuth();
  const { measurementSystem } = useTheme();
  const [profile, setProfile] = useState<HealthProfile | null>(null);

  useEffect(() => {
    api.profile()
      .then((data) => setProfile({ ...defaultProfile, ...(data as Partial<HealthProfile>) }))
      .catch(() => setProfile(null));
  }, []);

  const name = [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.username || "Athlete";
  const avatarSeed = encodeURIComponent(user?.username || user?.email || "FitGenius");
  const bmiValue = profile ? bmi(profile) : 0;

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-content-reveal">
      <div className="mb-4">
        <h2 className="text-2xl font-bold">User Profile</h2>
        <p className="text-muted-foreground mt-1">Manage your public identity and connected fitness data.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 border border-border bg-card rounded-2xl shadow-card overflow-hidden">
          <div className="h-24 bg-gradient-to-r from-primary/80 to-accent/80"></div>
          <div className="px-6 pb-6 relative">
            <div className="h-20 w-20 rounded-full bg-gradient-card border-4 border-card bg-background -mt-10 mb-4 overflow-hidden shadow-sm hover-lift mx-auto">
              <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${avatarSeed}&backgroundColor=b6e3f4`} alt="User avatar" className="h-full w-full object-cover" />
            </div>
            <div className="text-center mb-6">
              <h3 className="text-xl font-bold">{name}</h3>
              <p className="text-sm text-muted-foreground flex items-center justify-center gap-1 mt-1">
                <MapPin size={14} /> Backend account
              </p>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-secondary/10 text-secondary text-xs font-semibold mt-3">
                <ShieldCheck size={14} /> Authenticated
              </span>
            </div>
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Mail size={16} /> {user?.email || "No email set"}
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Calendar size={16} /> Joined {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "recently"}
              </div>
            </div>
            <Link to="/settings" className="w-full mt-6 py-2 border border-border hover:bg-muted text-sm font-semibold rounded-lg transition-colors flex items-center justify-center gap-2">
              <Edit3 size={16} /> Account Settings
            </Link>
          </div>
        </div>

        <div className="md:col-span-2 space-y-6">
          <div className="border border-border bg-card rounded-2xl p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <Activity className="text-primary" size={20} /> Health Profile
              </h3>
              <Link to="/profile" className="px-4 py-1.5 bg-primary/10 text-primary hover:bg-primary/20 text-xs font-semibold rounded-lg transition-colors border border-primary/20">
                Update Profile
              </Link>
            </div>
            {profile ? (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <BioCard label="Age" value={String(profile.age)} />
                <BioCard label="Weight" value={`${displayWeight(profile.weight, measurementSystem)} ${weightUnit(measurementSystem).toLowerCase()}`} />
                <BioCard label="Height" value={`${displayHeight(profile.height, measurementSystem)} ${heightUnit(measurementSystem).toLowerCase()}`} />
                <BioCard label="BMI" value={String(bmiValue)} status={bmiLabel(bmiValue)} />
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No backend health profile found yet.</p>
            )}
          </div>

          <div className="border border-border bg-card rounded-2xl p-6 shadow-sm">
            <h3 className="text-lg font-bold flex items-center gap-2 mb-6">
              <Target className="text-accent" size={20} /> Current Recommender Config
            </h3>
            {profile ? (
              <div className="space-y-4">
                <ConfigRow label="Primary Goal" value={profile.fitness_goal.replace("_", " ")} />
                <ConfigRow label="Experience Level" value={profile.experience_level} />
                <ConfigRow label="Preferred Equipment" value={profile.available_equipment.replace("_", " ")} />
                <ConfigRow label="Training Frequency" value={`${profile.exercise_frequency} days / week`} />
              </div>
            ) : (
              <Link to="/profile" className="inline-flex rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground">Create health profile</Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ConfigRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-border/50 last:border-b-0">
      <span className="text-muted-foreground text-sm font-medium">{label}</span>
      <span className="font-semibold capitalize">{value}</span>
    </div>
  );
}

function BioCard({ label, value, status }: { label: string; value: string; status?: string }) {
  return (
    <div className="bg-muted/30 border border-border rounded-xl p-4 text-center">
      <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold mb-1">{label}</div>
      <div className="text-xl font-bold tracking-tight">{value}</div>
      {status && <div className="text-[10px] font-bold uppercase tracking-wider text-secondary mt-1">{status}</div>}
    </div>
  );
}
