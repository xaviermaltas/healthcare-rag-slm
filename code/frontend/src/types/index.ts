// Types for the Healthcare RAG System

export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: string;
  specialty: string;
  condition: string;
  admissionReason: string;
  medications: string[];
  history: string[];
}

export interface UseCaseType {
  id: 'discharge' | 'referral' | 'clinical-summary';
  name: string;
  description: string;
  icon: string;
  endpoint: string;
}

export interface GenerationResult {
  success: boolean;
  data?: any;
  error?: string;
  generationTime?: number;
}

export interface DischargeSummaryRequest {
  patient_context: string;
  admission_reason: string;
  hospital_course: string;
  discharge_condition: string;
  medications: string[];
  follow_up_instructions: string;
  language?: string;
}

export interface ReferralRequest {
  patient_context: string;
  referral_reason: string;
  relevant_history: string[];
  examinations: string[];
  current_medications: string[];
  target_specialty?: string;
  urgency_level?: string;
  language?: string;
}

export interface ClinicalSummaryRequest {
  patient_context: string;
  current_symptoms: string[];
  medications: string[];
  specialty?: string;
  language?: string;
}
