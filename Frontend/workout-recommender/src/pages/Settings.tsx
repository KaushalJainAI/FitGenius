import React, { useState } from 'react';
import { Bell, Lock, Shield, Moon, MonitorSmartphone, Volume2, CreditCard } from 'lucide-react';

export default function Settings() {
  const [activeTab, setActiveTab] = useState('preferences');

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-content-reveal">
      <div className="mb-8">
        <h2 className="text-2xl font-bold">Settings & Preferences</h2>
        <p className="text-muted-foreground mt-1">Manage your account settings, display preferences, and notifications.</p>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Settings Sidebar */}
        <div className="md:w-64 shrink-0 space-y-1">
          <TabButton 
            active={activeTab === 'preferences'} 
            onClick={() => setActiveTab('preferences')} 
            icon={<MonitorSmartphone size={18} />} 
            label="App Preferences" 
          />
          <TabButton 
            active={activeTab === 'notifications'} 
            onClick={() => setActiveTab('notifications')} 
            icon={<Bell size={18} />} 
            label="Notifications" 
          />
          <TabButton 
            active={activeTab === 'security'} 
            onClick={() => setActiveTab('security')} 
            icon={<Shield size={18} />} 
            label="Security & Privacy" 
          />
          <TabButton 
            active={activeTab === 'billing'} 
            onClick={() => setActiveTab('billing')} 
            icon={<CreditCard size={18} />} 
            label="Billing & Subscription" 
          />
        </div>

        {/* Settings Content */}
        <div className="flex-1 space-y-6 bg-card border border-border rounded-2xl p-6 md:p-8 shadow-sm">
          {activeTab === 'preferences' && (
            <div className="space-y-6 animate-fade-in-up">
              <h3 className="text-lg font-semibold border-b border-border pb-4">App Preferences</h3>
              
              <div className="space-y-5">
                <ToggleSetting 
                  icon={<Moon />} 
                  title="Dark Mode" 
                  description="Toggle dark mode theme for the interface." 
                  defaultChecked={true} 
                />
                <hr className="border-border/50" />
                <SelectSetting 
                  title="Measurement System" 
                  description="Choose between Metric (kg, cm) and Imperial (lbs, in)."
                  options={['Metric (kg, cm)', 'Imperial (lbs, in)']}
                />
                <hr className="border-border/50" />
                <ToggleSetting 
                  icon={<Volume2 />} 
                  title="Workout Sounds" 
                  description="Play sounds when rests begin and finish." 
                  defaultChecked={true} 
                />
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-6 animate-fade-in-up">
              <h3 className="text-lg font-semibold border-b border-border pb-4">Notification Preferences</h3>
              
              <div className="space-y-5">
                <ToggleSetting 
                  icon={<Bell />} 
                  title="Push Notifications" 
                  description="Receive push notifications for workout reminders." 
                  defaultChecked={true} 
                />
                <hr className="border-border/50" />
                <ToggleSetting 
                  icon={<Bell />} 
                  title="Weekly Summary Email" 
                  description="Receive a weekly breakdown of your progress and plan adjustments." 
                  defaultChecked={true} 
                />
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6 animate-fade-in-up">
              <h3 className="text-lg font-semibold border-b border-border pb-4">Security & Privacy</h3>
              
              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Password</h4>
                    <p className="text-sm text-muted-foreground mt-1">Last changed 3 months ago</p>
                  </div>
                  <button className="px-4 py-2 border border-border hover:bg-muted text-sm font-medium rounded-lg transition-colors">
                    Update
                  </button>
                </div>
                <hr className="border-border/50" />
                <ToggleSetting 
                  icon={<Lock />} 
                  title="Two-Factor Authentication" 
                  description="Add an extra layer of security to your account." 
                  defaultChecked={false} 
                />
                <hr className="border-border/50" />
                <div>
                   <h4 className="font-medium text-destructive">Danger Zone</h4>
                   <p className="text-sm text-muted-foreground mt-1 mb-3">Permanently delete your account and all workout data.</p>
                   <button className="px-4 py-2 bg-destructive/10 text-destructive hover:bg-destructive/20 text-sm font-medium rounded-lg transition-colors border border-destructive/20">
                     Delete Account
                   </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'billing' && (
            <div className="space-y-6 animate-fade-in-up">
              <h3 className="text-lg font-semibold border-b border-border pb-4">Billing & Subscription</h3>
              
              <div className="bg-primary/5 border border-primary/20 rounded-xl p-5">
                <div className="flex justify-between items-center mb-4">
                   <h4 className="font-bold text-primary">Pro Tier <span className="text-xs ml-2 bg-primary/20 px-2 py-0.5 rounded-full">Active</span></h4>
                   <span className="font-semibold text-lg">$9.99<span className="text-sm font-normal text-muted-foreground">/mo</span></span>
                </div>
                <p className="text-sm text-muted-foreground mb-4">Your next billing date is April 15, 2026.</p>
                <div className="flex gap-3">
                   <button className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg transition-colors hover:bg-primary/90">
                     Manage Plan
                   </button>
                   <button className="px-4 py-2 border border-border hover:bg-muted text-sm font-medium rounded-lg transition-colors">
                     View Invoices
                   </button>
                </div>
              </div>
            </div>
          )}

          <div className="pt-6 mt-6 border-t border-border flex justify-end">
             <button className="px-6 py-2.5 bg-primary text-primary-foreground text-sm font-medium rounded-xl transition-all shadow-sm hover:opacity-90 active:scale-[0.98]">
               Save Changes
             </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }: { active: boolean, onClick: () => void, icon: React.ReactNode, label: string }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all text-left ${
        active 
          ? 'bg-secondary/10 text-secondary border border-secondary/20 shadow-sm' 
          : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground border border-transparent'
      }`}
    >
      <div className={`${active ? 'text-secondary' : 'text-muted-foreground'}`}>{icon}</div>
      {label}
    </button>
  );
}

function ToggleSetting({ icon, title, description, defaultChecked }: { icon: React.ReactNode, title: string, description: string, defaultChecked: boolean }) {
  const [checked, setChecked] = useState(defaultChecked);
  return (
    <div className="flex items-start sm:items-center justify-between gap-4">
      <div className="flex gap-3 items-start sm:items-center">
         <div className="w-10 h-10 rounded-lg bg-muted/50 flex flex-shrink-0 items-center justify-center text-muted-foreground border border-border">
            {icon}
         </div>
         <div>
            <h4 className="font-medium text-foreground">{title}</h4>
            <p className="text-sm text-muted-foreground">{description}</p>
         </div>
      </div>
      <button 
        onClick={() => setChecked(!checked)}
        className={`w-11 h-6 rounded-full transition-colors relative flex-shrink-0 ${checked ? 'bg-primary' : 'bg-muted border border-border'}`}
      >
         <div className={`w-4 h-4 bg-white rounded-full absolute top-1/2 -translate-y-1/2 transition-all ${checked ? 'left-6' : 'left-1'}`}></div>
      </button>
    </div>
  );
}

function SelectSetting({ title, description, options }: { title: string, description: string, options: string[] }) {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
         <h4 className="font-medium text-foreground">{title}</h4>
         <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
      <select className="w-full sm:w-auto bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all font-medium appearance-none">
        {options.map((opt, i) => (
           <option key={i}>{opt}</option>
        ))}
      </select>
    </div>
  );
}
