import { writable, derived } from 'svelte/store';
import type { User } from '$lib/types';
import { browser } from '$app/environment';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    user: null,
    token: null,
    loading: true
  });
  
  // Initialize immediately if in browser
  if (browser) {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        set({ user, token, loading: false });
      } catch {
        set({ user: null, token: null, loading: false });
      }
    } else {
      set({ user: null, token: null, loading: false });
    }
  }

  return {
    subscribe,
    
    init: () => {
      if (browser) {
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        
        if (token && userStr) {
          try {
            const user = JSON.parse(userStr);
            update(state => ({ ...state, user, token, loading: false }));
          } catch {
            update(state => ({ ...state, loading: false }));
          }
        } else {
          update(state => ({ ...state, loading: false }));
        }
      }
    },
    
    login: (user: User, token: string) => {
      if (browser) {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
      }
      set({ user, token, loading: false });
    },
    
    logout: () => {
      if (browser) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
      set({ user: null, token: null, loading: false });
    },
    
    updateUser: (user: User) => {
      if (browser) {
        localStorage.setItem('user', JSON.stringify(user));
      }
      update(state => ({ ...state, user }));
    }
  };
}

export const auth = createAuthStore();
export const isAuthenticated = derived(auth, $auth => !!$auth.token);
export const currentUser = derived(auth, $auth => $auth.user);
export const isAdmin = derived(auth, $auth => $auth.user?.role === 'admin');
