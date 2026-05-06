/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../lib/api';

type Theme = 'light' | 'dark';
export type MeasurementSystem = 'metric' | 'imperial';
type NotificationPermissionState = 'default' | 'granted' | 'denied' | 'unsupported';

export type NotificationSettings = {
  pushEnabled: boolean;
  weeklyEmailEnabled: boolean;
  reminderTime: string;
  lastReminderDate?: string;
};

interface ThemeContextType {
  theme: Theme;
  measurementSystem: MeasurementSystem;
  notificationSettings: NotificationSettings;
  notificationPermission: NotificationPermissionState;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
  setMeasurementSystem: (system: MeasurementSystem) => void;
  setNotificationSettings: (settings: Partial<NotificationSettings>) => Promise<void>;
  sendTestNotification: () => Promise<void>;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);
const notificationDefaults: NotificationSettings = {
  pushEnabled: false,
  weeklyEmailEnabled: true,
  reminderTime: '07:00',
};

function loadNotificationSettings(): NotificationSettings {
  try {
    const raw = localStorage.getItem('notificationSettings');
    return raw ? { ...notificationDefaults, ...JSON.parse(raw) } : notificationDefaults;
  } catch {
    return notificationDefaults;
  }
}

function getNotificationPermission(): NotificationPermissionState {
  if (!('Notification' in window)) return 'unsupported';
  return Notification.permission;
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    const saved = localStorage.getItem('theme');
    return (saved as Theme) || 'dark';
  });
  const [measurementSystem, setMeasurementSystemState] = useState<MeasurementSystem>(() => {
    const saved = localStorage.getItem('measurementSystem');
    return saved === 'imperial' ? 'imperial' : 'metric';
  });
  const [notificationSettings, setNotificationSettingsState] = useState<NotificationSettings>(loadNotificationSettings);
  const [notificationPermission, setNotificationPermission] = useState<NotificationPermissionState>(() => getNotificationPermission());

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);
    api.savePreferences({ theme: newTheme }).catch(() => {});
  };

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
  };

  const setMeasurementSystem = (system: MeasurementSystem) => {
    setMeasurementSystemState(system);
    localStorage.setItem('measurementSystem', system);
    api.savePreferences({ measurement_system: system }).catch(() => {});
  };

  const requestNotificationPermission = async () => {
    if (!('Notification' in window)) {
      setNotificationPermission('unsupported');
      return false;
    }

    if (Notification.permission === 'granted') {
      setNotificationPermission('granted');
      return true;
    }

    const permission = await Notification.requestPermission();
    setNotificationPermission(permission);
    return permission === 'granted';
  };

  const persistNotificationSettings = (settings: NotificationSettings) => {
    setNotificationSettingsState(settings);
    localStorage.setItem('notificationSettings', JSON.stringify(settings));
    api.savePreferences({
      push_enabled: settings.pushEnabled,
      reminder_time: settings.reminderTime,
      weekly_email_enabled: settings.weeklyEmailEnabled,
    }).catch(() => {});
  };

  const setNotificationSettings = async (settings: Partial<NotificationSettings>) => {
    const next = { ...notificationSettings, ...settings };

    if (settings.pushEnabled === true) {
      const allowed = await requestNotificationPermission();
      if (!allowed) {
        persistNotificationSettings({ ...next, pushEnabled: false });
        return;
      }
    }

    persistNotificationSettings(next);
  };

  const sendNotification = (title: string, body: string) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, { body });
      return;
    }

    window.dispatchEvent(new CustomEvent('fitgenius-notification', { detail: { title, body } }));
  };

  const sendTestNotification = async () => {
    const allowed = await requestNotificationPermission();
    if (!allowed) return;
    sendNotification('FitGenius reminder test', 'Daily workout reminders are ready.');
  };

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
  }, [theme]);

  useEffect(() => {
    api.preferences()
      .then((preferences) => {
        setThemeState(preferences.theme);
        localStorage.setItem('theme', preferences.theme);
        setMeasurementSystemState(preferences.measurement_system);
        localStorage.setItem('measurementSystem', preferences.measurement_system);
        const nextNotifications = {
          ...notificationDefaults,
          pushEnabled: preferences.push_enabled,
          reminderTime: preferences.reminder_time,
          weeklyEmailEnabled: preferences.weekly_email_enabled,
        };
        setNotificationSettingsState(nextNotifications);
        localStorage.setItem('notificationSettings', JSON.stringify(nextNotifications));
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const interval = window.setInterval(() => {
      if (!notificationSettings.pushEnabled || notificationPermission !== 'granted') return;

      const now = new Date();
      const today = now.toISOString().slice(0, 10);
      const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

      if (currentTime !== notificationSettings.reminderTime || notificationSettings.lastReminderDate === today) {
        return;
      }

      sendNotification('Time for your FitGenius check-in', 'Log your readiness and update today’s workout plan.');
      persistNotificationSettings({ ...notificationSettings, lastReminderDate: today });
    }, 30000);

    return () => window.clearInterval(interval);
  }, [notificationSettings, notificationPermission]);

  return (
    <ThemeContext.Provider value={{ theme, measurementSystem, notificationSettings, notificationPermission, toggleTheme, setTheme, setMeasurementSystem, setNotificationSettings, sendTestNotification }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
