/**
 * Type definitions for DataCollect Pro Cameroun
 */

export interface Dataset {
  id: number;
  name: string;
  description?: string;
  row_count: number;
  created_at: string;
}

export interface DataSource {
  id: number;
  name: string;
  type: string;
  status: string;
  last_run?: string;
}

export interface Analysis {
  id: number;
  analysis_type: string;
  title: string;
  description?: string;
  result?: string;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  database: string;
  version: string;
}
