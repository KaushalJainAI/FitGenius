import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, tokenStore } from "../lib/api";

type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

type AuthContextValue = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (payload: Record<string, unknown>) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = async () => {
    const current = await api.me() as User;
    setUser(current);
  };

  useEffect(() => {
    if (!tokenStore.access) {
      setIsLoading(false);
      return;
    }

    refreshUser()
      .catch(() => {
        tokenStore.clear();
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (username: string, password: string) => {
    const data = await api.login(username, password);
    tokenStore.set(data.access, data.refresh);
    await refreshUser();
  };

  const register = async (payload: Record<string, unknown>) => {
    await api.register(payload);
  };

  const logout = async () => {
    try {
      await api.logout();
    } finally {
      tokenStore.clear();
      setUser(null);
    }
  };

  const value = useMemo(() => ({
    user,
    isAuthenticated: Boolean(user),
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  }), [user, isLoading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
