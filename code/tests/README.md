# 🧪 Tests del Sistema Healthcare RAG

Aquesta carpeta conté tots els tests del projecte, organitzats per tipus.

---

## 📁 Estructura

```
tests/
├── unit/                          # Tests unitaris (mocks, sense APIs reals)
│   └── infrastructure/
│       └── test_ontology_manager_mock.py
│
└── integration/                   # Tests d'integració (amb APIs reals)
    └── test_ontologies_integration.py
```

---

## 🎯 Tipus de Tests

### **Tests Unitaris** (`/unit`)

**Què són:** Tests que proven components individuals de forma aïllada, utilitzant mocks per simular dependències externes.

**Característiques:**
- ✅ Ràpids (segons)
- ✅ No requereixen connexió a internet
- ✅ No requereixen API keys
- ✅ Utilitzen dades mock

**Exemple:**
- `test_ontology_manager_mock.py` - Prova `OntologyManager` amb respostes simulades de BioPortal

**Executar:**
```bash
./scripts/activate_and_run.sh pytest tests/unit/ -v
```

---

### **Tests d'Integració** (`/integration`)

**Què són:** Tests que proven la integració amb serveis externs reals (BioPortal, PubMed, Qdrant, etc.).

**Característiques:**
- ⏱️ Més lents (segons/minuts)
- 🌐 Requereixen connexió a internet
- 🔑 Requereixen API keys configurades
- 📊 Utilitzen dades reals

**Exemple:**
- `test_ontologies_integration.py` - Prova connexió real a BioPortal i cerca de conceptes

**Executar:**
```bash
# Opció 1: Utilitzar script dedicat
./scripts/run_ontology_tests.sh

# Opció 2: Executar directament
./scripts/activate_and_run.sh python3 tests/integration/test_ontologies_integration.py
```

**Prerequisits:**
- Sistema aixecat (`./scripts/start.sh`)
- API key de BioPortal configurada a `.env`

---

## 🚀 Executar Tests

### **Tots els tests unitaris**
```bash
./scripts/activate_and_run.sh pytest tests/unit/ -v
```

### **Tots els tests d'integració**
```bash
./scripts/activate_and_run.sh pytest tests/integration/ -v
```

### **Tots els tests**
```bash
./scripts/activate_and_run.sh pytest tests/ -v
```

### **Un test específic**
```bash
./scripts/activate_and_run.sh pytest tests/unit/infrastructure/test_ontology_manager_mock.py -v
```

### **Amb coverage**
```bash
./scripts/activate_and_run.sh pytest tests/ --cov=src/main --cov-report=html
```

---

## 📊 Tests Disponibles

### **Tests d'Ontologies**

| Test | Tipus | Fitxer | Descripció |
|------|-------|--------|------------|
| OntologyManager Mock | Unit | `unit/infrastructure/test_ontology_manager_mock.py` | Prova amb dades mock |
| Ontologies Integration | Integration | `integration/test_ontologies_integration.py` | Prova amb BioPortal real |

**Tests d'integració inclouen:**
1. ✅ Connexió a BioPortal
2. ✅ Estadístiques d'ontologies
3. ✅ Cerca SNOMED CT
4. ✅ Cerca MeSH
5. ✅ Cerca ICD-10
6. ✅ Cerca multi-ontologia
7. ✅ Mapatge de text clínic

---

## 🔧 Configuració

### **Variables d'entorn necessàries**

Per tests d'integració, assegura't que tens configurat a `.env`:

```bash
# Obligatori per tests d'ontologies
BIOPORTAL_API_KEY=your-api-key-here
BIOPORTAL_BASE_URL=https://data.bioontology.org

# Opcional per tests de PubMed
NCBI_API_KEY=your-ncbi-key-here
NCBI_EMAIL=your-email@example.com
```

---

## 📝 Escriure Nous Tests

### **Test Unitari**

```python
# tests/unit/infrastructure/test_my_component.py

import pytest
from unittest.mock import AsyncMock, patch

from src.main.infrastructure.my_component import MyComponent


class TestMyComponent:
    """Test MyComponent with mocked dependencies"""
    
    @pytest.mark.asyncio
    async def test_my_method(self):
        """Test my_method with mock data"""
        
        with patch('aiohttp.ClientSession') as mock_session:
            # Setup mock
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={'data': 'test'})
            
            mock_session_instance = AsyncMock()
            mock_session_instance.get = AsyncMock(return_value=mock_response)
            mock_session.return_value = mock_session_instance
            
            # Test
            component = MyComponent()
            result = await component.my_method()
            
            # Assertions
            assert result is not None
```

### **Test d'Integració**

```python
# tests/integration/test_my_integration.py

import asyncio
import pytest

from src.main.infrastructure.my_component import MyComponent
from config.settings import get_settings


async def test_real_api_call():
    """Test with real API call"""
    
    settings = get_settings()
    
    if not settings.MY_API_KEY:
        pytest.skip("API key not configured")
    
    component = MyComponent(api_key=settings.MY_API_KEY)
    
    result = await component.fetch_data()
    
    assert result is not None
    assert len(result) > 0


if __name__ == "__main__":
    asyncio.run(test_real_api_call())
```

---

## 🐛 Troubleshooting

### **Error: "No module named 'pytest'"**
```bash
# Instal·la pytest
./scripts/activate_and_run.sh pip install pytest pytest-asyncio pytest-cov
```

### **Error: "API key not set"**
```bash
# Verifica .env
cat .env | grep BIOPORTAL_API_KEY

# Afegeix si falta
echo "BIOPORTAL_API_KEY=your-key-here" >> .env
```

### **Tests d'integració fallen**
```bash
# Verifica que el sistema està aixecat
./scripts/start.sh

# Verifica connexió a internet
curl https://data.bioontology.org/ontologies

# Executa tests amb més verbositat
./scripts/activate_and_run.sh pytest tests/integration/ -vv -s
```

---

## 📚 Més Informació

- **Scripts:** `../scripts/README.md`
- **Arquitectura:** `../docs/ARCHITECTURE.md`
- **Setup:** `../docs/SETUP.md`
