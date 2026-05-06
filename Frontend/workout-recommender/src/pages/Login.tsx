import React, { useState } from 'react';
import { Dumbbell, ArrowRight, Mail, Lock } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-background">
      {/* Background decorations */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/20 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-accent/20 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-md bg-card border border-border shadow-2xl rounded-3xl p-8 relative z-10 animate-content-reveal">
        <div className="flex flex-col items-center mb-8">
          <div className="h-14 w-14 bg-primary/10 rounded-2xl flex items-center justify-center text-primary mb-4 shadow-inner">
            <Dumbbell size={32} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Welcome Back</h1>
          <p className="text-muted-foreground text-sm mt-2 text-center">
            Sign in to access your AI-powered workout plan.
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <input 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                type="email" 
                placeholder="sarah@example.com" 
                required
                className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium" 
              />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Password</label>
              <a href="#" className="text-xs font-medium text-primary hover:text-primary/80 transition-colors">Forgot Password?</a>
            </div>
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

          {error && <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive-foreground whitespace-pre-line">{error}</div>}

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full relative overflow-hidden rounded-xl bg-gradient-hero hover:opacity-90 text-white font-semibold py-3.5 shadow-elegant hover-glow transition-all disabled:opacity-80 flex items-center justify-center gap-2 mt-4"
          >
            {isLoading ? (
               <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
               <>
                 Sign In <ArrowRight size={18} />
               </>
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-sm text-muted-foreground">
            Don't have an account?{' '}
            <Link to="/register" className="font-semibold text-foreground hover:text-primary transition-colors">
              Create one now
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
