# 🎨 Frontend Scripts

Scripts per gestionar el frontend del Healthcare RAG System.

## 📜 Scripts Disponibles

### `start-frontend.sh`
Arrenca el servidor de desenvolupament del frontend.

**Funcionalitats:**
- ✅ Verifica fnm i Node.js
- ✅ Instal·la dependències si cal
- ✅ Crea .env.local si no existeix
- ✅ Comprova estat del backend API
- ✅ Arrenca servidor Vite a http://localhost:5173

**Ús:**
```bash
./scripts/frontend/start-frontend.sh
```

## 🚀 Flux d'Execució

```
1. Verificar fnm instal·lat
2. Verificar Node.js disponible
3. Instal·lar dependències (si cal)
4. Crear .env.local (si cal)
5. Comprovar backend API
6. Arrencar servidor Vite
```

## 📋 Prerequisits

- fnm (Fast Node Manager)
- Node.js 24+ (s'instal·la automàticament amb fnm)
- Backend API corrent (opcional, però recomanat)

## 🔧 Troubleshooting

### fnm no trobat
```bash
brew install fnm
echo 'eval "$(fnm env --use-on-cd)"' >> ~/.zshrc
source ~/.zshrc
```

### Backend API offline
```bash
cd ../..
./scripts/lifecycle/start.sh
```

### Port 5173 ocupat
Edita `frontend/vite.config.ts` i canvia el port.
