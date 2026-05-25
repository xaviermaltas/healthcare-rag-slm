"""
Healthcare RAG System Configuration
Centralized configuration management for all system components
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Main configuration class for Healthcare RAG system"""
    
    # Application settings
    APP_NAME: str = "Healthcare RAG System"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API settings
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=1, env="API_WORKERS")
    
    # Ollama settings
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    OLLAMA_MODEL: str = Field(default="llama3.2", env="OLLAMA_MODEL")
    OLLAMA_TIMEOUT: int = Field(default=60, env="OLLAMA_TIMEOUT")
    
    # Qdrant settings
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")
    QDRANT_COLLECTION: str = Field(default="healthcare_rag", env="QDRANT_COLLECTION")
    QDRANT_VECTOR_SIZE: int = Field(default=1024, env="QDRANT_VECTOR_SIZE")
    
    # Embeddings settings
    EMBEDDING_MODEL: str = Field(default="BAAI/bge-m3", env="EMBEDDING_MODEL")
    EMBEDDING_DEVICE: str = Field(default="cpu", env="EMBEDDING_DEVICE")
    EMBEDDING_BATCH_SIZE: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")
    
    # BioPortal API settings
    BIOPORTAL_API_KEY: str = Field(default="", env="BIOPORTAL_API_KEY")
    BIOPORTAL_BASE_URL: str = Field(default="https://data.bioontology.org", env="BIOPORTAL_BASE_URL")
    
    # SNOMED CT settings
    SNOMED_MIN_CONFIDENCE: float = Field(default=0.5, env="SNOMED_MIN_CONFIDENCE")
    SNOMED_ENABLE_QUERY_EXPANSION: bool = Field(default=True, env="SNOMED_ENABLE_QUERY_EXPANSION")
    
    # MedlinePlus API settings
    MEDLINEPLUS_BASE_URL: str = Field(default="https://wsearch.nlm.nih.gov/ws/query", env="MEDLINEPLUS_BASE_URL")
    
    # Chunking settings
    CHUNK_SIZE: int = Field(default=512, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=50, env="CHUNK_OVERLAP")
    
    # Retrieval settings
    RETRIEVAL_TOP_K: int = Field(default=10, env="RETRIEVAL_TOP_K")
    RERANK_TOP_K: int = Field(default=5, env="RERANK_TOP_K")
    
    # Generation settings
    GENERATION_MAX_TOKENS: int = Field(default=1000, env="GENERATION_MAX_TOKENS")
    GENERATION_TEMPERATURE: float = Field(default=0.7, env="GENERATION_TEMPERATURE")
    
    # Data paths
    DATA_DIR: Path = Field(default=Path("data"), env="DATA_DIR")
    RAW_DATA_DIR: Path = Field(default=Path("data/raw"), env="RAW_DATA_DIR")
    PROCESSED_DATA_DIR: Path = Field(default=Path("data/processed"), env="PROCESSED_DATA_DIR")
    EMBEDDINGS_CACHE_DIR: Path = Field(default=Path("data/embeddings"), env="EMBEDDINGS_CACHE_DIR")
    
    # Ontology files
    SNOMED_CT_FILE: Path = Field(default=Path("config/ontologies/snomed_ct.json"))
    ICD10_FILE: Path = Field(default=Path("config/ontologies/icd10.json"))
    MESH_FILE: Path = Field(default=Path("config/ontologies/mesh.json"))
    
    # Supported languages
    SUPPORTED_LANGUAGES: List[str] = Field(default=["es", "ca", "en"])
    DEFAULT_LANGUAGE: str = Field(default="es", env="DEFAULT_LANGUAGE")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings


def get_data_path(relative_path: str) -> Path:
    """Get absolute path for data files"""
    return Path(settings.DATA_DIR) / relative_path


def get_ontology_path(ontology_name: str) -> Path:
    """Get path for ontology files"""
    ontology_files = {
        "snomed": settings.SNOMED_CT_FILE,
        "icd10": settings.ICD10_FILE,
        "mesh": settings.MESH_FILE
    }
    return ontology_files.get(ontology_name.lower(), Path(""))
