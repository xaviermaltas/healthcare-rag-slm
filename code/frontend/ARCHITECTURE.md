# 🏗️ Arquitectura del Frontend

## 📊 Diagrama de Flux

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Patient 1   │  │  Patient 2   │  │  Patient 3   │          │
│  │  Card        │  │  Card        │  │  Card        │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┴──────────────────┘                  │
│                            │                                      │
│                            ▼                                      │
│                   ┌─────────────────┐                            │
│                   │  Action Buttons │                            │
│                   │  - Alta         │                            │
│                   │  - Derivació    │                            │
│                   │  - Resum        │                            │
│                   └────────┬────────┘                            │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REACT COMPONENTS                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  App.tsx (Main Component)                                │  │
│  │  - State management (useState)                           │  │
│  │  - API health check                                      │  │
│  │  - Loading states                                        │  │
│  │  - Modal control                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│         ┌───────────────────┼───────────────────┐               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │ PatientCard │   │ ResultModal  │   │ LoadingState │        │
│  │ Component   │   │ Component    │   │ Component    │        │
│  └─────────────┘   └──────────────┘   └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API SERVICE LAYER                          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  apiService (services/api.ts)                            │  │
│  │                                                           │  │
│  │  Methods:                                                │  │
│  │  - generateDischargeSummary()                            │  │
│  │  - generateReferral()                                    │  │
│  │  - generateClinicalSummary()                             │  │
│  │  - healthCheck()                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                         │
│                    http://localhost:8000                         │
│                                                                   │
│  Endpoints:                                                      │
│  - POST /generate/discharge-summary                              │
│  - POST /generate/referral                                       │
│  - POST /generate/clinical-summary                               │
│  - GET  /health                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Flux de Dades Detallat

### 1. Selecció de Pacient i Acció

```typescript
User clicks button → handleGenerate(patientId, useCase)
                     ↓
                  setIsLoading(true)
                     ↓
              Find patient data
                     ↓
            Build request payload
```

### 2. Crida a l'API

```typescript
Request Payload Example (Discharge Summary):
{
  patient_context: "Home de 68 anys",
  admission_reason: "Dolor toràcic opressiu...",
  hospital_course: "Pacient ingressat per...",
  discharge_condition: "Estable, milloria clínica",
  medications: ["Àcid acetilsalicílic 100mg/24h", ...],
  follow_up_instructions: "Control per Cardiologia...",
  language: "ca"
}
                     ↓
              API Service Layer
                     ↓
         fetch(API_URL + endpoint, {
           method: 'POST',
           body: JSON.stringify(payload)
         })
                     ↓
              Backend Processing
            (30-60 segons)
                     ↓
              JSON Response
```

### 3. Processament de Resposta

```typescript
Response Example:
{
  discharge_summary: "...",
  medical_codes: {
    snomed: [{code: "I21.9", confidence: 0.92}],
    atc: [{code: "B01AC06", confidence: 0.95}]
  },
  validation_status: {...},
  generation_metadata: {
    generation_time_seconds: 45.2
  }
}
                     ↓
          setResult(response)
                     ↓
         setShowModal(true)
                     ↓
      ResultModal displays data
```

## 📦 Estructura de Components

### App.tsx
**Responsabilitats:**
- State management global
- API health monitoring
- Coordinar interaccions entre components
- Gestió de loading states

**State:**
```typescript
const [isLoading, setIsLoading] = useState(false);
const [result, setResult] = useState<GenerationResult | null>(null);
const [showModal, setShowModal] = useState(false);
const [currentUseCase, setCurrentUseCase] = useState('');
const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');
```

### PatientCard.tsx
**Props:**
```typescript
{
  patient: Patient;
  onGenerateClick: (patientId, useCase) => void;
  isLoading?: boolean;
}
```

**Responsabilitats:**
- Mostrar informació del pacient
- 3 botons d'acció (Alta, Derivació, Resum)
- Disable buttons quan isLoading

### ResultModal.tsx
**Props:**
```typescript
{
  isOpen: boolean;
  onClose: () => void;
  result: GenerationResult | null;
  useCase: string;
}
```

**Responsabilitats:**
- Mostrar document generat
- Mostrar codis mèdics amb confidence
- Temps de generació
- JSON complet (collapsible)
- Gestió d'errors

## 🎨 Styling amb TailwindCSS

### Utilitats Personalitzades

```css
/* index.css */
@layer components {
  .btn-primary {
    @apply bg-primary-600 hover:bg-primary-700 
           text-white font-medium py-2 px-4 
           rounded-lg transition-colors duration-200;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-md 
           p-6 border border-gray-200;
  }
  
  .badge-emergency {
    @apply bg-medical-emergency text-white 
           px-2 py-1 rounded-full text-xs font-semibold;
  }
}
```

### Colors Personalitzats

```javascript
// tailwind.config.js
colors: {
  primary: {
    50: '#f0f9ff',
    600: '#0284c7',
    700: '#0369a1',
  },
  medical: {
    emergency: '#dc2626',
    warning: '#f59e0b',
    success: '#10b981',
    info: '#3b82f6',
  }
}
```

## 🔌 Integració amb Backend

### Environment Variables
```bash
# .env.local
VITE_API_URL=http://localhost:8000
```

### CORS Configuration
El backend FastAPI ha de permetre requests del frontend:
```python
# Backend: main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Optimitzacions

### Code Splitting
Vite automàticament fa code splitting per:
- Components lazy-loaded
- Vendor chunks separats
- CSS per component

### Performance
- **Bundle size:** ~150KB gzipped
- **First Load:** <1s
- **Time to Interactive:** <2s

### Caching
```typescript
// API responses no es fan cache (dades dinàmiques)
// Assets estàtics: cache infinit amb hash
```

## 🧪 Testing Strategy (Future)

```typescript
// Component tests
describe('PatientCard', () => {
  it('renders patient information', () => {...});
  it('calls onGenerateClick with correct params', () => {...});
  it('disables buttons when loading', () => {...});
});

// Integration tests
describe('App Integration', () => {
  it('generates discharge summary end-to-end', () => {...});
  it('handles API errors gracefully', () => {...});
});
```

## 📱 Responsive Design

```
Desktop (>1024px):  Grid 2 columns
Tablet (768-1024px): Grid 2 columns
Mobile (<768px):    Grid 1 column
```

## 🔐 Security Considerations

- **No sensitive data** en localStorage
- **API URL** configurable via env vars
- **HTTPS** en producció
- **CORS** configurat correctament
- **No API keys** al frontend

---

**Última actualització:** 3 de Maig de 2026
