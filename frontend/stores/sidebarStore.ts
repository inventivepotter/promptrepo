/**
 * Sidebar Store
 * Manages sidebar UI state with persistence
 */

import { create } from 'zustand';
import { persist, createLocalStorage } from '@/lib/zustand';
import { ConfigService } from '@/services/config/configService';

interface SidebarState {
  isCollapsed: boolean;
  hostingType: string;
  hasInitialized: boolean;
  setCollapsed: (collapsed: boolean) => void;
  toggleCollapsed: () => void;
  setHostingType: (type: string) => void;
  initializeHostingType: () => Promise<void>;
}

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set, get) => ({
      // State
      isCollapsed: false,
      hostingType: 'individual',
      hasInitialized: false,
      
      // Actions
      setCollapsed: (collapsed) => set({ isCollapsed: collapsed }),
      toggleCollapsed: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      setHostingType: (type) => set({ hostingType: type }),
      
      // Initialize hosting type from server
      initializeHostingType: async () => {
        // Only initialize once
        if (get().hasInitialized) return;
        
        try {
          const type = await ConfigService.getHostingType();
          set({ hostingType: type, hasInitialized: true });
        } catch (error) {
          console.warn('Failed to load hosting type:', error);
          set({ hostingType: 'individual', hasInitialized: true });
        }
      },
    }),
    {
      ...createLocalStorage('sidebar-store'),
      // Only persist UI preferences
      partialize: (state) => ({
        isCollapsed: state.isCollapsed,
        // Don't persist hostingType or hasInitialized as they should be fetched from server
      }),
      // Initialize on store hydration
      onRehydrateStorage: () => (state) => {
        // Auto-initialize hosting type when store is ready
        state?.initializeHostingType();
      },
    }
  )
);

// Export hooks for selective subscriptions
export const useSidebarCollapsed = () => useSidebarStore((state) => state.isCollapsed);
export const useHostingType = () => {
  const hostingType = useSidebarStore((state) => state.hostingType);
  const initializeHostingType = useSidebarStore((state) => state.initializeHostingType);
  
  // Auto-initialize if not done yet
  initializeHostingType();
  
  return hostingType;
};
export const useSidebarActions = () => {
  const { setCollapsed, toggleCollapsed, setHostingType } = useSidebarStore();
  return { setCollapsed, toggleCollapsed, setHostingType };
};