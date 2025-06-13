import { api } from './client';

export interface DashboardStats {
  totalServices: number;
  activeServices: number;
  totalUsers: number;
  activeUsers: number;
  apiKeys: number;
  searchesToday: number;
  avgResponseTime: number;
  systemHealth: string;
}

export interface AnalyticsData {
  users: {
    total: number;
    active: number;
    adminCount: number;
    recentLogins: number;
  };
  apiKeys: {
    total: number;
    active: number;
    totalRequests: number;
    requestsToday: number;
  };
  services: {
    total: number;
    active: number;
    deprecated: number;
    byType: Record<string, number>;
  };
  search: {
    totalQueries: number;
    queriesThisWeek: number;
    avgResponseTime: number;
    topQueries: Array<{ query: string; count: number }>;
  };
  system: {
    uptime: string;
    dbConnections: number;
    memoryUsage: number;
    cpuUsage: number;
  };
}

export const analyticsApi = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    return api.get('/analytics/dashboard');
  },
  
  getAnalytics: async (): Promise<AnalyticsData> => {
    return api.get('/analytics/');
  }
};
