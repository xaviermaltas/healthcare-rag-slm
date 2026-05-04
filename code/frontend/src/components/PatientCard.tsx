import { User, Activity, Pill, FileText, Send, ClipboardList } from 'lucide-react';
import type { Patient } from '../types';

interface PatientCardProps {
  patient: Patient;
  onGenerateClick: (patientId: string, useCase: 'discharge' | 'referral' | 'clinical-summary') => void;
  isLoading?: boolean;
}

export function PatientCard({ patient, onGenerateClick, isLoading }: PatientCardProps) {
  return (
    <div className="card hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
            <User className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{patient.name}</h3>
            <p className="text-sm text-gray-500">
              {patient.age} anys · {patient.gender}
            </p>
          </div>
        </div>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
          {patient.specialty}
        </span>
      </div>

      {/* Condition */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-2 mb-1">
          <Activity className="w-4 h-4 text-gray-600" />
          <span className="text-xs font-medium text-gray-600">Condició</span>
        </div>
        <p className="text-sm font-medium text-gray-900">{patient.condition}</p>
      </div>

      {/* Admission Reason */}
      <div className="mb-4">
        <p className="text-xs font-medium text-gray-600 mb-1">Motiu d'ingrés:</p>
        <p className="text-sm text-gray-700 line-clamp-2">{patient.admissionReason}</p>
      </div>

      {/* Medications */}
      {patient.medications.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Pill className="w-4 h-4 text-gray-600" />
            <span className="text-xs font-medium text-gray-600">
              Medicacions ({patient.medications.length})
            </span>
          </div>
          <div className="flex flex-wrap gap-1">
            {patient.medications.slice(0, 3).map((med, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded"
              >
                {med.split(' ')[0]}
              </span>
            ))}
            {patient.medications.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                +{patient.medications.length - 3}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="pt-4 border-t border-gray-200">
        <p className="text-xs font-medium text-gray-600 mb-3">Generar document:</p>
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => onGenerateClick(patient.id, 'discharge')}
            disabled={isLoading}
            className="flex flex-col items-center gap-1 p-3 bg-primary-50 hover:bg-primary-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Informe d'Alta"
          >
            <FileText className="w-5 h-5 text-primary-600" />
            <span className="text-xs font-medium text-primary-700">Alta</span>
          </button>
          
          <button
            onClick={() => onGenerateClick(patient.id, 'referral')}
            disabled={isLoading}
            className="flex flex-col items-center gap-1 p-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Informe de Derivació"
          >
            <Send className="w-5 h-5 text-purple-600" />
            <span className="text-xs font-medium text-purple-700">Derivació</span>
          </button>
          
          <button
            onClick={() => onGenerateClick(patient.id, 'clinical-summary')}
            disabled={isLoading}
            className="flex flex-col items-center gap-1 p-3 bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Resum Clínic"
          >
            <ClipboardList className="w-5 h-5 text-orange-600" />
            <span className="text-xs font-medium text-orange-700">Resum</span>
          </button>
        </div>
      </div>
    </div>
  );
}
