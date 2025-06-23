"""
ArXiv论文爬取模块
"""
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import arxiv
from loguru import logger
from config.settings import settings


@dataclass
class PaperMetadata:
    """论文元数据"""
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: datetime
    updated_date: datetime
    pdf_url: str
    summary: str


class ArXivCrawler:
    """ArXiv论文爬取器"""
    
    def __init__(self):
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=settings.CRAWL_DELAY,
            num_retries=settings.MAX_RETRIES
        )
        self.papers_dir = settings.DATA_DIR / "papers"
        self.papers_dir.mkdir(parents=True, exist_ok=True)
    
    def search_papers(self, query: str, max_results: int = None) -> List[PaperMetadata]:
        """
        搜索ArXiv论文
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            论文元数据列表
        """
        if max_results is None:
            max_results = int(settings.ARXIV_MAX_RESULTS)
        else:
            max_results = int(max_results)
            
        logger.info(f"开始搜索ArXiv论文，查询: {query}")
        
        try:
            # 构建搜索查询 - 移除排序参数避免API错误
            search = arxiv.Search(
                query=query,
                max_results=max_results
            )
            
            papers = []
            for result in self.client.results(search):
                paper = PaperMetadata(
                    arxiv_id=result.entry_id.split('/')[-1],
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    categories=result.categories,
                    published_date=result.published,
                    updated_date=result.updated,
                    pdf_url=result.pdf_url,
                    summary=result.summary
                )
                papers.append(paper)
                logger.debug(f"找到论文: {paper.title}")
            
            logger.info(f"搜索完成，共找到 {len(papers)} 篇论文")
            return papers
            
        except Exception as e:
            logger.error(f"搜索论文时发生错误: {e}")
            raise
    
    def download_paper(self, paper: PaperMetadata) -> Optional[Path]:
        """
        下载论文PDF
        
        Args:
            paper: 论文元数据
            
        Returns:
            下载的文件路径，如果失败返回None
        """
        try:
            # 构建文件名
            safe_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{paper.arxiv_id}_{safe_title[:50]}.pdf"
            filepath = self.papers_dir / filename
            
            # 检查文件是否已存在
            if filepath.exists():
                logger.info(f"论文已存在: {filename}")
                return filepath
            
            # 用 arxiv 包下载 PDF
            logger.info(f"开始下载论文: {paper.title}")
            search = arxiv.Search(id_list=[paper.arxiv_id])
            result = next(self.client.results(search))
            result.download_pdf(dirpath=str(self.papers_dir), filename=filename)
            logger.info(f"论文下载完成: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"下载论文失败 {paper.arxiv_id}: {e}")
            return None
    
    def download_papers(self, papers: List[PaperMetadata]) -> List[Path]:
        """
        批量下载论文
        
        Args:
            papers: 论文元数据列表
            
        Returns:
            成功下载的文件路径列表
        """
        logger.info(f"开始批量下载 {len(papers)} 篇论文")
        
        downloaded_files = []
        for i, paper in enumerate(papers, 1):
            logger.info(f"下载进度: {i}/{len(papers)}")
            
            filepath = self.download_paper(paper)
            if filepath:
                downloaded_files.append(filepath)
            
            # 添加延迟避免请求过快
            time.sleep(settings.CRAWL_DELAY)
        
        logger.info(f"批量下载完成，成功下载 {len(downloaded_files)} 篇论文")
        return downloaded_files
    
    def get_paper_info(self, arxiv_id: str) -> Optional[PaperMetadata]:
        """
        获取单篇论文信息
        
        Args:
            arxiv_id: ArXiv ID
            
        Returns:
            论文元数据
        """
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(self.client.results(search))
            
            return PaperMetadata(
                arxiv_id=result.entry_id.split('/')[-1],
                title=result.title,
                authors=[author.name for author in result.authors],
                abstract=result.summary,
                categories=result.categories,
                published_date=result.published,
                updated_date=result.updated,
                pdf_url=result.pdf_url,
                summary=result.summary
            )
            
        except Exception as e:
            logger.error(f"获取论文信息失败 {arxiv_id}: {e}")
            return None
    
    def search_by_category(self, category: str, max_results: int = None) -> List[PaperMetadata]:
        """
        按类别搜索论文
        
        Args:
            category: 论文类别（如 cs.AI, cs.LG等）
            max_results: 最大结果数量
            
        Returns:
            论文元数据列表
        """
        query = f"cat:{category}"
        if max_results is None:
            max_results = int(settings.ARXIV_MAX_RESULTS)
        else:
            max_results = int(max_results)
        return self.search_papers(query, max_results)
    
    def search_recent_papers(self, query: str, days: int = 30) -> List[PaperMetadata]:
        """
        搜索最近发布的论文
        
        Args:
            query: 搜索查询
            days: 最近天数
            
        Returns:
            论文元数据列表
        """
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        date_query = f"AND submittedDate:[{start_date.strftime('%Y%m%d')}0000 TO {end_date.strftime('%Y%m%d')}2359]"
        full_query = f"({query}) {date_query}"
        
        return self.search_papers(full_query) 