/**
 * Type definitions for DataCollect Pro Cameroun
 */

export interface Dataset {
  id: number;
  name: string;
  description?: string;
  row_count: number;
  created_at: string;
  source?: string;
  domain?: string;
  columns?: string[];
  last_updated?: string;
}

export interface DataSource {
  id: number;
  name: string;
  type: string;
  status: string;
  last_run?: string;
  sources?: any[];
}

export interface Analysis {
  id: number;
  analysis_type: string;
  title: string;
  description?: string;
  result?: string;
  created_at: string;
}

export interface DescriptiveRequest {
  dataset_id: number;
}

export interface RegressionRequest {
  dataset_id: number;
  target_column: string;
  feature_columns: string[];
}

export interface PCARequest {
  dataset_id: number;
  n_components: number;
}

export interface ClassificationRequest {
  dataset_id: number;
  target_column: string;
  feature_columns: string[];
}

export interface ClusteringRequest {
  dataset_id: number;
  n_clusters: number;
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
