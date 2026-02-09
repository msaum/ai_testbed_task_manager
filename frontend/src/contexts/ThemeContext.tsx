import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { getSettings, updateSettings } from '../utils/api';
import type { Settings } from '../types';

interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  saveSettings: (settings: Partial<Settings>) => Promise<void>;
  loading: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<'light' | 'dark'>('light');
  const [loading, setLoading] = useState(true);

  // Load saved theme from backend settings
  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    try {
      const settings = await getSettings();
      setThemeState(settings.theme as 'light' | 'dark');
    } catch (error) {
      // If settings not found, use system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setThemeState(prefersDark ? 'dark' : 'light');
    } finally {
      setLoading(false);
    }
  }

  function setTheme(newTheme: 'light' | 'dark') {
    setThemeState(newTheme);
    applyTheme(newTheme);
  }

  function toggleTheme() {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    saveSettings({ theme: newTheme });
  }

  function applyTheme(newTheme: 'light' | 'dark') {
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }

  async function saveSettings(settings: Partial<Settings>) {
    try {
      await updateSettings(settings);
      if (settings.theme) {
        setThemeState(settings.theme as 'light' | 'dark');
        applyTheme(settings.theme as 'light' | 'dark');
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }

  // Apply initial theme
  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme, saveSettings, loading }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
