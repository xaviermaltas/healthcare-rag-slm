"""
PubMed connector for Healthcare RAG system
Fetches medical articles from PubMed with citation and date filtering
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import logging
from .base_connector import BaseConnector, Document

logger = logging.getLogger(__name__)


class PubMedConnector(BaseConnector):
    """
    Connector for PubMed articles
    
    Features:
    - Search by query with filters
    - Filter by citation count (highly cited papers)
    - Filter by publication date (recent vs classic)
    - Fetch full abstracts and metadata
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
        self.email = self.config.get('email', '')  # NCBI requires email for API usage
        self.api_key = self.config.get('api_key', '')  # Optional, increases rate limit
        self.session = None
        
        # Rate limiting
        self.rate_limit = 10 if self.api_key else 3  # requests per second
        self.last_request_time = 0
        
    async def connect(self) -> bool:
        """Establish connection to PubMed API"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Test connection
            params = {
                'db': 'pubmed',
                'term': 'diabetes',
                'retmax': 1,
                'email': self.email
            }
            if self.api_key:
                params['api_key'] = self.api_key
            
            async with self.session.get(f"{self.base_url}/esearch.fcgi", params=params) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Failed to connect to PubMed: {e}")
            return False
    
    async def fetch_documents(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = 10,
        min_citations: Optional[int] = None,
        date_range: Optional[str] = None,
        sort_by: str = 'relevance'
    ) -> Iterator[Document]:
        """
        Fetch articles from PubMed
        
        Args:
            query: Search query (e.g., "diabetes mellitus type 2")
            limit: Maximum number of articles
            min_citations: Minimum citation count (None for all)
            date_range: Date filter options:
                - 'recent': Last 2 years
                - 'classic': >10 years old with high citations
                - 'YYYY/MM/DD:YYYY/MM/DD': Custom date range
                - None: All dates
            sort_by: Sort order ('relevance', 'pub_date', 'citations')
            
        Yields:
            Document objects with article data
        """
        if not self.session:
            await self.connect()
        
        if not query:
            query = "diabetes mellitus"
        
        try:
            # Step 1: Search for article IDs
            pmids = await self._search_pubmed(query, limit, date_range, sort_by)
            
            if not pmids:
                logger.warning(f"No articles found for query: {query}")
                return
            
            logger.info(f"Found {len(pmids)} articles for query: {query}")
            
            # Step 2: Fetch article details in batches
            batch_size = 200  # PubMed allows up to 200 IDs per request
            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i + batch_size]
                articles = await self._fetch_article_details(batch_pmids)
                
                for article in articles:
                    # Filter by citations if specified
                    if min_citations is not None:
                        citation_count = article.metadata.get('citation_count', 0)
                        if citation_count < min_citations:
                            continue
                    
                    yield article
                    
        except Exception as e:
            logger.error(f"Error fetching from PubMed: {e}")
    
    async def _search_pubmed(
        self,
        query: str,
        limit: int,
        date_range: Optional[str],
        sort_by: str
    ) -> List[str]:
        """Search PubMed and return list of PMIDs"""
        await self._rate_limit()
        
        # Build search query with filters
        search_term = query
        
        # Add date filter
        if date_range:
            if date_range == 'recent':
                # Last 2 years
                end_date = datetime.now()
                start_date = end_date - timedelta(days=730)
                search_term += f' AND ("{start_date.strftime("%Y/%m/%d")}"[Date - Publication] : "{end_date.strftime("%Y/%m/%d")}"[Date - Publication])'
            
            elif date_range == 'classic':
                # >10 years old
                end_date = datetime.now() - timedelta(days=3650)
                search_term += f' AND ("1900/01/01"[Date - Publication] : "{end_date.strftime("%Y/%m/%d")}"[Date - Publication])'
            
            elif ':' in date_range:
                # Custom range
                search_term += f' AND ("{date_range}"[Date - Publication])'
        
        # Map sort_by to PubMed sort parameter
        sort_param = {
            'relevance': 'relevance',
            'pub_date': 'pub+date',
            'citations': 'pub+date'  # PubMed doesn't support citation sort directly
        }.get(sort_by, 'relevance')
        
        params = {
            'db': 'pubmed',
            'term': search_term,
            'retmax': limit,
            'retmode': 'json',
            'sort': sort_param,
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        try:
            async with self.session.get(f"{self.base_url}/esearch.fcgi", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    pmids = data.get('esearchresult', {}).get('idlist', [])
                    return pmids
                else:
                    logger.error(f"PubMed search failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error in PubMed search: {e}")
            return []
    
    async def _fetch_article_details(self, pmids: List[str]) -> List[Document]:
        """Fetch detailed article information for given PMIDs"""
        await self._rate_limit()
        
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml',
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        try:
            async with self.session.get(f"{self.base_url}/efetch.fcgi", params=params) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    return await self._parse_pubmed_xml(xml_data)
                else:
                    logger.error(f"PubMed fetch failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching article details: {e}")
            return []
    
    async def _parse_pubmed_xml(self, xml_data: str) -> List[Document]:
        """Parse PubMed XML response into Document objects"""
        documents = []
        
        try:
            root = ET.fromstring(xml_data)
            
            for article in root.findall('.//PubmedArticle'):
                try:
                    # Extract PMID
                    pmid_elem = article.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else ''
                    
                    # Extract title
                    title_elem = article.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else ''
                    
                    # Extract abstract
                    abstract_texts = article.findall('.//AbstractText')
                    abstract = ' '.join([
                        (elem.text or '') for elem in abstract_texts
                    ])
                    
                    # Extract authors
                    authors = []
                    for author in article.findall('.//Author'):
                        last_name = author.find('LastName')
                        fore_name = author.find('ForeName')
                        if last_name is not None and fore_name is not None:
                            authors.append(f"{fore_name.text} {last_name.text}")
                    
                    # Extract publication date
                    pub_date = article.find('.//PubDate')
                    year = pub_date.find('Year').text if pub_date is not None and pub_date.find('Year') is not None else ''
                    month = pub_date.find('Month').text if pub_date is not None and pub_date.find('Month') is not None else '01'
                    day = pub_date.find('Day').text if pub_date is not None and pub_date.find('Day') is not None else '01'
                    pub_date_str = f"{year}-{month}-{day}" if year else ''
                    
                    # Extract journal
                    journal_elem = article.find('.//Journal/Title')
                    journal = journal_elem.text if journal_elem is not None else ''
                    
                    # Extract MeSH terms
                    mesh_terms = []
                    for mesh in article.findall('.//MeshHeading/DescriptorName'):
                        if mesh.text:
                            mesh_terms.append(mesh.text)
                    
                    # Extract DOI
                    doi = ''
                    for article_id in article.findall('.//ArticleId'):
                        if article_id.get('IdType') == 'doi':
                            doi = article_id.text
                            break
                    
                    # Get citation count (requires additional API call to PubMed Central)
                    citation_count = await self._get_citation_count(pmid)
                    
                    # Build content
                    content = f"{title}\n\n{abstract}"
                    
                    # Build metadata
                    metadata = {
                        'pmid': pmid,
                        'title': title,
                        'abstract': abstract,
                        'authors': authors,
                        'publication_date': pub_date_str,
                        'journal': journal,
                        'mesh_terms': mesh_terms,
                        'doi': doi,
                        'citation_count': citation_count,
                        'source_type': 'pubmed',
                        'url': f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'
                    }
                    
                    documents.append(Document(
                        id=f"pubmed_{pmid}",
                        source='pubmed',
                        language='en',
                        content=content,
                        metadata=metadata
                    ))
                    
                except Exception as e:
                    logger.error(f"Error parsing article: {e}")
                    continue
            
            logger.info(f"Parsed {len(documents)} articles from XML")
            return documents
            
        except Exception as e:
            logger.error(f"Error parsing PubMed XML: {e}")
            return []
    
    async def _get_citation_count(self, pmid: str) -> int:
        """
        Get citation count for a PMID
        Uses PubMed Central (PMC) citation data
        """
        try:
            await self._rate_limit()
            
            params = {
                'db': 'pubmed',
                'linkname': 'pubmed_pubmed_citedin',
                'id': pmid,
                'retmode': 'json',
                'email': self.email
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            async with self.session.get(f"{self.base_url}/elink.fcgi", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    linksets = data.get('linksets', [])
                    if linksets and 'linksetdbs' in linksets[0]:
                        for linksetdb in linksets[0]['linksetdbs']:
                            if linksetdb.get('linkname') == 'pubmed_pubmed_citedin':
                                return len(linksetdb.get('links', []))
                    return 0
                else:
                    return 0
                    
        except Exception as e:
            logger.debug(f"Could not fetch citation count for {pmid}: {e}")
            return 0
    
    async def _rate_limit(self):
        """Implement rate limiting for PubMed API"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        self.last_request_time = asyncio.get_event_loop().time()
    
    async def fetch_highly_cited_articles(
        self,
        query: str,
        min_citations: int = 100,
        limit: int = 50
    ) -> Iterator[Document]:
        """
        Fetch highly cited articles (classic papers)
        
        Args:
            query: Search query
            min_citations: Minimum citation threshold
            limit: Maximum articles to fetch
            
        Yields:
            Highly cited articles
        """
        # Fetch older articles (more time to accumulate citations)
        async for doc in self.fetch_documents(
            query=query,
            limit=limit * 2,  # Fetch more to filter by citations
            date_range='classic',
            sort_by='pub_date'
        ):
            if doc.metadata.get('citation_count', 0) >= min_citations:
                yield doc
    
    async def fetch_recent_articles(
        self,
        query: str,
        limit: int = 50
    ) -> Iterator[Document]:
        """
        Fetch recent articles (last 2 years)
        
        Args:
            query: Search query
            limit: Maximum articles
            
        Yields:
            Recent articles
        """
        async for doc in self.fetch_documents(
            query=query,
            limit=limit,
            date_range='recent',
            sort_by='pub_date'
        ):
            yield doc
    
    async def disconnect(self) -> None:
        """Close connection to PubMed API"""
        if self.session:
            await self.session.close()
            self.session = None
