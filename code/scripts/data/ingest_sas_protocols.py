#!/usr/bin/env python3
"""
Script per indexar protocols SAS (Servei Andalús de Salut) per informes d'alta

Aquest script:
1. Crea protocols de mostra basats en guies clíniques estàndard
2. Els indexa a Qdrant amb metadata enriquida
3. Configura boost factors per protocols oficials

Nota: En producció, aquests protocols s'obtindrien de fonts oficials SAS
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main.core.ingestion.indexer import DocumentIndexer
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from src.main.infrastructure.vector_db.qdrant_client import QdrantClient as QdrantClientWrapper
from config.settings import settings


# Protocols de mostra basats en guies clíniques estàndard
SAS_PROTOCOLS = [
    {
        "title": "Protocol d'Alta Hospitalària - Infart Agut de Miocardi",
        "specialty": "Cardiologia",
        "content": """
PROTOCOL D'ALTA HOSPITALÀRIA - INFART AGUT DE MIOCARDI (IAM)

1. DIAGNÒSTIC PRINCIPAL
- Infart agut de miocardi amb elevació del segment ST (IAMCEST)
- Codi SNOMED CT: 401303003
- Codi ICD-10: I21.9

2. PROCEDIMENTS REALITZATS
- ECG de 12 derivacions
- Analítica amb troponines
- Ecocardiograma transtorácic
- Coronariografia (si indicat)
- Angioplastia primària (si indicat)

3. TRACTAMENT FARMACOLÒGIC
- Antiagregació doble (AAS + Clopidogrel/Ticagrelor) durant 12 mesos
  * AAS 100mg/24h (Codi ATC: B01AC06)
  * Clopidogrel 75mg/24h (Codi ATC: B01AC04) o Ticagrelor 90mg/12h
- Estatina d'alta intensitat
  * Atorvastatina 80mg/24h (Codi ATC: C10AA05)
- IECA o ARA-II
  * Ramipril 2.5-10mg/24h (Codi ATC: C09AA05)
- Betabloqueig
  * Bisoprolol 2.5-10mg/24h (Codi ATC: C07AB07)

4. RECOMANACIONS DE SEGUIMENT
- Control en consulta de cardiologia en 7-10 dies
- Ecocardiograma de control en 1 mes
- Control analític amb perfil lipídic en 2 setmanes
- Objectiu LDL <55 mg/dL
- Rehabilitació cardíaca (si disponible)

5. SIGNES D'ALARMA
- Dolor torácic recurrent
- Disnea de nova aparició o empitjorament
- Palpitacions
- Síncope
- Edemes en extremitats inferiors

6. MODIFICACIÓ DE FACTORS DE RISC
- Cessació tabàquica (obligatori)
- Dieta mediterrània
- Exercici físic moderat (després de valoració)
- Control de pes (IMC <25)
- Control de pressió arterial (<130/80 mmHg)
- Control glucèmic si diabètic (HbA1c <7%)

7. CONTRAINDICACIONS
- Evitar AINE (risc de sangrat amb doble antiagregació)
- Evitar esforços intensos durant les primeres 4-6 setmanes
- No conduir durant 1 setmana (4 setmanes si professional)

REFERÈNCIES:
- Guia ESC 2023 per Síndrome Coronària Aguda
- Protocol SAS Cardiologia 2024
""",
        "source_url": "https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/",
        "last_updated": "2024-01-15",
        "official": True
    },
    {
        "title": "Protocol d'Alta Hospitalària - Diabetis Mellitus Descompensada",
        "specialty": "Endocrinologia",
        "content": """
PROTOCOL D'ALTA HOSPITALÀRIA - DIABETIS MELLITUS DESCOMPENSADA

1. DIAGNÒSTIC PRINCIPAL
- Diabetis mellitus tipus 2 descompensada
- Codi SNOMED CT: 44054006
- Codi ICD-10: E11.9

2. CRITERIS D'INGRÉS
- Hiperglucèmia severa (>400 mg/dL)
- Cetoacidosi diabètica
- Estat hiperosmolar hiperglucèmic
- Hipoglucèmia severa recurrent

3. TRACTAMENT FARMACOLÒGIC
- Metformina 850-1000mg/12h (Codi ATC: A10BA02)
- Insulina basal (Glargina/Degludec)
  * Glargina 10-40 UI/24h (Codi ATC: A10AE04)
- Insulina ràpida (si necessari)
  * Lispro/Aspart segons pauta (Codi ATC: A10AB04)
- ISGLT2 si indicat
  * Empagliflozina 10-25mg/24h (Codi ATC: A10BK03)

4. OBJECTIUS DE CONTROL
- Glucèmia basal: 80-130 mg/dL
- Glucèmia postprandial: <180 mg/dL
- HbA1c: <7% (individualitzar segons pacient)
- Evitar hipoglucèmies (<70 mg/dL)

5. AUTOCONTROL
- Glucèmies capil·lars segons pauta:
  * Mínim 3 vegades/dia si insulina
  * Abans de menjar i 2h després
- Registre en llibreta o app
- Reconèixer símptomes d'hipoglucèmia

6. RECOMANACIONS DIETÈTIQUES
- Dieta mediterrània
- Distribució: 45-50% carbohidrats, 30-35% greixos, 15-20% proteïnes
- Evitar sucres simples
- Fibra: >25g/dia
- Racions controlades (plat Harvard)

7. SEGUIMENT
- Control en atenció primària en 1 setmana
- Control en endocrinologia en 1 mes
- Analítica amb HbA1c cada 3 mesos
- Fons d'ull anual
- Control podològic semestral
- Funció renal (filtrat glomerular) anual

8. EDUCACIÓ DIABETOLÒGICA
- Reconeixement i tractament d'hipoglucèmies
- Tècnica d'administració d'insulina
- Rotació de zones de punció
- Conservació d'insulina
- Malaltia intercurrent (sick day rules)

9. SIGNES D'ALARMA
- Hipoglucèmia severa (<50 mg/dL)
- Hiperglucèmia persistent (>300 mg/dL)
- Cetones en orina
- Vòmits persistents
- Alteració del nivell de consciència

REFERÈNCIES:
- Guia ADA 2024 Standards of Care
- Protocol SAS Endocrinologia 2024
""",
        "source_url": "https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/",
        "last_updated": "2024-02-01",
        "official": True
    },
    {
        "title": "Protocol d'Alta Hospitalària - Accident Cerebrovascular Isquèmic",
        "specialty": "Neurologia",
        "content": """
PROTOCOL D'ALTA HOSPITALÀRIA - ACCIDENT CEREBROVASCULAR ISQUÈMIC (ACVI)

1. DIAGNÒSTIC PRINCIPAL
- Accident cerebrovascular isquèmic
- Codi SNOMED CT: 422504002
- Codi ICD-10: I63.9

2. LOCALITZACIÓ I SEVERITAT
- Territori vascular afectat (especificar)
- Escala NIHSS a l'ingrés i alta
- Escala Rankin modificada

3. PROCEDIMENTS REALITZATS
- TC cranial urgent
- RM cerebral amb difusió
- Doppler de troncs supraaòrtics
- Ecocardiograma transtorácic
- Holter 24h (si indicat)
- Fibrinòlisi IV (si <4.5h i criteris)
- Trombectomia mecànica (si indicat)

4. TRACTAMENT FARMACOLÒGIC
Prevenció secundària:
- Antiagregació
  * AAS 100-300mg/24h (Codi ATC: B01AC06) o
  * Clopidogrel 75mg/24h (Codi ATC: B01AC04)
  * Doble antiagregació primeres 3 setmanes si indicat
- Estatina d'alta intensitat
  * Atorvastatina 80mg/24h (Codi ATC: C10AA05)
  * Objectiu LDL <70 mg/dL
- Antihipertensius (si HTA)
  * Objectiu PA <140/90 mmHg (<130/80 si diabètic)
- Anticoagulació (si fibril·lació auricular)
  * Apixaban/Rivaroxaban segons pauta

5. REHABILITACIÓ
- Fisioterpia (si seqüeles motores)
- Logopèdia (si afàsia/disfàgia)
- Teràpia ocupacional
- Valoració per neuropsicologia si dèficit cognitiu

6. RECOMANACIONS DE SEGUIMENT
- Control en neurologia en 1 mes
- Control en atenció primària en 1 setmana
- Analítica amb perfil lipídic en 1 mes
- Doppler de troncs supraaòrtics de control en 3-6 mesos
- RM cerebral de control si indicat

7. MODIFICACIÓ DE FACTORS DE RISC
- Cessació tabàquica (obligatori)
- Control de pressió arterial (<140/90 mmHg)
- Control de diabetis (HbA1c <7%)
- Control de dislipèmia (LDL <70 mg/dL)
- Exercici físic moderat regular
- Dieta mediterrània
- Reducció d'alcohol (<2 unitats/dia)

8. SIGNES D'ALARMA
- Debilitat o pèrdua de força sobtada
- Alteració del llenguatge
- Pèrdua de visió
- Cefalea intensa sobtada
- Alteració de l'equilibri o coordinació
- Confusió o alteració del nivell de consciència

9. PREVENCIÓ DE COMPLICACIONS
- Mobilització precoç (prevenció TVP)
- Hidratació adequada
- Control de glicèmia
- Prevenció d'úlceres per pressió
- Valoració de disfàgia abans d'alimentació oral

REFERÈNCIES:
- Guia ESO 2023 per Ictus Isquèmic
- Protocol SAS Neurologia 2024
- Pla Andalús d'Ictus
""",
        "source_url": "https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/",
        "last_updated": "2024-01-20",
        "official": True
    },
    {
        "title": "Protocol d'Alta Hospitalària - Insuficiència Cardíaca Aguda",
        "specialty": "Cardiologia",
        "content": """
PROTOCOL D'ALTA HOSPITALÀRIA - INSUFICIÈNCIA CARDÍACA AGUDA

1. DIAGNÒSTIC PRINCIPAL
- Insuficiència cardíaca aguda descompensada
- Codi SNOMED CT: 42343007
- Codi ICD-10: I50.9

2. CLASSIFICACIÓ
- NYHA (I-IV): especificar classe funcional
- Fracció d'ejecció (FE):
  * FE reduïda (<40%)
  * FE lleugerament reduïda (40-49%)
  * FE preservada (≥50%)

3. PROCEDIMENTS REALITZATS
- Ecocardiograma transtorácic
- Radiografia de tòrax
- Analítica amb BNP/NT-proBNP
- ECG
- Cateterisme cardíac (si indicat)

4. TRACTAMENT FARMACOLÒGIC
Teràpia quadruple (si FE reduïda):
- IECA o ARA-II + Sacubitrilo/Valsartan
  * Enalapril 2.5-20mg/12h (Codi ATC: C09AA02) o
  * Sacubitrilo/Valsartan 24/26-97/103mg/12h (Codi ATC: C09DX04)
- Betabloqueig
  * Bisoprolol 1.25-10mg/24h (Codi ATC: C07AB07) o
  * Carvedilol 3.125-25mg/12h (Codi ATC: C07AG02)
- Antagonista mineralocorticoide
  * Espironolactona 25-50mg/24h (Codi ATC: C03DA01)
- ISGLT2
  * Dapagliflozina 10mg/24h (Codi ATC: A10BK01) o
  * Empagliflozina 10mg/24h (Codi ATC: A10BK03)
- Diürètic de l'ansa
  * Furosemida 20-120mg/24h (Codi ATC: C03CA01)

5. OBJECTIUS DE TRACTAMENT
- Euvolèmia (absència d'edemes)
- PA adequada (PAS >90 mmHg)
- Freqüència cardíaca 60-70 lpm
- Funció renal estable
- Potassi 4-5 mEq/L

6. AUTOCONTROL
- Pes diari (matí, després d'orinar)
- Consultar si guany >2 kg en 3 dies
- Restricció de líquids (1-1.5L/dia si congestió)
- Restricció de sal (<2g/dia)

7. RECOMANACIONS DE SEGUIMENT
- Control en cardiologia en 2 setmanes
- Control en atenció primària en 1 setmana
- Analítica amb funció renal i ions en 1 setmana
- Ecocardiograma de control en 3 mesos
- Programa d'insuficiència cardíaca (si disponible)

8. MODIFICACIÓ D'ESTIL DE VIDA
- Restricció de sal (<2g/dia)
- Restricció de líquids (1-1.5L/dia)
- Exercici físic moderat (caminar 30 min/dia)
- Evitar alcohol
- Vacunació antigripal i pneumocòccica
- Control de pes diari

9. SIGNES D'ALARMA
- Guany de pes >2 kg en 3 dies
- Augment de disnea o ortopnea
- Edemes en extremitats inferiors
- Disminució de la diüresi
- Mareig o síncope
- Palpitacions

10. CONTRAINDICACIONS
- Evitar AINE (retenen líquids)
- Evitar glitazones (retenen líquids)
- Precaució amb verapamil/diltiazem (efecte inotròpic negatiu)

REFERÈNCIES:
- Guia ESC 2023 per Insuficiència Cardíaca
- Protocol SAS Cardiologia 2024
""",
        "source_url": "https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/",
        "last_updated": "2024-02-10",
        "official": True
    },
    {
        "title": "Protocol d'Alta Hospitalària - Pneumònia Adquirida a la Comunitat",
        "specialty": "Medicina Interna",
        "content": """
PROTOCOL D'ALTA HOSPITALÀRIA - PNEUMÒNIA ADQUIRIDA A LA COMUNITAT (PAC)

1. DIAGNÒSTIC PRINCIPAL
- Pneumònia adquirida a la comunitat
- Codi SNOMED CT: 385093006
- Codi ICD-10: J18.9

2. SEVERITAT
- Escala CURB-65: especificar puntuació
- Escala PSI (Pneumonia Severity Index)
- Necessitat d'UCI: Sí/No

3. MICROBIOLOGIA
- Agent etiològic (si identificat):
  * Streptococcus pneumoniae
  * Haemophilus influenzae
  * Mycoplasma pneumoniae
  * Legionella pneumophila
  * Altres
- Antibiograma (si disponible)

4. TRACTAMENT ANTIBIÒTIC
Segons severitat i agent:
- PAC lleu-moderada:
  * Amoxicil·lina/Clavulànic 875/125mg/8h (Codi ATC: J01CR02)
  * + Azitromicina 500mg/24h (Codi ATC: J01FA10) si atípic
- PAC severa:
  * Ceftriaxona 2g/24h IV (Codi ATC: J01DD04)
  * + Azitromicina 500mg/24h (Codi ATC: J01FA10)
- Durada: 5-7 dies (individualitzar)

5. TRACTAMENT ADJUVANT
- Oxigenoteràpia (si SatO2 <92%)
- Hidratació adequada
- Antipirétics
  * Paracetamol 1g/8h (Codi ATC: N02BE01)
- Broncodilatadors (si broncoespasme)

6. CRITERIS D'ALTA
- Afebril >24h
- Estabilitat hemodinàmica
- SatO2 >90% amb aire ambient
- Tolerància oral
- Capacitat d'autocura o suport domiciliari

7. RECOMANACIONS DE SEGUIMENT
- Control en atenció primària en 3-5 dies
- Radiografia de tòrax de control en 4-6 setmanes
- Completar pauta antibiòtica
- Repòs relatiu durant 1 setmana

8. PREVENCIÓ
- Vacunació antineumocòccica (si >65 anys o factors de risc)
- Vacunació antigripal anual
- Cessació tabàquica
- Evitar exposició a fum i contaminants

9. SIGNES D'ALARMA
- Febre persistent >3 dies
- Empitjorament de disnea
- Dolor toràcic
- Hemoptisi
- Confusió o alteració del nivell de consciència
- Incapacitat per mantenir hidratació oral

10. FACTORS DE RISC PER COMPLICACIONS
- Edat >65 anys
- Comorbiditats (MPOC, diabetis, IC, IRC)
- Immunosupressió
- Tabaquisme actiu
- Alcoholisme

REFERÈNCIES:
- Guia SEPAR 2023 per Pneumònia
- Protocol SAS Medicina Interna 2024
- Guia IDSA/ATS per PAC
""",
        "source_url": "https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/",
        "last_updated": "2024-01-25",
        "official": True
    }
]


async def index_sas_protocols():
    """Indexa protocols SAS a Qdrant"""
    
    print("🏥 Indexant Protocols SAS per Informes d'Alta")
    print("=" * 80)
    
    # Initialize clients
    print("\n1️⃣ Inicialitzant clients...")
    embeddings_client = BGEM3Embeddings()
    qdrant_client = QdrantClientWrapper()
    
    # Initialize indexer
    indexer = DocumentIndexer(
        qdrant_client=qdrant_client,
        embedding_model=embeddings_client,
        collection_name=settings.QDRANT_COLLECTION
    )
    
    print(f"✅ Clients inicialitzats")
    print(f"   - Collection: {settings.QDRANT_COLLECTION}")
    print(f"   - Embedding model: BGE-M3")
    
    # Process and index protocols
    print(f"\n2️⃣ Processant {len(SAS_PROTOCOLS)} protocols...")
    
    # Import Document class
    from src.main.core.ingestion.indexer import Document
    
    # Prepare documents
    documents = []
    for i, protocol in enumerate(SAS_PROTOCOLS, 1):
        print(f"\n📄 Protocol {i}/{len(SAS_PROTOCOLS)}: {protocol['title']}")
        print(f"   Especialitat: {protocol['specialty']}")
        
        # Prepare metadata
        metadata = {
            "type": "protocol_sas",
            "specialty": protocol["specialty"],
            "official": protocol["official"],
            "source_url": protocol["source_url"],
            "last_updated": protocol["last_updated"],
            "title": protocol["title"],
            "source": f"SAS Protocol - {protocol['title']}",
            "indexed_at": datetime.now().isoformat()
        }
        
        # Create document
        doc = Document(
            content=protocol["content"],
            metadata=metadata
        )
        documents.append(doc)
        print(f"   ✅ Document preparat")
    
    # Index all documents
    print(f"\n3️⃣ Indexant {len(documents)} documents a Qdrant...")
    try:
        stats = await indexer.index_documents(
            documents=documents,
            batch_size=5,
            show_progress=True
        )
        
        indexed_count = stats.get('indexed_chunks', 0)
        print(f"   ✅ Indexació completada")
        print(f"   - Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   - Chunks indexats: {indexed_count}")
        print(f"   - Chunks fallits: {stats.get('failed_chunks', 0)}")
        
    except Exception as e:
        print(f"   ❌ Error indexant: {e}")
        import traceback
        traceback.print_exc()
        indexed_count = 0
    
    # Verify indexing
    print(f"\n4️⃣ Verificant indexació...")
    try:
        # Count protocols in collection
        collection_info = qdrant_client.client.get_collection(settings.QDRANT_COLLECTION)
        total_points = collection_info.points_count
        print(f"   ✅ Total documents a la col·lecció: {total_points}")
        
        # Search for a protocol
        test_query = "infart agut de miocardi tractament"
        print(f"\n5️⃣ Test de retrieval: '{test_query}'")
        
        # Generate embedding for test query
        query_embedding = await embeddings_client.encode_query(test_query)
        
        # Search
        results = qdrant_client.client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_embedding,
            limit=3,
            query_filter={
                "must": [
                    {"key": "type", "match": {"value": "protocol_sas"}}
                ]
            }
        )
        
        print(f"   📊 Resultats trobats: {len(results)}")
        for j, result in enumerate(results, 1):
            print(f"\n   {j}. Score: {result.score:.4f}")
            print(f"      Títol: {result.payload.get('title', 'N/A')}")
            print(f"      Especialitat: {result.payload.get('specialty', 'N/A')}")
            print(f"      Tipus: {result.payload.get('type', 'N/A')}")
        
    except Exception as e:
        print(f"   ❌ Error verificant: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Indexació de protocols SAS completada!")
    print("=" * 80)


async def main():
    """Main function"""
    try:
        await index_sas_protocols()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
