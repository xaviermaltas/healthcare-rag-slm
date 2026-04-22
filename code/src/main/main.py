"""
Main FastAPI application for Healthcare RAG system
Provides REST API endpoints for medical document retrieval and generation
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any

from config.settings import get_settings
from src.main.api.routes import health, query, documents, collections, models, admin, ontology, discharge_summary
from src.main.api.dependencies import get_ollama_client, get_qdrant_client, get_embeddings_model, get_snomed_client
from src.main.api.middleware import setup_logging_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Healthcare RAG API...")
    
    # Initialize core components
    try:
        # Initialize Ollama client
        ollama_client = await get_ollama_client()
        if not await ollama_client.health_check():
            logger.warning("Ollama client health check failed")
        
        # Initialize Qdrant client
        qdrant_client = await get_qdrant_client()
        if not await qdrant_client.health_check():
            logger.warning("Qdrant client health check failed")
        
        # Initialize Embeddings model
        try:
            embeddings_model = await get_embeddings_model()
            if await embeddings_model.health_check():
                logger.info("Embeddings model initialized successfully")
            else:
                logger.warning("Embeddings model health check failed")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings model: {e}")
        
        # Initialize SNOMED CT client (optional)
        try:
            if settings.BIOPORTAL_API_KEY:
                snomed_client = await get_snomed_client()
                logger.info("SNOMED CT client initialized successfully")
            else:
                logger.info("SNOMED CT disabled (no API key)")
        except Exception as e:
            logger.warning(f"SNOMED CT client initialization failed: {e}")
        
        logger.info("Healthcare RAG API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Healthcare RAG API...")
    try:
        ollama_client = await get_ollama_client()
        await ollama_client.close()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Healthcare RAG System API for Junta de Andalucía",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging middleware
setup_logging_middleware(app)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(ontology.router, prefix="/ontology", tags=["Ontology"])
app.include_router(collections.router, prefix="/collections", tags=["Collections"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(discharge_summary.router, tags=["Generation"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Healthcare RAG System API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs_url": "/docs" if settings.DEBUG else None
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": str(asyncio.get_event_loop().time())
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": str(asyncio.get_event_loop().time())
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower()
    )
