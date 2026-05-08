import { Activity, Pill, ExternalLink } from 'lucide-react';

interface CodedCondition {
  condition: string;
  snomed_code?: string;
  icd10_code?: string;
  relevance?: string;
  source?: string;
}

interface CodedMedication {
  medication: string;
  atc_code?: string;
  therapeutic_class?: string;
  source?: string;
}

interface CodedConditionsPanelProps {
  conditions?: CodedCondition[];
  medications?: CodedMedication[];
}

export function CodedConditionsPanel({ conditions = [], medications = [] }: CodedConditionsPanelProps) {
  // Generate BioPortal URL for SNOMED CT
  const getSnomedUrl = (code: string): string => {
    return `https://bioportal.bioontology.org/ontologies/SNOMEDCT?p=classes&conceptid=${code}`;
  };

  // Generate BioPortal URL for ICD-10
  const getIcd10Url = (code: string): string => {
    return `https://bioportal.bioontology.org/ontologies/ICD10?p=classes&conceptid=${code}`;
  };

  // Generate BioPortal URL for ATC
  const getAtcUrl = (code: string): string => {
    return `https://bioportal.bioontology.org/ontologies/ATC?p=classes&conceptid=${code}`;
  };

  return (
    <div className="space-y-6">
      {/* Conditions */}
      {conditions && conditions.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-bold text-gray-900">Condicions Codificades</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {conditions.map((cond, idx) => (
              <div
                key={idx}
                className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-300 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <p className="font-semibold text-gray-900 mb-2">{cond.condition}</p>
                <div className="space-y-1 text-sm">
                  {cond.snomed_code && (
                    <div className="flex items-center gap-2">
                      <span className="inline-block w-2 h-2 bg-blue-600 rounded-full"></span>
                      <span className="text-gray-700">
                        <span className="font-mono font-bold text-blue-700">SNOMED:</span> {cond.snomed_code}
                      </span>
                      <a
                        href={getSnomedUrl(cond.snomed_code)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 transition-colors"
                        title="Veure a BioPortal"
                      >
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  )}
                  {cond.icd10_code && (
                    <div className="flex items-center gap-2">
                      <span className="inline-block w-2 h-2 bg-blue-600 rounded-full"></span>
                      <span className="text-gray-700">
                        <span className="font-mono font-bold text-blue-700">ICD-10:</span> {cond.icd10_code}
                      </span>
                      <a
                        href={getIcd10Url(cond.icd10_code)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 transition-colors"
                        title="Veure a BioPortal"
                      >
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  )}
                  {cond.relevance && (
                    <div className="text-xs text-gray-600 mt-2">
                      Rellevància: <span className="font-semibold capitalize">{cond.relevance}</span>
                    </div>
                  )}
                  {cond.source && (
                    <div className="text-xs text-gray-500">
                      Font: {cond.source}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Medications */}
      {medications && medications.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Pill className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-bold text-gray-900">Medicaments Codificats</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {medications.map((med, idx) => (
              <div
                key={idx}
                className="bg-gradient-to-br from-green-50 to-green-100 border border-green-300 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <p className="font-semibold text-gray-900 mb-2">{med.medication}</p>
                <div className="space-y-1 text-sm">
                  {med.atc_code ? (
                    <div className="flex items-center gap-2">
                      <span className="inline-block w-2 h-2 bg-green-600 rounded-full"></span>
                      <span className="text-gray-700">
                        <span className="font-mono font-bold text-green-700">ATC:</span> {med.atc_code}
                      </span>
                      <a
                        href={getAtcUrl(med.atc_code)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-green-600 hover:text-green-800 transition-colors"
                        title="Veure a BioPortal"
                      >
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span className="inline-block w-2 h-2 bg-gray-400 rounded-full"></span>
                      <span className="text-gray-500 italic">Codi ATC no disponible</span>
                    </div>
                  )}
                  {med.therapeutic_class && med.therapeutic_class !== 'Unknown' && (
                    <div className="text-xs text-gray-600 mt-2">
                      Classe: <span className="font-semibold">{med.therapeutic_class}</span>
                    </div>
                  )}
                  {med.source && (
                    <div className="text-xs text-gray-500">
                      Font: {med.source}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
