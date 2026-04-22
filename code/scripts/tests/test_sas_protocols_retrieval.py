#!/usr/bin/env python3
"""
Test retrieval of SAS protocols
Verifica que els protocols SAS s'han indexat correctament i es recuperen adequadament
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from qdrant_client import QdrantClient
from config.settings import settings


async def test_protocol_retrieval():
    """Test retrieval of SAS protocols"""
    
    print("🔍 Test de Retrieval de Protocols SAS")
    print("=" * 80)
    
    # Initialize clients
    print("\n1️⃣ Inicialitzant clients...")
    embeddings_client = BGEM3Embeddings()
    qdrant_client = QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT
    )
    
    print(f"✅ Clients inicialitzats")
    print(f"   - Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    print(f"   - Collection: {settings.QDRANT_COLLECTION}")
    
    # Test queries
    test_queries = [
        "infart agut de miocardi tractament antiagregació",
        "diabetis mellitus descompensada insulina",
        "accident cerebrovascular isquèmic rehabilitació",
        "insuficiència cardíaca diürètics",
        "pneumònia comunitària antibiòtic"
    ]
    
    print(f"\n2️⃣ Testejant {len(test_queries)} queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}/{len(test_queries)}: '{query}'")
        print(f"{'='*80}")
        
        try:
            # Generate embedding
            result = await embeddings_client.encode_query(query)
            query_embedding = result.get('dense', result.get('embedding', []))
            
            # Search in Qdrant
            results = qdrant_client.query_points(
                collection_name=settings.QDRANT_COLLECTION,
                query=query_embedding,
                limit=3,
                score_threshold=0.3
            ).points
            
            print(f"\n📊 Resultats trobats: {len(results)}")
            
            for j, hit in enumerate(results, 1):
                score = hit.score
                payload = hit.payload
                
                print(f"\n  {j}. Score: {score:.4f}")
                print(f"     Títol: {payload.get('title', 'N/A')}")
                print(f"     Tipus: {payload.get('type', 'N/A')}")
                print(f"     Especialitat: {payload.get('specialty', 'N/A')}")
                print(f"     Oficial: {payload.get('official', 'N/A')}")
                print(f"     Font: {payload.get('source', 'N/A')[:80]}...")
                
                # Show snippet of content
                content = payload.get('content', '')
                snippet = content[:200].replace('\n', ' ')
                print(f"     Contingut: {snippet}...")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Test filtering by specialty
    print(f"\n{'='*80}")
    print(f"3️⃣ Test de filtratge per especialitat")
    print(f"{'='*80}")
    
    specialties = ["Cardiologia", "Endocrinologia", "Neurologia"]
    
    for specialty in specialties:
        print(f"\n🏥 Especialitat: {specialty}")
        
        try:
            # Search with filter
            query = "tractament farmacològic"
            result = await embeddings_client.encode_query(query)
            query_embedding = result.get('dense', result.get('embedding', []))
            
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            results = qdrant_client.query_points(
                collection_name=settings.QDRANT_COLLECTION,
                query=query_embedding,
                limit=5,
                query_filter=Filter(
                    must=[
                        FieldCondition(key="type", match=MatchValue(value="protocol_sas")),
                        FieldCondition(key="specialty", match=MatchValue(value=specialty))
                    ]
                )
            ).points
            
            print(f"   📊 Protocols trobats: {len(results)}")
            for hit in results:
                print(f"      - {hit.payload.get('title', 'N/A')} (score: {hit.score:.4f})")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Count total protocols
    print(f"\n{'='*80}")
    print(f"4️⃣ Resum de protocols indexats")
    print(f"{'='*80}")
    
    try:
        # Count by type
        query = "protocol"
        result = await embeddings_client.encode_query(query)
        query_embedding = result.get('dense', result.get('embedding', []))
        
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        results = qdrant_client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_embedding,
            limit=100,
            query_filter=Filter(
                must=[
                    FieldCondition(key="type", match=MatchValue(value="protocol_sas"))
                ]
            )
        ).points
        
        print(f"\n✅ Total protocols SAS indexats: {len(results)}")
        
        # Group by specialty
        by_specialty = {}
        for hit in results:
            spec = hit.payload.get('specialty', 'Unknown')
            by_specialty[spec] = by_specialty.get(spec, 0) + 1
        
        print(f"\n📊 Distribució per especialitat:")
        for spec, count in sorted(by_specialty.items()):
            print(f"   - {spec}: {count} protocol(s)")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*80}")
    print(f"✅ Test de retrieval completat!")
    print(f"{'='*80}")


async def main():
    """Main function"""
    try:
        await test_protocol_retrieval()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
