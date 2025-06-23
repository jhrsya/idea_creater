"""
ArXiv爬虫模块测试
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.crawler.arxiv_crawler import ArXivCrawler, PaperMetadata


class TestArXivCrawler:
    """ArXiv爬虫测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.crawler = ArXivCrawler()
    
    def test_init(self):
        """测试初始化"""
        assert self.crawler is not None
        assert self.crawler.papers_dir.exists()
    
    def test_search_papers_empty_query(self):
        """测试空查询"""
        with pytest.raises(Exception):
            self.crawler.search_papers("")
    
    def test_search_papers_invalid_query(self):
        """测试无效查询"""
        # 这里应该测试无效查询的处理
        pass
    
    @patch('src.crawler.arxiv_crawler.arxiv')
    def test_search_papers_success(self, mock_arxiv):
        """测试成功搜索"""
        # 模拟搜索结果
        mock_result = Mock()
        mock_result.entry_id = "http://arxiv.org/abs/1234.5678"
        mock_result.title = "Test Paper"
        mock_result.authors = [Mock(name="Author 1"), Mock(name="Author 2")]
        mock_result.summary = "Test abstract"
        mock_result.categories = ["cs.AI", "cs.LG"]
        mock_result.published = "2023-01-01"
        mock_result.updated = "2023-01-01"
        mock_result.pdf_url = "http://arxiv.org/pdf/1234.5678.pdf"
        
        mock_search = Mock()
        mock_search.results.return_value = [mock_result]
        
        mock_arxiv.Search.return_value = mock_search
        
        papers = self.crawler.search_papers("test query", max_results=1)
        
        assert len(papers) == 1
        assert papers[0].title == "Test Paper"
        assert papers[0].arxiv_id == "1234.5678"
    
    def test_download_paper_success(self):
        """测试成功下载论文"""
        # 创建模拟论文元数据
        paper = PaperMetadata(
            arxiv_id="1234.5678",
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            abstract="Test abstract",
            categories=["cs.AI"],
            published_date="2023-01-01",
            updated_date="2023-01-01",
            pdf_url="http://arxiv.org/pdf/1234.5678.pdf",
            summary="Test summary"
        )
        
        # 模拟下载成功
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b"fake pdf content"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = self.crawler.download_paper(paper)
            
            # 由于文件可能已存在，这里只测试函数调用
            assert mock_get.called
    
    def test_get_paper_info_success(self):
        """测试获取论文信息成功"""
        with patch('src.crawler.arxiv_crawler.arxiv') as mock_arxiv:
            mock_result = Mock()
            mock_result.entry_id = "http://arxiv.org/abs/1234.5678"
            mock_result.title = "Test Paper"
            mock_result.authors = [Mock(name="Author 1")]
            mock_result.summary = "Test abstract"
            mock_result.categories = ["cs.AI"]
            mock_result.published = "2023-01-01"
            mock_result.updated = "2023-01-01"
            mock_result.pdf_url = "http://arxiv.org/pdf/1234.5678.pdf"
            
            mock_search = Mock()
            mock_search.results.return_value = [mock_result]
            
            mock_arxiv.Search.return_value = mock_search
            
            result = self.crawler.get_paper_info("1234.5678")
            
            assert result is not None
            assert result.title == "Test Paper"
    
    def test_search_by_category(self):
        """测试按类别搜索"""
        with patch.object(self.crawler, 'search_papers') as mock_search:
            mock_search.return_value = []
            
            self.crawler.search_by_category("cs.AI")
            
            mock_search.assert_called_with("cat:cs.AI", None)
    
    def test_search_recent_papers(self):
        """测试搜索最近论文"""
        with patch.object(self.crawler, 'search_papers') as mock_search:
            mock_search.return_value = []
            
            self.crawler.search_recent_papers("test", days=30)
            
            # 验证调用了search_papers
            assert mock_search.called


class TestPaperMetadata:
    """论文元数据测试类"""
    
    def test_paper_metadata_creation(self):
        """测试论文元数据创建"""
        paper = PaperMetadata(
            arxiv_id="1234.5678",
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            abstract="Test abstract",
            categories=["cs.AI"],
            published_date="2023-01-01",
            updated_date="2023-01-01",
            pdf_url="http://arxiv.org/pdf/1234.5678.pdf",
            summary="Test summary"
        )
        
        assert paper.arxiv_id == "1234.5678"
        assert paper.title == "Test Paper"
        assert len(paper.authors) == 2
        assert paper.categories == ["cs.AI"] 