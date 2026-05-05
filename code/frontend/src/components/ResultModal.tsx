import { X, CheckCircle, XCircle, Clock, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';
import { CodedConditionsPanel } from './CodedConditionsPanel';
import type { GenerationResult } from '../types';

interface ResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: GenerationResult | null;
  useCase: string;
}

export function ResultModal({ isOpen, onClose, result, useCase }: ResultModalProps) {
  const [copiedJson, setCopiedJson] = useState(false);
  const [copiedDocument, setCopiedDocument] = useState(false);

  if (!isOpen || !result) return null;

  const getDocumentTitle = (useCase: string): string => {
    const titles: Record<string, string> = {
      'discharge': 'Informe d\'Alta Hospitalària',
      'discharge-summary': 'Informe d\'Alta Hospitalària',
      'referral': 'Informe de Derivació a Especialista',
      'clinical-summary': 'Resum Clínic Previ a Consulta',
    };
    return titles[useCase] || 'Document Generat';
  };

  const getDocumentContent = (): string => {
    if (!result.data) return '';
    return (
      result.data.discharge_document ||
      result.data.referral_document ||
      result.data.discharge_summary ||
      result.data.referral_summary ||
      result.data.summary ||
      result.data.clinical_summary ||
      result.data.generated_text ||
      result.data.text ||
      ''
    );
  };

  const copyDocumentToClipboard = async () => {
    const content = getDocumentContent();
    if (content) {
      await navigator.clipboard.writeText(content);
      setCopiedDocument(true);
      setTimeout(() => setCopiedDocument(false), 2000);
    }
  };

  const copyToClipboard = async () => {
    if (result.data) {
      await navigator.clipboard.writeText(JSON.stringify(result.data, null, 2));
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            {result.success ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600" />
            )}
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {result.success ? 'Document generat' : 'Error en la generació'}
              </h2>
              <p className="text-sm text-gray-500">{getDocumentTitle(useCase)}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {result.success && result.data ? (
            <div className="space-y-6">
              {/* Generation Time */}
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Clock className="w-4 h-4" />
                <span>Temps de generació: {result.generationTime?.toFixed(2)}s</span>
              </div>

              {/* ALWAYS SHOW: Document Text - Rendered as Markdown */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">📄 {getDocumentTitle(useCase)}</h3>
                    <p className="text-sm text-gray-500 mt-1">Document generat automàticament pel sistema RAG</p>
                  </div>
                  <button
                    onClick={copyDocumentToClipboard}
                    className="flex items-center gap-2 px-3 py-2 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg transition-colors"
                  >
                    {copiedDocument ? (
                      <>
                        <Check className="w-4 h-4" />
                        Copiat!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copiar text
                      </>
                    )}
                  </button>
                </div>
                <div className="bg-white border border-gray-300 rounded-lg p-8 shadow-sm">
                  <MarkdownRenderer
                    content={getDocumentContent() || 'No s\'ha generat cap text'}
                  />
                </div>
              </div>

              {/* Coded Conditions and Medications */}
              {(result.data.relevant_conditions || result.data.coded_medications) && (
                <CodedConditionsPanel
                  conditions={result.data.relevant_conditions}
                  medications={result.data.coded_medications}
                />
              )}

              {/* Medical Codes (Legacy) */}
              {result.data.medical_codes && (
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-3">🏥 Codis Mèdics (Legacy)</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {result.data.medical_codes.snomed && result.data.medical_codes.snomed.length > 0 && (
                      <div className="bg-white border-2 border-blue-200 rounded-lg p-4 shadow-sm">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
                            <span className="text-white text-xs font-bold">SC</span>
                          </div>
                          <div>
                            <p className="text-sm font-bold text-blue-900">SNOMED CT</p>
                            <p className="text-xs text-blue-600">Terminologia clínica</p>
                          </div>
                        </div>
                        <div className="space-y-2">
                          {result.data.medical_codes.snomed.map((code: any, idx: number) => (
                            <div key={idx} className="bg-blue-50 p-2 rounded border border-blue-200">
                              <div className="flex items-center justify-between">
                                <span className="font-mono text-sm font-semibold text-blue-900">{code.code}</span>
                                {code.confidence && (
                                  <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded-full">
                                    {(code.confidence * 100).toFixed(0)}%
                                  </span>
                                )}
                              </div>
                              {code.label && (
                                <p className="text-xs text-blue-700 mt-1">{code.label}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {result.data.medical_codes.atc && result.data.medical_codes.atc.length > 0 && (
                      <div className="bg-white border-2 border-green-200 rounded-lg p-4 shadow-sm">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="w-8 h-8 bg-green-600 rounded flex items-center justify-center">
                            <span className="text-white text-xs font-bold">ATC</span>
                          </div>
                          <div>
                            <p className="text-sm font-bold text-green-900">ATC</p>
                            <p className="text-xs text-green-600">Classificació de medicaments</p>
                          </div>
                        </div>
                        <div className="space-y-2">
                          {result.data.medical_codes.atc.map((code: any, idx: number) => (
                            <div key={idx} className="bg-green-50 p-2 rounded border border-green-200">
                              <div className="flex items-center justify-between">
                                <span className="font-mono text-sm font-semibold text-green-900">{code.code}</span>
                                {code.confidence && (
                                  <span className="text-xs bg-green-600 text-white px-2 py-1 rounded-full">
                                    {(code.confidence * 100).toFixed(0)}%
                                  </span>
                                )}
                              </div>
                              {code.label && (
                                <p className="text-xs text-green-700 mt-1">{code.label}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ALWAYS SHOW: Raw JSON */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-bold text-gray-900">👨‍💻 Resposta JSON (Desenvolupadors)</h3>
                  <button
                    onClick={copyToClipboard}
                    className="flex items-center gap-2 px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
                  >
                    {copiedJson ? (
                      <>
                        <Check className="w-4 h-4" />
                        Copiat!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copiar
                      </>
                    )}
                  </button>
                </div>
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 overflow-hidden">
                  <pre className="text-xs text-green-400 overflow-x-auto font-mono max-h-96">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-600 font-medium mb-2">Error en la generació</p>
              <p className="text-gray-600 text-sm">{result.error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="btn-primary"
          >
            Tancar
          </button>
        </div>
      </div>
    </div>
  );
}
