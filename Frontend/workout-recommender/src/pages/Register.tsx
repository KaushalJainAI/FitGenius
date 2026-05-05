import React, { useState } from 'react';
import { Dumbbell, ArrowRight, User, Mail, Lock, Activity } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export default function Register() {
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  const handleNext = (e: React.MouseEvent) => {
    e.preventDefault();
    setStep(2);
  };

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API call for registration & plan generation
    setTimeout(() => {
      setIsLoading(false);
      navigate('/');
    }, 1500);
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
                        type="text" 
                        placeholder="Sarah Connor" 
                        required
                        className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" 
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Email Address</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                      <input 
                        type="email" 
                        placeholder="sarah@example.com" 
                        required
                        className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" 
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                      <input 
                        type="password" 
                        placeholder="••••••••" 
                        required
                        className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" 
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
                      <input type="number" defaultValue={25} required className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Weight</label>
                      <div className="relative">
                        <input type="number" defaultValue={68} required className="w-full bg-background border border-border rounded-lg pl-3 pr-8 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">KG</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Height</label>
                      <div className="relative">
                        <input type="number" defaultValue={170} required className="w-full bg-background border border-border rounded-lg pl-3 pr-9 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">CM</span>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Primary Goal</label>
                      <select required className="w-full bg-background border border-border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium appearance-none">
                        <option>Muscle Gain</option>
                        <option>Weight Loss</option>
                        <option>Endurance</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Prior Experience</label>
                      <select required className="w-full bg-background border border-border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium appearance-none">
                        <option>Advanced</option>
                        <option selected>Intermediate</option>
                        <option>Beginner</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex gap-4 pt-4 mt-auto border-t border-border/50">
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
