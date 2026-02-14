import { create } from 'zustand';

type AppState = {
  theme: 'light' | 'dark';
  sharedCount: number;
  toggleTheme: () => void;
  incShared: () => void;
  decShared: () => void;
};

export const useAppStore = create<AppState>((set) => ({
  theme: 'dark',
  sharedCount: 0,
  toggleTheme: () =>
    set((state) => ({
      theme: state.theme === 'light' ? 'dark' : 'light',
    })),
  incShared: () => set((state) => ({ sharedCount: state.sharedCount + 1 })),
  decShared: () => set((state) => ({ sharedCount: state.sharedCount - 1 })),
}));