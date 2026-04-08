"""
Medical specialized chunking for Healthcare RAG system
Implements semantic chunking that respects medical document structure
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    content: str
    start_index: int
    end_index: int
    chunk_type: str
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MedicalChunker:
    """Specialized chunker for medical documents"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Medical section headers patterns
        self.section_patterns = [
            r'^(RESUMEN|ABSTRACT|SUMMARY)$',
            r'^(INTRODUCCIÓN|INTRODUCTION)$',
            r'^(OBJETIVOS?|OBJECTIVES?)$',
            r'^(METODOLOGÍA|METHODOLOGY|MÉTODOS|METHODS)$',
            r'^(RESULTADOS|RESULTS)$',
            r'^(DISCUSIÓN|DISCUSSION)$',
            r'^(CONCLUSIONES?|CONCLUSIONS?)$',
            r'^(REFERENCIAS|REFERENCES|BIBLIOGRAFÍA)$',
            r'^(DIAGNÓSTICO|DIAGNOSIS)$',
            r'^(TRATAMIENTO|TREATMENT)$',
            r'^(PROCEDIMIENTO|PROCEDURE)$',
            r'^(INDICACIONES|INDICATIONS)$',
            r'^(CONTRAINDICACIONES|CONTRAINDICATIONS)$',
            r'^(EFECTOS ADVERSOS|ADVERSE EFFECTS)$',
            r'^(DOSIFICACIÓN|DOSAGE)$'
        ]
        
        # Clinical list patterns
        self.list_patterns = [
            r'^\s*[-•]\s+',  # Bullet points
            r'^\s*\d+[\.\)]\s+',  # Numbered lists
            r'^\s*[a-z][\.\)]\s+',  # Lettered lists
            r'^\s*[IVX]+[\.\)]\s+'  # Roman numerals
        ]
    
    def chunk_document(self, text: str, document_metadata: Dict = None) -> List[Chunk]:
        """Main chunking function for medical documents"""
        if not text.strip():
            return []
        
        # First, try semantic chunking by sections
        semantic_chunks = self._chunk_by_sections(text)
        
        # If no clear sections found, use paragraph-based chunking
        if len(semantic_chunks) <= 1:
            semantic_chunks = self._chunk_by_paragraphs(text)
        
        # Further split large chunks if needed
        final_chunks = []
        for chunk in semantic_chunks:
            if len(chunk.content) > self.chunk_size * 1.5:
                sub_chunks = self._split_large_chunk(chunk)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
        
        # Add document metadata to all chunks
        if document_metadata:
            for chunk in final_chunks:
                chunk.metadata.update(document_metadata)
        
        return final_chunks
    
    def _chunk_by_sections(self, text: str) -> List[Chunk]:
        """Chunk text by medical document sections"""
        chunks = []
        lines = text.split('\n')
        current_section = []
        current_section_type = 'content'
        start_index = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip().upper()
            
            # Check if line is a section header
            is_section_header = any(
                re.match(pattern, line_stripped) 
                for pattern in self.section_patterns
            )
            
            if is_section_header and current_section:
                # Save previous section
                content = '\n'.join(current_section).strip()
                if content:
                    end_index = start_index + len(content)
                    chunks.append(Chunk(
                        content=content,
                        start_index=start_index,
                        end_index=end_index,
                        chunk_type=current_section_type,
                        metadata={'section_header': current_section_type}
                    ))
                    start_index = end_index
                
                # Start new section
                current_section = [line]
                current_section_type = line_stripped.lower()
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            content = '\n'.join(current_section).strip()
            if content:
                chunks.append(Chunk(
                    content=content,
                    start_index=start_index,
                    end_index=start_index + len(content),
                    chunk_type=current_section_type,
                    metadata={'section_header': current_section_type}
                ))
        
        return chunks
    
    def _chunk_by_paragraphs(self, text: str) -> List[Chunk]:
        """Chunk text by paragraphs when no clear sections exist"""
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = []
        current_length = 0
        start_index = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            paragraph_length = len(paragraph)
            
            # If adding this paragraph would exceed chunk size
            if current_length + paragraph_length > self.chunk_size and current_chunk:
                # Save current chunk
                content = '\n\n'.join(current_chunk)
                chunks.append(Chunk(
                    content=content,
                    start_index=start_index,
                    end_index=start_index + len(content),
                    chunk_type='paragraph_group'
                ))
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0:
                    overlap_content = self._get_overlap_content(current_chunk, self.chunk_overlap)
                    current_chunk = [overlap_content, paragraph] if overlap_content else [paragraph]
                    start_index += len(content) - len(overlap_content) if overlap_content else len(content)
                else:
                    current_chunk = [paragraph]
                    start_index += len(content)
                
                current_length = sum(len(p) for p in current_chunk)
            else:
                current_chunk.append(paragraph)
                current_length += paragraph_length
        
        # Add final chunk
        if current_chunk:
            content = '\n\n'.join(current_chunk)
            chunks.append(Chunk(
                content=content,
                start_index=start_index,
                end_index=start_index + len(content),
                chunk_type='paragraph_group'
            ))
        
        return chunks
    
    def _split_large_chunk(self, chunk: Chunk) -> List[Chunk]:
        """Split a large chunk into smaller ones"""
        if len(chunk.content) <= self.chunk_size:
            return [chunk]
        
        # Try to split by sentences first
        sentences = self._split_sentences(chunk.content)
        
        sub_chunks = []
        current_sentences = []
        current_length = 0
        start_index = chunk.start_index
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_sentences:
                # Save current sub-chunk
                content = ' '.join(current_sentences)
                sub_chunks.append(Chunk(
                    content=content,
                    start_index=start_index,
                    end_index=start_index + len(content),
                    chunk_type=f"{chunk.chunk_type}_split",
                    metadata=chunk.metadata.copy()
                ))
                
                # Start new sub-chunk with overlap
                if self.chunk_overlap > 0 and current_sentences:
                    overlap_sentences = self._get_sentence_overlap(current_sentences, self.chunk_overlap)
                    current_sentences = overlap_sentences + [sentence]
                    start_index += len(content) - sum(len(s) for s in overlap_sentences)
                else:
                    current_sentences = [sentence]
                    start_index += len(content)
                
                current_length = sum(len(s) for s in current_sentences)
            else:
                current_sentences.append(sentence)
                current_length += sentence_length
        
        # Add final sub-chunk
        if current_sentences:
            content = ' '.join(current_sentences)
            sub_chunks.append(Chunk(
                content=content,
                start_index=start_index,
                end_index=start_index + len(content),
                chunk_type=f"{chunk.chunk_type}_split",
                metadata=chunk.metadata.copy()
            ))
        
        return sub_chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences, handling medical abbreviations"""
        # Protect medical abbreviations
        protected_text = text
        protection_map = {}
        
        medical_abbrevs = ['Dr.', 'Dra.', 'Prof.', 'mg.', 'ml.', 'kg.', 'cm.', 'mm.']
        for i, abbrev in enumerate(medical_abbrevs):
            placeholder = f"__ABBREV_{i}__"
            protected_text = protected_text.replace(abbrev, placeholder)
            protection_map[placeholder] = abbrev
        
        # Split sentences
        sentences = re.split(r'[.!?]+\s+', protected_text)
        
        # Restore abbreviations
        for i, sentence in enumerate(sentences):
            for placeholder, abbrev in protection_map.items():
                sentence = sentence.replace(placeholder, abbrev)
            sentences[i] = sentence.strip()
        
        return [s for s in sentences if s]
    
    def _get_overlap_content(self, chunks: List[str], overlap_size: int) -> str:
        """Get overlap content from previous chunks"""
        if not chunks:
            return ""
        
        # Take last chunk and truncate to overlap size
        last_chunk = chunks[-1]
        if len(last_chunk) <= overlap_size:
            return last_chunk
        
        # Try to break at sentence boundary
        sentences = self._split_sentences(last_chunk)
        overlap_content = ""
        
        for sentence in reversed(sentences):
            if len(overlap_content + sentence) <= overlap_size:
                overlap_content = sentence + " " + overlap_content
            else:
                break
        
        return overlap_content.strip()
    
    def _get_sentence_overlap(self, sentences: List[str], overlap_size: int) -> List[str]:
        """Get overlap sentences"""
        if not sentences:
            return []
        
        overlap_sentences = []
        current_length = 0
        
        for sentence in reversed(sentences):
            if current_length + len(sentence) <= overlap_size:
                overlap_sentences.insert(0, sentence)
                current_length += len(sentence)
            else:
                break
        
        return overlap_sentences
    
    def get_chunk_statistics(self, chunks: List[Chunk]) -> Dict:
        """Get statistics about the chunks"""
        if not chunks:
            return {}
        
        chunk_lengths = [len(chunk.content) for chunk in chunks]
        chunk_types = [chunk.chunk_type for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'avg_chunk_length': sum(chunk_lengths) / len(chunk_lengths),
            'min_chunk_length': min(chunk_lengths),
            'max_chunk_length': max(chunk_lengths),
            'chunk_types': list(set(chunk_types)),
            'type_distribution': {t: chunk_types.count(t) for t in set(chunk_types)}
        }
