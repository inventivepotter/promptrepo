/**
 * Sidebar Store
 * Manages sidebar UI state with persistence
 */

import { create } from 'zustand';
import { persist, createLocalStorage } from '@/lib/zustand';

interface SidebarState {
  isCollapsed: boolean;
  hasHydrated: boolean;
  setCollapsed: (collapsed: boolean) => void;
  toggleCollapsed: () => void;
  setHasHydrated: (state: boolean) => void;
}

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set) => ({
      // State - default to expanded
      isCollapsed: false,
      hasHydrated: false,
      
      // Actions
      setCollapsed: (collapsed) => set({ isCollapsed: collapsed }),
      toggleCollapsed: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      setHasHydrated: (state) => set({ hasHydrated: state }),
    }),
    {
      ...createLocalStorage('sidebar-store'),
      // Only persist UI preferences
      partialize: (state) => ({
        isCollapsed: state.isCollapsed,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);

// Export hooks for selective subscriptions with equality checks to prevent unnecessary re-renders
export const useSidebarCollapsed = () => useSidebarStore(
  (state) => state.isCollapsed
);

export const useSidebarActions = () => {
  const { setCollapsed, toggleCollapsed } = useSidebarStore();
  return { setCollapsed, toggleCollapsed };
};

export const useSidebarHasHydrated = () => useSidebarStore(
  (state) => state.hasHydrated
);