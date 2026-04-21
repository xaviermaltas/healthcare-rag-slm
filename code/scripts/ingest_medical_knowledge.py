#!/usr/bin/env python3
"""
Medical Knowledge Ingestion Script
Populates the RAG system with:
1. Ontology concepts (SNOMED CT, MeSH, ICD-10)
2. PubMed articles (highly cited + recent)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main.core.ingestion.connectors.pubmed_connector import PubMedConnector
from src.main.core.ingestion.indexer import DocumentIndexer, Document
from src.main.infrastructure.ontologies.ontology_manager import OntologyManager, OntologyType
from src.main.infrastructure.vector_db.qdrant_client import QdrantClient
from src.main.infrastructure.embeddings.bge_m3 import BGEM3Embeddings
from config.settings import get_settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Medical topics to ingest
MEDICAL_TOPICS = [
    "diabetes mellitus type 2",
    "hypertension",
    "heart failure",
    "chronic kidney disease",
    "asthma",
    "COPD",
    "depression",
    "anxiety disorder",
    "stroke",
    "myocardial infarction"
]


async def ingest_ontology_concepts(
    ontology_manager: OntologyManager,
    indexer: DocumentIndexer,
    topics: list[str],
    concepts_per_topic: int = 50
) -> int:
    """
    Ingest ontology concepts for medical topics
    
    Args:
        ontology_manager: OntologyManager instance
        indexer: DocumentIndexer instance
        topics: List of medical topics
        concepts_per_topic: Concepts to fetch per topic
    """
    logger.info("=" * 60)
    logger.info("INGESTING ONTOLOGY CONCEPTS")
    logger.info("=" * 60)
    
    total_concepts = 0
    
    for topic in topics:
        logger.info(f"\n📚 Processing topic: {topic}")
        
        # Search across all ontologies
        concepts = await ontology_manager.search_concepts(
            query=topic,
            ontologies=[OntologyType.SNOMED_CT, OntologyType.MESH, OntologyType.ICD10],
            limit=concepts_per_topic
        )
        
        logger.info(f"  ✓ Found {len(concepts)} concepts")
        
        # Group by ontology
        by_ontology = {}
        for concept in concepts:
            ont = concept.ontology.value
            if ont not in by_ontology:
                by_ontology[ont] = []
            by_ontology[ont].append(concept)
        
        for ont, ont_concepts in by_ontology.items():
            logger.info(f"    - {ont}: {len(ont_concepts)} concepts")
        
        total_concepts += len(concepts)
        
        # Convert concepts to Documents for indexing
        documents = []
        for concept in concepts:
            # Format concept as document
            content = f"{concept.pref_label}\n\n"
            if concept.definition:
                content += f"Definition: {concept.definition}\n\n"
            if concept.synonyms:
                content += f"Synonyms: {', '.join(concept.synonyms[:5])}\n\n"
            
            doc = Document(
                content=content.strip(),
                metadata={
                    'type': 'ontology_concept',
                    'ontology': concept.ontology.value,
                    'concept_id': concept.concept_id,
                    'pref_label': concept.pref_label,
                    'topic': topic,
                    'source': 'bioportal'
                }
            )
            documents.append(doc)
        
        # Index to Qdrant
        if documents:
            stats = await indexer.index_documents(documents, show_progress=False)
            logger.info(f"  ✓ Indexed {stats['indexed_chunks']} chunks")
    
    logger.info(f"\n✅ Total concepts ingested: {total_concepts}")
    return total_concepts


async def ingest_pubmed_articles(
    pubmed_connector: PubMedConnector,
    indexer: DocumentIndexer,
    topics: list[str],
    articles_per_topic: int = 20
) -> int:
    """
    Ingest PubMed articles for medical topics
    
    Args:
        pubmed_connector: PubMedConnector instance
        indexer: DocumentIndexer instance
        topics: List of medical topics
        articles_per_topic: Articles to fetch per topic
    """
    logger.info("\n" + "=" * 60)
    logger.info("INGESTING PUBMED ARTICLES")
    logger.info("=" * 60)
    
    total_articles = 0
    
    for topic in topics:
        logger.info(f"\n📄 Processing topic: {topic}")
        
        # Fetch highly cited articles (classic papers)
        logger.info("  Fetching highly cited articles...")
        highly_cited = []
        async for doc in pubmed_connector.fetch_highly_cited_articles(
            query=topic,
            min_citations=50,
            limit=articles_per_topic // 2
        ):
            highly_cited.append(doc)
        
        logger.info(f"    ✓ Found {len(highly_cited)} highly cited articles")
        
        # Fetch recent articles
        logger.info("  Fetching recent articles...")
        recent = []
        async for doc in pubmed_connector.fetch_recent_articles(
            query=topic,
            limit=articles_per_topic // 2
        ):
            recent.append(doc)
        
        logger.info(f"    ✓ Found {len(recent)} recent articles")
        
        # Show sample
        if highly_cited:
            sample = highly_cited[0]
            logger.info(f"\n  📋 Sample highly cited article:")
            logger.info(f"    Title: {sample.metadata.get('title', '')[:80]}...")
            logger.info(f"    Citations: {sample.metadata.get('citation_count', 0)}")
            logger.info(f"    Date: {sample.metadata.get('publication_date', '')}")
        
        if recent:
            sample = recent[0]
            logger.info(f"\n  📋 Sample recent article:")
            logger.info(f"    Title: {sample.metadata.get('title', '')[:80]}...")
            logger.info(f"    Date: {sample.metadata.get('publication_date', '')}")
        
        total_articles += len(highly_cited) + len(recent)
        
        # Convert articles to Documents for indexing
        documents = []
        for article in highly_cited + recent:
            doc = Document(
                content=article.content,
                metadata={
                    'type': 'pubmed_article',
                    'topic': topic,
                    'source': 'pubmed',
                    **article.metadata
                }
            )
            documents.append(doc)
        
        # Index to Qdrant
        if documents:
            stats = await indexer.index_documents(documents, show_progress=False)
            logger.info(f"  ✓ Indexed {stats['indexed_chunks']} chunks")
    
    logger.info(f"\n✅ Total articles ingested: {total_articles}")
    return total_articles


async def get_ontology_stats(ontology_manager: OntologyManager):
    """Display statistics about available ontologies"""
    logger.info("\n" + "=" * 60)
    logger.info("ONTOLOGY STATISTICS")
    logger.info("=" * 60)
    
    stats = await ontology_manager.get_ontology_stats()
    
    for ontology, data in stats.items():
        if 'error' in data:
            logger.error(f"\n❌ {ontology}: {data['error']}")
        else:
            logger.info(f"\n📊 {ontology}:")
            logger.info(f"  Name: {data.get('name', 'N/A')}")
            logger.info(f"  Version: {data.get('version', 'N/A')}")
            logger.info(f"  Classes: {data.get('num_classes', 0):,}")
            logger.info(f"  Description: {data.get('description', 'N/A')[:100]}...")


async def main():
    """Main ingestion workflow"""
    settings = get_settings()
    
    logger.info("🚀 Starting Medical Knowledge Ingestion")
    logger.info(f"Topics to process: {len(MEDICAL_TOPICS)}")
    
    # Check API keys
    if not settings.BIOPORTAL_API_KEY:
        logger.error("❌ BIOPORTAL_API_KEY not set in environment")
        logger.info("Please set it in .env file:")
        logger.info("  BIOPORTAL_API_KEY=your-api-key-here")
        return
    
    # Initialize connectors
    logger.info("\n🔌 Initializing connectors...")
    
    # Ontology Manager
    ontology_manager = OntologyManager(
        api_key=settings.BIOPORTAL_API_KEY,
        base_url=settings.BIOPORTAL_BASE_URL
    )
    
    if not await ontology_manager.initialize():
        logger.error("❌ Failed to initialize OntologyManager")
        return
    
    logger.info("  ✓ OntologyManager initialized")
    
    # PubMed Connector
    pubmed_connector = PubMedConnector(config={
        'email': 'healthcare-rag@example.com',  # Replace with your email
        'api_key': ''  # Optional: Add NCBI API key for higher rate limits
    })
    
    if not await pubmed_connector.connect():
        logger.error("❌ Failed to connect to PubMed")
        return
    
    logger.info("  ✓ PubMed connector initialized")
    
    # Initialize Qdrant and Embeddings
    logger.info("\n🔌 Initializing Qdrant and embeddings...")
    
    qdrant_client = QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT
    )
    
    embedding_model = BGEM3Embeddings(
        model_name=settings.EMBEDDING_MODEL,
        device=settings.EMBEDDING_DEVICE
    )
    
    # Initialize indexer
    indexer = DocumentIndexer(
        qdrant_client=qdrant_client,
        embedding_model=embedding_model,
        collection_name=settings.QDRANT_COLLECTION,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    
    logger.info("  ✓ Indexer initialized")
    
    try:
        # Show ontology statistics
        await get_ontology_stats(ontology_manager)
        
        # Ingest ontology concepts
        concepts_count = await ingest_ontology_concepts(
            ontology_manager=ontology_manager,
            indexer=indexer,
            topics=MEDICAL_TOPICS,
            concepts_per_topic=50
        )
        
        # Ingest PubMed articles
        articles_count = await ingest_pubmed_articles(
            pubmed_connector=pubmed_connector,
            indexer=indexer,
            topics=MEDICAL_TOPICS,
            articles_per_topic=20
        )
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("INGESTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"✅ Ontology concepts: {concepts_count}")
        logger.info(f"✅ PubMed articles: {articles_count}")
        logger.info(f"✅ Total documents: {concepts_count + articles_count}")
        
    finally:
        # Cleanup
        await ontology_manager.close()
        await pubmed_connector.disconnect()
        logger.info("\n🔌 Connections closed")


if __name__ == "__main__":
    asyncio.run(main())
