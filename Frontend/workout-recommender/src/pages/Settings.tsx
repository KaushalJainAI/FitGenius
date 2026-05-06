import React, { useEffect, useState } from 'react';
import { Bell, CheckCircle, Lock, Shield, Moon, MonitorSmartphone, CreditCard, Sparkles } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { Select } from '../components/Select';
import { api } from '../lib/api';
import type { BillingPlan, SecurityStatus, Subscription } from '../lib/api';

export default function Settings() {
  const [activeTab, setActiveTab] = useState('preferences');
  const { theme, measurementSystem, notificationSettings, notificationPermission, toggleTheme, setMeasurementSystem, setNotificationSettings, sendTestNotification } = useTheme();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [billingPlans, setBillingPlans] = useState<BillingPlan[]>([]);
  const [security, setSecurity] = useState<SecurityStatus | null>(null);
  const [billingLoading, setBillingLoading] = useState(false);
  const [billingActionLoading, setBillingActionLoading] = useState(false);
  const [billingNotice, setBillingNotice] = useState("");

  useEffect(() => {
    if (activeTab !== 'billing' || subscription || billingLoading) return;

    setBillingLoading(true);
    api.subscription()
      .then(setSubscription)
      .catch((err) => setBillingNotice(err instanceof Error ? err.message : 'Unable to load subscription.'))
      .finally(() => setBillingLoading(false));
    api.billingPlans()
      .then((data) => setBillingPlans(data.plans))
      .catch(() => setBillingPlans([]));
  }, [activeTab, subscription, billingLoading]);

  useEffect(() => {
    if (activeTab !== 'security' || security) return;
    api.security()
      .then(setSecurity)
      .catch(() => setSecurity(null));
  }, [activeTab, security]);

  const startProTrial = async () => {
    setBillingActionLoading(true);
    setBillingNotice("");
    try {
      const response = await api.startProTrial();
      setSubscription(response.data);
      setBillingNotice(response.message);
    } catch (err) {
      setBillingNotice(err instanceof Error ? err.message : 'Unable to start Pro trial.');
    } finally {
      setBillingActionLoading(false);
    }
  };

  const cancelSubscription = async () => {
    setBillingActionLoading(true);
    setBillingNotice("");
    try {
      const response = await api.cancelSubscription();
      setSubscription(response.data);
      setBillingNotice(response.message);
    } catch (err) {
      setBillingNotice(err instanceof Error ? err.message : 'Unable to cancel subscription.');
    } finally {
      setBillingActionLoading(false);
    }
  };

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
                  checked={theme === 'dark'}
                  onChange={toggleTheme}
                />
                <hr className="border-border/50" />
                <SelectSetting
                  title="Measurement System"
                  description="Choose between Metric (kg, cm) and Imperial (lbs, in)."
                  options={[
                    { value: 'metric', label: 'Metric (kg, cm)' },
                    { value: 'imperial', label: 'Imperial (lbs, in)' },
                  ]}
                  value={measurementSystem}
                  onChange={(value) => setMeasurementSystem(value === 'imperial' ? 'imperial' : 'metric')}
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
                  description={notificationPermission === 'denied' ? 'Browser permission is blocked. Enable notifications in site settings.' : 'Receive a daily workout reminder while the app is open.'}
                  checked={notificationSettings.pushEnabled}
                  onChange={() => setNotificationSettings({ pushEnabled: !notificationSettings.pushEnabled })}
                />
                <hr className="border-border/50" />
                <TimeSetting
                  title="Daily Reminder Time"
                  description="Choose when FitGenius should remind you to check in."
                  value={notificationSettings.reminderTime}
                  onChange={(value) => setNotificationSettings({ reminderTime: value })}
                />
                <hr className="border-border/50" />
                <ToggleSetting
                  icon={<Bell />}
                  title="Weekly Summary Email"
                  description="Receive a weekly breakdown of your progress and plan adjustments."
                  checked={notificationSettings.weeklyEmailEnabled}
                  onChange={() => setNotificationSettings({ weeklyEmailEnabled: !notificationSettings.weeklyEmailEnabled })}
                />
                <button type="button" onClick={sendTestNotification} className="rounded-lg border border-border bg-background px-4 py-2 text-sm font-semibold hover:bg-muted">
                  Send Test Notification
                </button>
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
                    <p className="text-sm text-muted-foreground mt-1">Last changed {security?.password_changed_at ? formatDate(security.password_changed_at) : 'not available'}</p>
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
                  checked={security?.two_factor_enabled ?? false}
                  onChange={async () => {
                    const next = security?.two_factor_enabled ? await api.disableTwoFactor() : await api.enableTwoFactor();
                    setSecurity((current) => current ? { ...current, two_factor_enabled: next.two_factor_enabled } : current);
                  }}
                />
                <hr className="border-border/50" />
                <div>
                   <h4 className="font-medium text-destructive">Danger Zone</h4>
                   <p className="text-sm text-muted-foreground mt-1 mb-3">Permanently delete your account and all workout data.</p>
                   <button disabled={!security?.can_delete_account} className="px-4 py-2 bg-destructive/10 text-destructive hover:bg-destructive/20 text-sm font-medium rounded-lg transition-colors border border-destructive/20 disabled:opacity-50">
                     Delete Account
                   </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'billing' && (
            <div className="space-y-6 animate-fade-in-up">
              <h3 className="text-lg font-semibold border-b border-border pb-4">Billing & Subscription</h3>

              {billingLoading && <div className="rounded-lg border border-border bg-background p-4 text-sm text-muted-foreground">Loading subscription...</div>}
              {billingNotice && <div className="rounded-lg border border-border bg-background p-4 text-sm text-muted-foreground whitespace-pre-line">{billingNotice}</div>}

              {subscription && (
                <>
                  <div className="bg-primary/5 border border-primary/20 rounded-xl p-5">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <h4 className="font-bold text-primary flex flex-wrap items-center gap-2">
                          {subscription.plan_label} Tier
                          <span className="text-xs bg-primary/20 px-2 py-0.5 rounded-full capitalize">{subscription.status}</span>
                          {subscription.is_trial_active && <span className="text-xs bg-secondary/20 text-secondary px-2 py-0.5 rounded-full">Free Trial</span>}
                        </h4>
                        <p className="text-sm text-muted-foreground mt-2">
                          {subscription.plan === 'pro'
                            ? `Trial ends ${formatDate(subscription.trial_ends_at)}. No payment gateway is connected.`
                            : 'You are on the free plan. Upgrade to Pro under a free trial anytime.'}
                        </p>
                      </div>
                      <span className="font-semibold text-lg">$0<span className="text-sm font-normal text-muted-foreground">/trial</span></span>
                    </div>

                    <div className="mt-5 grid gap-2">
                      {subscription.features.map((feature) => (
                        <div key={feature} className="flex items-center gap-2 text-sm text-muted-foreground">
                          <CheckCircle className="h-4 w-4 text-secondary" />
                          {feature}
                        </div>
                      ))}
                    </div>

                    <div className="mt-6 flex flex-wrap gap-3">
                      {subscription.plan === 'pro' ? (
                        <button disabled={billingActionLoading} onClick={cancelSubscription} className="px-4 py-2 border border-border hover:bg-muted text-sm font-medium rounded-lg transition-colors disabled:opacity-70">
                          Return to Free
                        </button>
                      ) : (
                        <button disabled={billingActionLoading} onClick={startProTrial} className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-lg transition-colors hover:bg-primary/90 disabled:opacity-70">
                          <Sparkles className="h-4 w-4" /> Start Pro Free Trial
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {(billingPlans.length ? billingPlans : [
                      { id: 'free', label: 'Free', price: 0, billing_cycle: 'free', features: ['Basic profile', 'Daily check-ins', 'Starter recommendations'] },
                      { id: 'pro', label: 'Pro Trial', price: 0, billing_cycle: 'free_trial', features: ['Adaptive AI plans', 'Progress analytics', 'Manual free-trial validation'] },
                    ]).map((plan) => (
                      <PlanCard key={plan.id} title={plan.label} price={`$${plan.price}`} active={subscription.plan === plan.id} features={plan.features} />
                    ))}
                  </div>
                </>
              )}
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

interface ToggleSettingProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  defaultChecked?: boolean;
  checked?: boolean;
  onChange?: () => void;
}

function ToggleSetting({ icon, title, description, defaultChecked, checked: controlledChecked, onChange }: ToggleSettingProps) {
  const [internalChecked, setInternalChecked] = useState(defaultChecked ?? false);
  const isControlled = controlledChecked !== undefined;
  const isChecked = isControlled ? controlledChecked : internalChecked;

  const handleToggle = () => {
    if (onChange) {
      onChange();
    } else {
      setInternalChecked(!internalChecked);
    }
  };

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
        onClick={handleToggle}
        className={`w-11 h-6 rounded-full transition-all duration-300 relative flex-shrink-0 focus:outline-none focus:ring-2 focus:ring-primary/40 ${isChecked ? 'bg-primary shadow-[0_0_10px_hsl(var(--primary)/0.3)]' : 'bg-muted border border-border'}`}
      >
         <div className={`w-4 h-4 bg-white rounded-full absolute top-1/2 -translate-y-1/2 shadow-sm transition-all duration-300 ${isChecked ? 'left-6' : 'left-1'}`}></div>
      </button>
    </div>
  );
}

function SelectSetting({ title, description, options, value, onChange }: { title: string, description: string, options: Array<{ value: string; label: string }>; value: string; onChange: (value: string) => void }) {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
         <h4 className="font-medium text-foreground">{title}</h4>
         <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
      <div className="w-full sm:w-auto min-w-[220px]">
        <Select
          options={options}
          value={value}
          onChange={onChange}
        />
      </div>
    </div>
  );
}

function TimeSetting({ title, description, value, onChange }: { title: string; description: string; value: string; onChange: (value: string) => void }) {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h4 className="font-medium text-foreground">{title}</h4>
        <p className="text-sm text-muted-foreground mt-1">{description}</p>
      </div>
      <input
        type="time"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full sm:w-52 rounded-xl border-2 border-border bg-background px-4 py-2.5 text-sm font-bold text-foreground outline-none transition-all hover:bg-muted/30 focus:border-primary/50 focus:ring-4 focus:ring-primary/10"
      />
    </div>
  );
}

function PlanCard({ title, price, active, features }: { title: string; price: string; active: boolean; features: string[] }) {
  return (
    <div className={`rounded-xl border p-5 ${active ? 'border-primary/40 bg-primary/5' : 'border-border bg-background'}`}>
      <div className="flex items-center justify-between gap-3">
        <h4 className="font-bold">{title}</h4>
        {active && <span className="rounded-full bg-secondary/15 px-2 py-0.5 text-xs font-semibold text-secondary">Current</span>}
      </div>
      <p className="mt-2 text-2xl font-bold">{price}</p>
      <div className="mt-4 space-y-2">
        {features.map((feature) => (
          <p key={feature} className="text-sm text-muted-foreground">{feature}</p>
        ))}
      </div>
    </div>
  );
}

function formatDate(value: string | null) {
  if (!value) return 'after the trial period';
  return new Date(value).toLocaleDateString();
}
