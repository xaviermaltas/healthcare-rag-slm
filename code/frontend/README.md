# 🏥 Healthcare RAG System - Frontend

Frontend web modern per demostrar les funcionalitats del sistema RAG mèdic.

## 🎯 Descripció

Aplicació web desenvolupada amb **React + TypeScript + TailwindCSS** que proporciona una interfície intuïtiva per interactuar amb el sistema Healthcare RAG. Permet generar documents clínics automàticament utilitzant IA.

## 🚀 Tecnologies

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite (ultra-ràpid HMR)
- **Styling:** TailwindCSS 3
- **Icons:** Lucide React
- **Node Manager:** fnm (Fast Node Manager)
- **Node Version:** 24.15.0 (LTS)

## 📋 Prerequisits

1. **fnm (Fast Node Manager)**
   ```bash
   brew install fnm
   echo 'eval "$(fnm env --use-on-cd)"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Node.js LTS**
   ```bash
   fnm install --lts
   fnm default lts-latest
   ```

3. **Backend API corrent**
   - El backend FastAPI ha d'estar actiu a `http://localhost:8000`
   - Veure `../README.md` per instruccions del backend

## 🛠️ Instal·lació

```bash
# 1. Navegar al directori frontend
cd frontend

# 2. Instal·lar dependències
npm install

# 3. Configurar variables d'entorn
cp .env.example .env.local
# Editar .env.local si cal canviar l'URL de l'API
```

## 🎨 Desenvolupament

```bash
# Iniciar servidor de desenvolupament
npm run dev

# L'aplicació estarà disponible a:
# http://localhost:5173
```

El servidor de desenvolupament inclou:
- ⚡ Hot Module Replacement (HMR) ultra-ràpid
- 🔄 Recàrrega automàtica en canvis
- 🎯 TypeScript type checking
- 🎨 TailwindCSS amb JIT compiler

## 🏗️ Build per Producció

```bash
# Compilar per producció
npm run build

# Previsualitzar build de producció
npm run preview
```

## 📁 Estructura del Projecte

```
frontend/
├── src/
│   ├── components/          # Components React
│   │   ├── PatientCard.tsx  # Targeta de pacient
│   │   └── ResultModal.tsx  # Modal de resultats
│   ├── data/                # Dades estàtiques
│   │   └── patients.ts      # Pacients d'exemple
│   ├── services/            # Serveis API
│   │   └── api.ts           # Client API
│   ├── types/               # TypeScript types
│   │   └── index.ts         # Tipus globals
│   ├── App.tsx              # Component principal
│   ├── main.tsx             # Entry point
│   └── index.css            # Styles globals (Tailwind)
├── .env.example             # Variables d'entorn (template)
├── .nvmrc                   # Versió Node.js per fnm
├── tailwind.config.js       # Configuració Tailwind
└── package.json             # Dependències i scripts
```

## 🎯 Funcionalitats

### 1. Visualització de Pacients
- 4 pacients d'exemple basats en casos reals
- Informació detallada: nom, edat, especialitat, condició
- Medicacions i antecedents mèdics

### 2. Generació de Documents

#### 📄 Informe d'Alta (~60s)
- Diagnòstics codificats (SNOMED CT, ICD-10)
- Medicacions codificades (ATC)
- Recomanacions de seguiment

#### 📤 Informe de Derivació (~40s)
- Motiu codificat (SNOMED CT)
- Especialitat destí
- Nivell d'urgència

#### 📋 Resum Clínic (~30s)
- Antecedents rellevants
- Alertes i interaccions
- Medicacions actuals

## 🔧 Configuració

### Variables d'Entorn (.env.local)
```bash
VITE_API_URL=http://localhost:8000
```

## 📝 Scripts Disponibles

```bash
npm run dev          # Desenvolupament
npm run build        # Build producció
npm run preview      # Preview build
```

## 🐛 Troubleshooting

### API Offline
Assegura't que el backend està corrent:
```bash
cd ..
docker-compose up -d
```

### Port 5173 ja en ús
Edita `vite.config.ts` i canvia el port.

## 📄 Llicència

TFM Xavier Maltas Tarridas - 2026
