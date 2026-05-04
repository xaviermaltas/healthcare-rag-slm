import { useState } from 'react';
import { Activity, AlertCircle, Loader2 } from 'lucide-react';
import { PatientCard } from './components/PatientCard';
import { ResultModal } from './components/ResultModal';
import { EXAMPLE_PATIENTS } from './data/patients';
import { apiService } from './services/api';
import type { GenerationResult } from './types';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [currentUseCase, setCurrentUseCase] = useState('');
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Check API health on mount
  useState(() => {
    apiService.healthCheck().then((isOnline) => {
      setApiStatus(isOnline ? 'online' : 'offline');
    });
  });

  const handleGenerate = async (
    patientId: string,
    useCase: 'discharge' | 'referral' | 'clinical-summary'
  ) => {
    console.log('🎯 handleGenerate called:', { patientId, useCase });
    
    const patient = EXAMPLE_PATIENTS.find((p) => p.id === patientId);
    if (!patient) {
      console.error('❌ Patient not found:', patientId);
      return;
    }

    console.log('👤 Patient found:', patient.name);
    setIsLoading(true);
    setCurrentUseCase(useCase);

    try {
      let response: GenerationResult;
      console.log(`📝 Generating ${useCase}...`);

      if (useCase === 'discharge') {
        response = await apiService.generateDischargeSummary({
          patient_context: `${patient.gender} de ${patient.age} anys`,
          admission_reason: patient.admissionReason,
          hospital_course: `Pacient ingressat per ${patient.condition}. ${patient.history.join('. ')}.`,
          discharge_condition: 'Estable, milloria clínica',
          medications: patient.medications,
          follow_up_instructions: `Control per ${patient.specialty} en 1 setmana`,
          language: 'ca',
        });
      } else if (useCase === 'referral') {
        response = await apiService.generateReferral({
          patient_context: `${patient.gender} de ${patient.age} anys`,
          referral_reason: patient.admissionReason,
          relevant_history: patient.history,
          examinations: [],
          current_medications: patient.medications,
          target_specialty: patient.specialty,
          urgency_level: 'preferent',
          language: 'ca',
        });
      } else {
        // Clinical Summary
        const clinicalSummaryRequest = {
          patient_context: `${patient.gender} de ${patient.age} anys. Antecedents: ${patient.history.join(', ')}`,
          current_symptoms: [patient.condition, patient.admissionReason],
          medications: patient.medications,
          specialty: patient.specialty,
          language: 'ca',
        };
        console.log('📋 Clinical Summary Request:', clinicalSummaryRequest);
        response = await apiService.generateClinicalSummary(clinicalSummaryRequest);
      }

      setResult(response);
      setShowModal(true);
    } catch (error) {
      setResult({
        success: false,
        error: error instanceof Error ? error.message : 'Error desconegut',
      });
      setShowModal(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
                <Activity className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Healthcare RAG System
                </h1>
                <p className="text-sm text-gray-500">
                  Generació automàtica de documents clínics amb IA
                </p>
              </div>
            </div>
            
            {/* API Status */}
            <div className="flex items-center gap-2">
              {apiStatus === 'checking' && (
                <span className="text-sm text-gray-500">Comprovant API...</span>
              )}
              {apiStatus === 'online' && (
                <>
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-green-600 font-medium">API Online</span>
                </>
              )}
              {apiStatus === 'offline' && (
                <>
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  <span className="text-sm text-red-600 font-medium">API Offline</span>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Info Banner */}
        <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-blue-900 mb-1">
                Prova de Concepte - Demo Funcional
              </h3>
              <p className="text-sm text-blue-700">
                Selecciona un pacient i clica en el tipus de document que vols generar.
                El sistema utilitzarà el RAG per generar informes mèdics amb codificació automàtica.
              </p>
            </div>
          </div>
        </div>

        {/* Loading Overlay */}
        {isLoading && (
          <div className="mb-8 bg-primary-50 border border-primary-200 rounded-lg p-6">
            <div className="flex items-center gap-3">
              <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />
              <div>
                <p className="text-sm font-medium text-primary-900">
                  Generant document...
                </p>
                <p className="text-xs text-primary-700">
                  Això pot trigar entre 30-60 segons
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Patients Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {EXAMPLE_PATIENTS.map((patient) => (
            <PatientCard
              key={patient.id}
              patient={patient}
              onGenerateClick={handleGenerate}
              isLoading={isLoading}
            />
          ))}
        </div>
      </main>

      {/* Result Modal */}
      <ResultModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        result={result}
        useCase={currentUseCase}
      />
    </div>
  );
}

export default App;
