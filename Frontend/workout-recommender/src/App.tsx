import React, { useEffect, useState } from 'react';
import { Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom';
import { 
  Activity, 
  Dumbbell, 
  Flame, 
  Trophy, 
  User, 
  Calendar, 
  CalendarCheck,
  LogOut,
  Sparkles,
  X
} from 'lucide-react';
import { cn } from './lib/utils';
import Dashboard from './pages/Dashboard';
import ProfileSetup from './pages/ProfileSetup';
import MyPlan from './pages/MyPlan';
import Progress from './pages/Progress';
import DailyCheckIn from './pages/DailyCheckIn';
import Login from './pages/Login';
import Register from './pages/Register';
import SettingsPage from './pages/Settings';
import UserAccount from './pages/UserAccount';
import HelpChat from './pages/HelpChat';
import { useAuth } from './contexts/AuthContext';
import { api } from './lib/api';

export default function App() {
  const location = useLocation();
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const isAuthRoute = location.pathname === '/login' || location.pathname === '/register';
  const [streakDays, setStreakDays] = useState<number | null>(null);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    api.analyticsSummary()
      .then((data) => setStreakDays((data as { streak_days?: number }).streak_days ?? null))
      .catch(() => setStreakDays(null));
  }, [isAuthenticated]);

  if (isAuthRoute) {
    if (isAuthenticated) {
      return <Navigate to="/" replace />;
    }

    return (
      <div className="">
         <Routes>
           <Route path="/login" element={<Login />} />
           <Route path="/register" element={<Register />} />
         </Routes>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="h-10 w-10 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const displayName = user?.first_name || user?.username || 'Athlete';
  const avatarSeed = encodeURIComponent(user?.username || user?.email || 'FitGenius');

  return (
    <div className="min-h-screen bg-background text-foreground font-sans selection:bg-primary/30">
      {/* Sidebar Navigation */}
      <aside className="fixed left-0 top-0 h-full w-20 md:w-64 bg-sidebar border-r border-sidebar-border z-50 flex flex-col transition-all duration-300">
        <div className="h-20 flex items-center justify-center md:justify-start md:px-6 border-b border-sidebar-border">
          <div className="bg-primary/10 p-2 rounded-xl text-primary animate-pulse-subtle">
            <Dumbbell className="h-6 w-6" />
          </div>
          <span className="hidden md:block ml-3 font-bold text-lg tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            FitGenius AI
          </span>
        </div>
        
        <nav className="flex-1 py-6 flex flex-col gap-2 px-3">
          <NavItem to="/" icon={<Activity />} label="Dashboard" active={location.pathname === '/'} />
          <NavItem to="/profile" icon={<User />} label="Profile Setup" active={location.pathname === '/profile'} />
          <NavItem to="/check-in" icon={<CalendarCheck />} label="Daily Check-In" active={location.pathname === '/check-in'} />
          <NavItem to="/plan" icon={<Calendar />} label="My Plan" active={location.pathname === '/plan'} />
          <NavItem to="/progress" icon={<Trophy />} label="Progress" active={location.pathname === '/progress'} />
        </nav>
        
        <div className="p-4 border-t border-sidebar-border space-y-2">
          <NavLink to="/settings" className={({isActive}) => `w-full flex items-center justify-center md:justify-start gap-3 p-3 rounded-lg transition-colors ${isActive ? 'bg-sidebar-accent text-primary' : 'text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground'}`}>
            <SettingsIcon />
            <span className="hidden md:block text-sm font-medium">Settings</span>
          </NavLink>
          <button onClick={() => logout()} className="w-full flex items-center justify-center md:justify-start gap-3 p-3 rounded-lg transition-colors text-sidebar-foreground/70 hover:bg-destructive/10 hover:text-destructive">
            <LogOut className="h-5 w-5" />
            <span className="hidden md:block text-sm font-medium">Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="ml-20 md:ml-64 p-6 md:p-10 min-h-screen transition-all duration-300 flex flex-col">
        {/* Universal Header */}
        <header className="mb-8 flex justify-between items-center animate-fade-in-up">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Welcome back, {displayName}!</h1>
            <p className="text-muted-foreground mt-1">Consistency is key. You're doing great.</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 bg-card border border-border px-4 py-2 rounded-full shadow-sm text-sm font-medium">
              <Flame className="h-4 w-4 text-primary animate-pulse-subtle" />
              <span>{streakDays ?? 0} Day Streak</span>
            </div>
            <NavLink to="/account" className="block h-10 w-10 rounded-full bg-gradient-card border-2 border-primary/20 flex items-center justify-center overflow-hidden shadow-sm hover-lift cursor-pointer transition-transform hover:scale-105 active:scale-95">
              <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${avatarSeed}&backgroundColor=b6e3f4`} alt="User avatar" className="h-full w-full object-cover" />
            </NavLink>
          </div>
        </header>

        {/* Dynamic Route Content */}
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile" element={<ProfileSetup />} />
            <Route path="/check-in" element={<DailyCheckIn />} />
            <Route path="/plan" element={<MyPlan />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/account" element={<UserAccount />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </main>

      <div className={cn("fixed bottom-4 z-[110] transition-all duration-300", isHelpOpen ? "pointer-events-none translate-y-4 opacity-0 right-10" : "right-8")}>
        <button
          onClick={() => setIsHelpOpen((value) => !value)}
          className={cn(
            "flex items-center gap-2 p-3 px-5 rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.12)] transition-all duration-300 border backdrop-blur-md active:scale-95",
            isHelpOpen
              ? "bg-primary text-primary-foreground border-primary scale-110 shadow-primary/20"
              : "bg-card/70 text-muted-foreground border-border/50 hover:border-primary/50 hover:text-primary hover:shadow-primary/10 hover:bg-card/90"
          )}
        >
          <Sparkles className={cn("w-5 h-5", isHelpOpen && "animate-pulse")} />
          <span className="text-sm font-bold tracking-tight uppercase">Help</span>
        </button>
      </div>

      <aside
        className={cn(
          "fixed right-0 top-0 bottom-0 z-[100] w-full max-w-[720px] bg-card border-l border-border shadow-2xl transition-all duration-300 ease-out p-4 overflow-hidden",
          isHelpOpen ? "translate-x-0 opacity-100" : "translate-x-full opacity-0 pointer-events-none"
        )}
      >
        <div className="h-full flex flex-col">
          <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <p className="font-semibold text-sm">Help</p>
                <p className="text-xs text-muted-foreground">Profile-aware chat</p>
              </div>
            </div>
            <button onClick={() => setIsHelpOpen(false)} className="p-2 rounded-lg hover:bg-muted transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="flex-1 min-h-0">
            <HelpChat embedded />
          </div>
        </div>
      </aside>
    </div>
  );
}

function NavItem({ to, icon, label, active = false }: { to: string, icon: React.ReactNode, label: string, active?: boolean }) {
  return (
    <NavLink 
      to={to}
      className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative",
        active 
          ? "bg-primary text-primary-foreground font-medium shadow-md shadow-primary/20" 
          : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground"
      )}
    >
      <div className={cn("flex-shrink-0 transition-transform group-hover:scale-110", active && "text-primary-foreground")}>{icon}</div>
      <span className="hidden md:block whitespace-nowrap">{label}</span>
      <span className="md:hidden absolute left-full ml-4 bg-foreground text-background text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
         {label}
      </span>
    </NavLink>
  );
}

function SettingsIcon() {
  return (
    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 15.5A3.5 3.5 0 1 0 12 8a3.5 3.5 0 0 0 0 7.5Z" />
      <path d="M19.4 15a1.8 1.8 0 0 0 .36 1.98l.04.04a2.1 2.1 0 0 1-2.97 2.97l-.04-.04a1.8 1.8 0 0 0-1.98-.36 1.8 1.8 0 0 0-1.09 1.65V21.3a2.1 2.1 0 0 1-4.2 0v-.06a1.8 1.8 0 0 0-1.09-1.65 1.8 1.8 0 0 0-1.98.36l-.04.04a2.1 2.1 0 0 1-2.97-2.97l.04-.04A1.8 1.8 0 0 0 4.6 15a1.8 1.8 0 0 0-1.65-1.09H2.9a2.1 2.1 0 0 1 0-4.2h.06A1.8 1.8 0 0 0 4.6 8a1.8 1.8 0 0 0-.36-1.98l-.04-.04A2.1 2.1 0 1 1 7.17 3l.04.04A1.8 1.8 0 0 0 9.2 3.4 1.8 1.8 0 0 0 10.29 1.75V1.7a2.1 2.1 0 0 1 4.2 0v.06A1.8 1.8 0 0 0 15.58 3.4a1.8 1.8 0 0 0 1.98-.36l.04-.04a2.1 2.1 0 1 1 2.97 2.97l-.04.04A1.8 1.8 0 0 0 19.4 8a1.8 1.8 0 0 0 1.65 1.09h.06a2.1 2.1 0 0 1 0 4.2h-.06A1.8 1.8 0 0 0 19.4 15Z" />
    </svg>
  );
}
