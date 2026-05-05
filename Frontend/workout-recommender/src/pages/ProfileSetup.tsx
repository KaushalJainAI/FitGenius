import React, { useState } from 'react';
import { Sparkles, Settings, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ProfileSetup() {
  const [isGenerating, setIsGenerating] = useState(false);
  const navigate = useNavigate();

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      navigate('/plan');
    }, 1500);
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto animate-content-reveal">
      <div className="bg-card border border-border rounded-2xl shadow-card flex flex-col items-center justify-center p-8 mb-6 relative overflow-hidden text-center group">
         <div className="absolute top-0 right-0 w-32 h-32 bg-secondary/10 rounded-full blur-3xl -mr-10 -mt-10 transition-smooth group-hover:bg-secondary/20"></div>
         <Activity size={40} className="text-secondary/50 mb-4" />
         <h2 className="text-2xl font-bold mb-2">Configure Your Profile</h2>
         <p className="text-muted-foreground w-11/12 mx-auto">
            These constraints are sent to the AI matrix factorization algorithm to suggest the best possible combination of exercises and sets for your level and fitness goals.
         </p>
      </div>

      <div className="bg-card border border-border rounded-2xl shadow-card overflow-hidden flex flex-col">
        <div className="border-b border-border p-5 bg-muted/30">
          <h2 className="font-semibold text-lg flex items-center justify-between">
            Profile Setup & Constraints
            <Settings className="h-5 w-5 text-muted-foreground" />
          </h2>
        </div>
        <form onSubmit={handleGenerate} className="p-6 space-y-5 flex-1 flex flex-col">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Age</label>
              <input type="number" defaultValue={25} className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Weight</label>
              <div className="relative">
                <input type="number" defaultValue={68} className="w-full bg-background border border-border rounded-lg pl-3 pr-8 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">KG</span>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Height</label>
              <div className="relative">
                <input type="number" defaultValue={170} className="w-full bg-background border border-border rounded-lg pl-3 pr-9 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">CM</span>
              </div>
            </div>
          </div>

          <div className="bg-secondary/10 border border-secondary/20 rounded-lg px-4 py-3 flex items-center justify-between">
            <span className="text-sm font-medium">Estimated BMI</span>
            <span className="text-sm font-bold text-secondary">23.5 (Healthy)</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Goal</label>
              <select className="w-full bg-background border border-border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium appearance-none">
                <option>Muscle Gain</option>
                <option>Weight Loss</option>
                <option>Endurance</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex justify-between">
                 Experience
                 <div className="bg-primary rounded-full w-8 h-4 relative flex items-center px-[2px] transition-all"><div className="w-3 h-3 bg-white rounded-full ml-auto"></div></div>
              </label>
              <select className="w-full bg-background border border-border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium appearance-none">
                <option>Advanced</option>
                <option selected>Intermediate</option>
                <option>Beginner</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="space-y-3 flex flex-col justify-start">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Equipment</label>
              <div className="grid grid-cols-2 gap-3">
                 <label className="flex items-center justify-center p-3 rounded-xl border-2 border-primary/50 bg-primary/10 cursor-pointer font-medium text-sm transition-all shadow-sm">
                    <input type="radio" name="equip" defaultChecked className="hidden" />
                    Full Gym
                 </label>
                 <label className="flex items-center justify-center p-3 rounded-xl border-2 border-transparent bg-muted cursor-pointer hover:bg-muted/80 font-medium text-sm transition-all text-muted-foreground">
                    <input type="radio" name="equip" className="hidden" />
                    Dumbbells
                 </label>
              </div>
            </div>
            
            <div className="space-y-3 flex flex-col justify-start">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Days per week</label>
              <div className="flex gap-2">
                 {[2, 3, 4, 5].map((d) => (
                    <label key={d} className={`flex-1 flex items-center justify-center p-3 rounded-xl border-2 cursor-pointer font-medium text-sm transition-all ${d === 3 ? 'border-primary/50 bg-primary/10' : 'border-transparent bg-muted hover:bg-muted/80 text-muted-foreground w-full'}`}>
                       <input type="radio" name="days" defaultChecked={d === 3} className="hidden" />
                       {d}{d === 5 ? '+' : ''}
                    </label>
                 ))}
              </div>
            </div>
          </div>

          <div className="pt-6 mt-auto border-t border-border">
            <button 
              type="submit" 
              disabled={isGenerating}
              className="w-full relative overflow-hidden rounded-xl bg-gradient-hero hover:opacity-90 text-white font-medium py-3.5 shadow-elegant hover-glow transition-all disabled:opacity-80 flex items-center justify-center gap-2 uppercase tracking-wider text-sm"
            >
              {isGenerating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Generating Pipeline...</span>
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  <span>Update Profile & Generate Plan</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
