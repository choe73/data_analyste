/**
 * API Client for DataCollect Pro Cameroun
 */

const API_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000';

export interface Analysis {
  id: number;
  analysis_type: string;
  title: string;
  description?: string;
  result?: string;
  created_at: string;
}

export interface AnalysisCreate {
  analysis_type: string;
  title: string;
  description?: string;
  result?: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  database: string;
  version: string;
}

export interface Dataset {
  id: number;
  name: string;
  description?: string;
  row_count: number;
  created_at: string;
}

export interface CollectionSource {
  id: number;
  name: string;
  type: string;
  status: string;
  last_run?: string;
}

export interface CollectionStatus {
  source_id: number;
  status: string;
  last_run: string;
  next_run?: string;
  records_collected: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Health & Status
  async getHealth(): Promise<HealthResponse> {
    return this.request('/health');
  }

  async getReady(): Promise<{ ready: boolean }> {
    return this.request('/ready');
  }

  // Analyses
  async listAnalyses(
    analysisType?: string,
    skip: number = 0,
    limit: number = 10
  ): Promise<Analysis[]> {
    const params = new URLSearchParams();
    if (analysisType) params.append('analysis_type', analysisType);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());

    return this.request(`/api/v1/analyses?${params}`);
  }

  async getAnalysis(id: number): Promise<Analysis> {
    return this.request(`/api/v1/analyses/${id}`);
  }

  async createAnalysis(data: AnalysisCreate): Promise<Analysis> {
    return this.request('/api/v1/analyses', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async testAnalysis(): Promise<any> {
    return this.request('/api/v1/analysis/test');
  }

  async interpretAnalysis(data: any): Promise<any> {
    return this.request('/api/v1/analysis/interpret', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Datasets
  async listDatasets(domain?: string, source?: string): Promise<Dataset[]> {
    const params = new URLSearchParams()
    if (domain) params.append('domain', domain)
    if (source) params.append('source', source)
    const qs = params.toString()
    return this.request(`/api/v1/datasets${qs ? '?' + qs : ''}`)
  }

  async getDataset(id: number): Promise<Dataset> {
    return this.request(`/api/v1/datasets/${id}`);
  }

  // Data Collection
  async listSources(): Promise<CollectionSource[]> {
    return this.request('/api/v1/collection/sources');
  }

  async triggerCollection(sourceId: number): Promise<any> {
    return this.request(`/api/v1/collection/trigger/${sourceId}`, {
      method: 'POST',
    });
  }

  async triggerAllCollections(): Promise<any> {
    return this.request('/api/v1/collection/trigger-all', {
      method: 'POST',
    });
  }

  async getCollectionStatus(sourceId: number): Promise<CollectionStatus> {
    return this.request(`/api/v1/collection/status/${sourceId}`);
  }
}

export const apiClient = new ApiClient()

// Export convenience functions for common operations
export const checkHealth = () => apiClient.getHealth()
export const listAnalyses = (type?: string, skip?: number, limit?: number) =>
  apiClient.listAnalyses(type, skip, limit)
export const getAnalysis = (id: number) => apiClient.getAnalysis(id)
export const createAnalysis = (data: AnalysisCreate) => apiClient.createAnalysis(data)
export const interpretAnalysis = (data: any) => apiClient.interpretAnalysis(data)
export const getDatasets = (domain?: string, source?: string) =>
  apiClient.listDatasets(domain, source)
export const getDataset = (id: number) => apiClient.getDataset(id)
export const getSources = () => apiClient.listSources()
export const triggerCollection = (sourceId: number) => apiClient.triggerCollection(sourceId)
export const triggerAllCollections = () => apiClient.triggerAllCollections()
export const getCollectionStatus = (sourceId: number) => apiClient.getCollectionStatus(sourceId)

// Analysis functions
export const descriptiveAnalysis = (data: any) => apiClient.request('/api/v1/analysis/descriptive', {
  method: 'POST',
  body: JSON.stringify(data),
})

export const regressionAnalysis = (data: any) => apiClient.request('/api/v1/analysis/regression', {
  method: 'POST',
  body: JSON.stringify(data),
})

export const pcaAnalysis = (data: any) => apiClient.request('/api/v1/analysis/pca', {
  method: 'POST',
  body: JSON.stringify(data),
})

export const classificationAnalysis = (data: any) => apiClient.request('/api/v1/analysis/classification', {
  method: 'POST',
  body: JSON.stringify(data),
})

export const clusteringAnalysis = (data: any) => apiClient.request('/api/v1/analysis/clustering', {
  method: 'POST',
  body: JSON.stringify(data),
})
