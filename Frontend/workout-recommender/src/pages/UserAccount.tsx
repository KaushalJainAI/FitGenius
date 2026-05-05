import { Mail, Calendar, MapPin, Edit3, ShieldCheck, Activity, Target } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function UserAccount() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-content-reveal">
      <div className="mb-4">
        <h2 className="text-2xl font-bold">User Profile</h2>
        <p className="text-muted-foreground mt-1">Manage your public identity and connected fitness data.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column - ID Card */}
        <div className="md:col-span-1 border border-border bg-card rounded-2xl shadow-card overflow-hidden">
           <div className="h-24 bg-gradient-to-r from-primary/80 to-accent/80"></div>
           <div className="px-6 pb-6 relative">
              <div className="h-20 w-20 rounded-full bg-gradient-card border-4 border-card bg-background -mt-10 mb-4 overflow-hidden shadow-sm hover-lift mx-auto">
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah&backgroundColor=b6e3f4" alt="User avatar" className="h-full w-full object-cover" />
              </div>
              
              <div className="text-center mb-6">
                 <h3 className="text-xl font-bold">Sarah Connor</h3>
                 <p className="text-sm text-muted-foreground flex items-center justify-center gap-1 mt-1">
                    <MapPin size={14} /> Los Angeles, CA
                 </p>
                 <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-secondary/10 text-secondary text-xs font-semibold mt-3">
                    <ShieldCheck size={14} /> Pro Member
                 </span>
              </div>

              <div className="space-y-4">
                 <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Mail size={16} /> sarah@example.com
                 </div>
                 <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Calendar size={16} /> Joined March 2026
                 </div>
              </div>

              <button className="w-full mt-6 py-2 border border-border hover:bg-muted text-sm font-semibold rounded-lg transition-colors flex items-center justify-center gap-2">
                 <Edit3 size={16} /> Edit Public Profile
              </button>
           </div>
        </div>

        {/* Right Column - Fitness Bio & Stats */}
        <div className="md:col-span-2 space-y-6">
           {/* Biological Data */}
           <div className="border border-border bg-card rounded-2xl p-6 shadow-sm">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
                 <h3 className="text-lg font-bold flex items-center gap-2">
                    <Activity className="text-primary" size={20} /> Matrix Constraints
                 </h3>
                 <Link 
                   to="/profile"
                   className="px-4 py-1.5 bg-primary/10 text-primary hover:bg-primary/20 text-xs font-semibold rounded-lg transition-colors border border-primary/20"
                 >
                   Recalibrate Bio Data
                 </Link>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                 <BioCard label="Age" value="25" />
                 <BioCard label="Weight" value="68 kg" />
                 <BioCard label="Height" value="170 cm" />
                 <BioCard label="BMI" value="23.5" status="Healthy" />
              </div>
           </div>

           {/* Goals & Preferences */}
           <div className="border border-border bg-card rounded-2xl p-6 shadow-sm">
              <h3 className="text-lg font-bold flex items-center gap-2 mb-6">
                 <Target className="text-accent" size={20} /> Current Recommender Config
              </h3>

              <div className="space-y-4">
                 <div className="flex justify-between items-center py-2 border-b border-border/50">
                    <span className="text-muted-foreground text-sm font-medium">Primary Goal</span>
                    <span className="font-semibold">Muscle Gain</span>
                 </div>
                 <div className="flex justify-between items-center py-2 border-b border-border/50">
                    <span className="text-muted-foreground text-sm font-medium">Experience Level</span>
                    <span className="font-semibold">Intermediate</span>
                 </div>
                 <div className="flex justify-between items-center py-2 border-b border-border/50">
                    <span className="text-muted-foreground text-sm font-medium">Preferred Equipment</span>
                    <span className="font-semibold">Full Gym Access</span>
                 </div>
                 <div className="flex justify-between items-center py-2">
                    <span className="text-muted-foreground text-sm font-medium">Training Frequency</span>
                    <span className="font-semibold">3 Days / Week</span>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}

function BioCard({ label, value, status }: { label: string, value: string, status?: string }) {
   return (
      <div className="bg-muted/30 border border-border rounded-xl p-4 text-center">
         <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold mb-1">{label}</div>
         <div className="text-xl font-bold tracking-tight">{value}</div>
         {status && (
            <div className="text-[10px] font-bold uppercase tracking-wider text-secondary mt-1">{status}</div>
         )}
      </div>
   );
}
