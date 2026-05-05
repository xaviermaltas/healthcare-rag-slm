// API Service for Healthcare RAG System

import type { 
  DischargeSummaryRequest, 
  ReferralRequest, 
  ClinicalSummaryRequest,
  GenerationResult 
} from '../types';
import { logger } from './logger';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private async request(
    endpoint: string,
    method: string = 'GET',
    body?: any
  ): Promise<GenerationResult> {
    const startTime = Date.now();
    
    logger.request(method, endpoint, body);
    
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
      });

      const data = await response.json();
      const generationTime = (Date.now() - startTime) / 1000;

      logger.response(method, endpoint, response.status, Date.now() - startTime);

      if (!response.ok) {
        logger.error(`API Error: ${response.status}`, data);
        let errorMsg = 'Error en la petició';
        if (Array.isArray(data.detail)) {
          // Pydantic validation errors
          errorMsg = data.detail.map((e: any) => 
            `${e.loc?.join('.')}: ${e.msg}`
          ).join('\n');
        } else if (typeof data.detail === 'string') {
          errorMsg = data.detail;
        }
        return {
          success: false,
          error: errorMsg,
          generationTime,
        };
      }

      return {
        success: true,
        data,
        generationTime,
      };
    } catch (error) {
      logger.error(`Request failed: ${endpoint}`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error desconegut',
        generationTime: (Date.now() - startTime) / 1000,
      };
    }
  }

  async generateDischargeSummary(request: DischargeSummaryRequest): Promise<GenerationResult> {
    return this.request('/generate/discharge-summary', 'POST', request);
  }

  async generateReferral(request: ReferralRequest): Promise<GenerationResult> {
    return this.request('/generate/referral', 'POST', request);
  }

  async generateClinicalSummary(request: ClinicalSummaryRequest): Promise<GenerationResult> {
    return this.request('/generate/clinical-summary', 'POST', request);
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const apiService = new ApiService();
