// Example patients based on evaluation cases

import type { Patient } from '../types';

export const EXAMPLE_PATIENTS: Patient[] = [
  {
    id: 'cardiology_ami_001',
    name: 'Joan García Martínez',
    age: 68,
    gender: 'Home',
    specialty: 'Cardiologia',
    condition: 'Infart agut de miocardi',
    admissionReason: 'Dolor toràcic opressiu de 2 hores d\'evolució amb irradiació a braç esquerre i mandíbula. Diaforesi i dispnea associades.',
    medications: [
      'Àcid acetilsalicílic 100mg/24h',
      'Atorvastatina 80mg/24h',
      'Bisoprolol 5mg/24h',
      'Ramipril 5mg/24h',
      'Clopidogrel 75mg/24h'
    ],
    history: [
      'Hipertensió arterial en tractament',
      'Dislipèmia',
      'Exfumador (20 paquets/any)',
      'Diabetis mellitus tipus 2'
    ]
  },
  {
    id: 'endocrinology_diabetes_001',
    name: 'Maria López Fernández',
    age: 54,
    gender: 'Dona',
    specialty: 'Endocrinologia',
    condition: 'Diabetis mellitus tipus 2 descompensada',
    admissionReason: 'Poliúria, polidipsia i pèrdua de pes de 3 setmanes d\'evolució. Glucèmia capilar de 450 mg/dL.',
    medications: [
      'Metformina 850mg/12h',
      'Glicazida 60mg/24h',
      'Enalapril 10mg/24h',
      'Simvastatina 20mg/24h'
    ],
    history: [
      'Diabetis mellitus tipus 2 de 10 anys d\'evolució',
      'Hipertensió arterial',
      'Obesitat (IMC 32)',
      'Retinopatia diabètica no proliferativa'
    ]
  },
  {
    id: 'neurology_stroke_001',
    name: 'Pere Sánchez Vila',
    age: 72,
    gender: 'Home',
    specialty: 'Neurologia',
    condition: 'Ictus isquèmic',
    admissionReason: 'Hemiparèsia dreta i afàsia d\'inici sobtat fa 3 hores. Desorientació temporoespacial.',
    medications: [
      'Àcid acetilsalicílic 100mg/24h',
      'Atorvastatina 40mg/24h',
      'Amlodipí 5mg/24h'
    ],
    history: [
      'Fibril·lació auricular paroxística',
      'Hipertensió arterial',
      'Dislipèmia',
      'AIT previ fa 2 anys'
    ]
  },
  {
    id: 'internal_medicine_pneumonia_001',
    name: 'Anna Rodríguez Pujol',
    age: 65,
    gender: 'Dona',
    specialty: 'Medicina Interna',
    condition: 'Pneumònia adquirida a la comunitat',
    admissionReason: 'Febre de 39°C, tos productiva amb expectoració purulenta i dispnea de 4 dies d\'evolució. Saturació O2 88% aire ambient.',
    medications: [
      'Amoxicil·lina-àcid clavulànic 1g/8h IV',
      'Azitromicina 500mg/24h',
      'Paracetamol 1g/8h si febre',
      'Omeprazol 20mg/24h'
    ],
    history: [
      'MPOC GOLD II',
      'Exfumadora',
      'Sense al·lèrgies medicamentoses conegudes'
    ]
  }
];

export const USE_CASES = [
  {
    id: 'discharge' as const,
    name: 'Informe d\'Alta',
    description: 'Generar informe d\'alta hospitalària amb diagnòstics codificats i recomanacions',
    icon: 'FileText',
    endpoint: '/generate/discharge-summary'
  },
  {
    id: 'referral' as const,
    name: 'Informe de Derivació',
    description: 'Generar informe de derivació a especialista amb motiu clínic codificat',
    icon: 'Send',
    endpoint: '/generate/referral'
  },
  {
    id: 'clinical-summary' as const,
    name: 'Resum Clínic',
    description: 'Generar resum clínic previ a consulta amb alertes i interaccions',
    icon: 'ClipboardList',
    endpoint: '/generate/clinical-summary'
  }
];
