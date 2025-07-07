"""
创新点提取模块测试
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.extractor.innovation_extractor import (
    InnovationExtractor, InnovationPoint, ExtractedInnovations
)


class TestInnovationExtractor:
    """创新点提取器测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.extractor = InnovationExtractor()
        self.test_paper_content = """
        This is a test paper about machine learning innovations.
        The paper introduces a new algorithm that improves accuracy by 20%.
        The methodology uses deep learning techniques with novel architecture.
        """
        self.test_paper_title = "Test Paper on ML Innovations"
    
    def test_init(self):
        """测试初始化"""
        extractor = InnovationExtractor()
        # DeepSeek使用统一的ai_client，不需要单独的客户端对象
        assert extractor is not None
    
    @patch('src.extractor.innovation_extractor.call_ai')
    def test_extract_innovations_success(self, mock_call_ai):
        """测试成功提取创新点"""
        # 模拟AI返回结果
        mock_call_ai.return_value = '''
        {
            "innovations": [
                {
                    "title": "Novel Architecture",
                    "description": "A new neural network architecture",
                    "category": "架构创新",
                    "impact": "Reduces computational cost",
                    "methodology": "Attention mechanism",
                    "novelty_score": 0.9,
                    "confidence": 0.85
                }
            ],
            "summary": "The paper proposes a novel architecture",
            "extraction_metadata": {
                "model_used": "deepseek-chat",
                "confidence_overall": 0.9
            }
        }
        '''
        
        result = self.extractor.extract_innovations(
            self.test_paper_content, self.test_paper_title
        )
        
        assert result is not None
        assert result.paper_title == self.test_paper_title
        assert len(result.innovations) == 1
        assert result.innovations[0].title == "Novel Architecture"
        assert result.innovations[0].novelty_score == 0.9
        mock_call_ai.assert_called_once()
    
    @patch('src.extractor.innovation_extractor.call_ai')
    def test_extract_innovations_failure(self, mock_call_ai):
        """测试提取失败"""
        mock_call_ai.side_effect = Exception("API error")
        
        result = self.extractor.extract_innovations(
            self.test_paper_content, self.test_paper_title
        )
        
        assert result is None
    
    @patch('src.extractor.innovation_extractor.call_ai')
    def test_extract_innovations_empty_result(self, mock_call_ai):
        """测试空结果"""
        mock_call_ai.return_value = None
        
        result = self.extractor.extract_innovations(
            self.test_paper_content, self.test_paper_title
        )
        
        assert result is None
    
    def test_save_and_load_innovations(self):
        """测试保存和加载创新点"""
        # 创建测试数据
        innovation = InnovationPoint(
            title="Test Innovation",
            description="Test description",
            category="Test Category",
            impact="Test impact",
            methodology="Test methodology",
            novelty_score=0.8,
            confidence=0.9
        )
        
        extracted = ExtractedInnovations(
            paper_title="Test Paper",
            paper_id="test_id",
            innovations=[innovation],
            summary="Test summary",
            extraction_metadata={"test": "metadata"}
        )
        
        # 测试保存
        test_path = Path("/tmp/test_innovations.json")
        self.extractor.save_innovations(extracted, test_path)
        
        # 验证文件存在
        assert test_path.exists()
        
        # 测试加载
        loaded = self.extractor.load_innovations(test_path)
        assert loaded is not None
        assert loaded.paper_title == "Test Paper"
        assert len(loaded.innovations) == 1
        assert loaded.innovations[0].title == "Test Innovation"
        
        # 清理测试文件
        test_path.unlink()
    
    def test_build_extraction_prompt(self):
        """测试构建提取提示"""
        prompt = self.extractor._build_extraction_prompt(
            self.test_paper_content, self.test_paper_title
        )
        
        assert self.test_paper_title in prompt
        assert "innovations" in prompt
        assert "JSON" in prompt
    
    def test_parse_extraction_result_success(self):
        """测试解析提取结果成功"""
        result_text = '''
        {
            "innovations": [
                {
                    "title": "Test Innovation",
                    "description": "Test description",
                    "category": "Test Category",
                    "impact": "Test impact",
                    "methodology": "Test methodology",
                    "novelty_score": 0.8,
                    "confidence": 0.9
                }
            ],
            "summary": "Test summary",
            "extraction_metadata": {"test": "metadata"}
        }
        '''
        
        result = self.extractor._parse_extraction_result(result_text, "Test Paper")
        
        assert result is not None
        assert result.paper_title == "Test Paper"
        assert len(result.innovations) == 1
        assert result.innovations[0].title == "Test Innovation"
    
    def test_parse_extraction_result_invalid_json(self):
        """测试解析无效JSON"""
        result_text = "This is not valid JSON"
        
        result = self.extractor._parse_extraction_result(result_text, "Test Paper")
        
        assert result is None


class TestInnovationPoint:
    """创新点测试类"""
    
    def test_innovation_point_creation(self):
        """测试创新点创建"""
        innovation = InnovationPoint(
            title="Test Innovation",
            description="Test description",
            category="Test Category",
            impact="Test impact",
            methodology="Test methodology",
            novelty_score=0.8,
            confidence=0.9
        )
        
        assert innovation.title == "Test Innovation"
        assert innovation.novelty_score == 0.8
        assert innovation.confidence == 0.9


class TestExtractedInnovations:
    """提取创新点集合测试类"""
    
    def test_extracted_innovations_creation(self):
        """测试创新点集合创建"""
        innovation = InnovationPoint(
            title="Test Innovation",
            description="Test description",
            category="Test Category",
            impact="Test impact",
            methodology="Test methodology",
            novelty_score=0.8,
            confidence=0.9
        )
        
        extracted = ExtractedInnovations(
            paper_title="Test Paper",
            paper_id="test_id",
            innovations=[innovation],
            summary="Test summary",
            extraction_metadata={"test": "metadata"}
        )
        
        assert extracted.paper_title == "Test Paper"
        assert len(extracted.innovations) == 1
        assert extracted.innovations[0].title == "Test Innovation" 