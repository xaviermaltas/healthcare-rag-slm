"""
Ollama client for Healthcare RAG system
Handles communication with local Ollama models for text generation
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, AsyncGenerator
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama models"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:11434",
                 model: str = "mistral",
                 timeout: int = 60):
        
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.session = None
        
    async def initialize(self) -> bool:
        """Initialize Ollama client and check connection"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            
            # Test connection
            return await self.health_check()
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            if not self.session:
                await self.initialize()
            
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            if not self.session:
                await self.initialize()
            
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('models', [])
                else:
                    logger.error(f"Failed to get models: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    async def generate(self, 
                      prompt: str,
                      model: Optional[str] = None,
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: int = 1000,
                      stream: bool = False) -> Dict[str, Any]:
        """Generate text using Ollama model"""
        
        if not self.session:
            await self.initialize()
        
        model_name = model or self.model
        
        # Prepare request payload
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "stop": ["</s>", "[/INST]"]  # Common stop tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                
                if response.status == 200:
                    if stream:
                        return await self._handle_streaming_response(response)
                    else:
                        result = await response.json()
                        return {
                            "response": result.get("response", ""),
                            "model": model_name,
                            "done": result.get("done", True),
                            "total_duration": result.get("total_duration", 0),
                            "load_duration": result.get("load_duration", 0),
                            "prompt_eval_count": result.get("prompt_eval_count", 0),
                            "eval_count": result.get("eval_count", 0)
                        }
                else:
                    error_text = await response.text()
                    logger.error(f"Ollama generation failed: HTTP {response.status} - {error_text}")
                    return {"error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            logger.error(f"Error during text generation: {e}")
            return {"error": str(e)}
    
    async def _handle_streaming_response(self, response) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle streaming response from Ollama"""
        async for line in response.content:
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    yield chunk
                except json.JSONDecodeError:
                    continue
    
    async def chat(self, 
                   messages: List[Dict[str, str]],
                   model: Optional[str] = None,
                   temperature: float = 0.7,
                   max_tokens: int = 1000) -> Dict[str, Any]:
        """Chat with model using conversation format"""
        
        if not self.session:
            await self.initialize()
        
        model_name = model or self.model
        
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "message": result.get("message", {}),
                        "model": model_name,
                        "done": result.get("done", True),
                        "total_duration": result.get("total_duration", 0),
                        "eval_count": result.get("eval_count", 0)
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Ollama chat failed: HTTP {response.status} - {error_text}")
                    return {"error": f"HTTP {response.status}: {error_text}"}
                    
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            return {"error": str(e)}
    
    async def generate_medical_response(self,
                                      query: str,
                                      context_documents: List[Dict[str, Any]],
                                      system_prompt: Optional[str] = None,
                                      temperature: float = 0.7,
                                      max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate medical response using RAG context"""
        
        # Build context from retrieved documents
        context_text = self._build_context_from_documents(context_documents)
        
        # Default medical system prompt if none provided
        if not system_prompt:
            system_prompt = """Eres un asistente médico especializado que ayuda a profesionales sanitarios de la Junta de Andalucía. 

Instrucciones:
- Responde basándote únicamente en la información médica proporcionada en el contexto
- Si no tienes información suficiente, indícalo claramente
- Usa terminología médica precisa pero comprensible
- Incluye referencias a las fuentes cuando sea relevante
- Responde en español
- No proporciones diagnósticos definitivos, solo información orientativa"""
        
        # Build the complete prompt
        full_prompt = f"""Contexto médico:
{context_text}

Pregunta: {query}

Respuesta basada en el contexto proporcionado:"""
        
        result = await self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Add context metadata to result
        if "error" not in result:
            result["context_sources"] = [
                {
                    "source": doc.get("source", ""),
                    "title": doc.get("metadata", {}).get("title", ""),
                    "relevance_score": doc.get("score", 0.0)
                }
                for doc in context_documents
            ]
            result["context_length"] = len(context_text)
        
        return result
    
    def _build_context_from_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Build context text from retrieved documents"""
        if not documents:
            return "No se encontró información relevante en la base de datos médica."
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            source = doc.get("source", "documento")
            title = doc.get("metadata", {}).get("title", "")
            
            # Format document for context
            doc_text = f"[Fuente {i} - {source}"
            if title:
                doc_text += f" - {title}"
            doc_text += f"]:\n{content}\n"
            
            context_parts.append(doc_text)
        
        return "\n".join(context_parts)
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull/download a model"""
        try:
            if not self.session:
                await self.initialize()
            
            payload = {"name": model_name}
            
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json=payload
            ) as response:
                
                if response.status == 200:
                    # Handle streaming response for pull progress
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line.decode('utf-8'))
                                if chunk.get("status") == "success":
                                    logger.info(f"Successfully pulled model: {model_name}")
                                    return True
                            except json.JSONDecodeError:
                                continue
                    return True
                else:
                    logger.error(f"Failed to pull model {model_name}: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model"""
        try:
            if not self.session:
                await self.initialize()
            
            payload = {"name": model_name}
            
            async with self.session.delete(
                f"{self.base_url}/api/delete",
                json=payload
            ) as response:
                
                if response.status == 200:
                    logger.info(f"Successfully deleted model: {model_name}")
                    return True
                else:
                    logger.error(f"Failed to delete model {model_name}: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting model {model_name}: {e}")
            return False
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
            self.session = None
