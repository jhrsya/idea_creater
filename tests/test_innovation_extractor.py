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
    
    def test_init_without_api_keys(self):
        """测试没有API密钥的初始化"""
        extractor = InnovationExtractor()
        assert extractor.openai_client is None
        assert extractor.anthropic_client is None
    
    @patch('src.extractor.innovation_extractor.openai')
    def test_init_with_openai_key(self, mock_openai):
        """测试有OpenAI密钥的初始化"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            extractor = InnovationExtractor()
            assert extractor.openai_client is not None
            mock_openai.OpenAI.assert_called_once_with(api_key='test_key')
    
    @patch('src.extractor.innovation_extractor.anthropic')
    def test_init_with_anthropic_key(self, mock_anthropic):
        """测试有Anthropic密钥的初始化"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
            extractor = InnovationExtractor()
            assert extractor.anthropic_client is not None
            mock_anthropic.Anthropic.assert_called_once_with(api_key='test_key')
    
    @patch('src.extractor.innovation_extractor.openai')
    def test_extract_innovations_openai_success(self, mock_openai):
        """测试OpenAI成功提取创新点"""
        # 模拟OpenAI客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "innovations": [
                {
                    "title": "Novel Algorithm",
                    "description": "A new algorithm that improves accuracy",
                    "category": "算法创新",
                    "impact": "Improves accuracy by 20%",
                    "methodology": "Deep learning with novel architecture",
                    "novelty_score": 0.85,
                    "confidence": 0.9
                }
            ],
            "summary": "The paper introduces a novel algorithm",
            "extraction_metadata": {
                "model_used": "gpt-4",
                "confidence_overall": 0.85
            }
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        self.extractor.openai_client = mock_client
        
        result = self.extractor.extract_innovations_openai(
            self.test_paper_content, self.test_paper_title
        )
        
        assert result is not None
        assert result.paper_title == self.test_paper_title
        assert len(result.innovations) == 1
        assert result.innovations[0].title == "Novel Algorithm"
        assert result.innovations[0].novelty_score == 0.85
    
    @patch('src.extractor.innovation_extractor.openai')
    def test_extract_innovations_openai_failure(self, mock_openai):
        """测试OpenAI提取失败"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        self.extractor.openai_client = mock_client
        
        result = self.extractor.extract_innovations_openai(
            self.test_paper_content, self.test_paper_title
        )
        
        assert result is None
    
    @patch('src.extractor.innovation_extractor.anthropic')
    def test_extract_innovations_anthropic_success(self, mock_anthropic):
        """测试Anthropic成功提取创新点"""
        # 模拟Anthropic客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''
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
                "model_used": "claude-3",
                "confidence_overall": 0.9
            }
        }
        '''
        mock_client.messages.create.return_value = mock_response
        self.extractor.anthropic_client = mock_client
        
        result = self.extractor.extract_innovations_anthropic(
            self.test_paper_content, self.test_paper_title
        )
        
        assert result is not None
        assert result.paper_title == self.test_paper_title
        assert len(result.innovations) == 1
        assert result.innovations[0].title == "Novel Architecture"
        assert result.innovations[0].novelty_score == 0.9
    
    def test_build_extraction_prompt(self):
        """测试构建提取提示"""
        prompt = self.extractor._build_extraction_prompt(
            self.test_paper_content, self.test_paper_title
        )
        
        assert self.test_paper_title in prompt
        assert "JSON" in prompt
        assert "创新点" in prompt
        assert "novelty_score" in prompt
    
    def test_parse_extraction_result_valid_json(self):
        """测试解析有效的JSON结果"""
        json_result = '''
        {
            "innovations": [
                {
                    "title": "Test Innovation",
                    "description": "Test description",
                    "category": "测试类别",
                    "impact": "Test impact",
                    "methodology": "Test methodology",
                    "novelty_score": 0.8,
                    "confidence": 0.9
                }
            ],
            "summary": "Test summary",
            "extraction_metadata": {
                "model_used": "test_model"
            }
        }
        '''
        
        result = self.extractor._parse_extraction_result(json_result, self.test_paper_title)
        
        assert result is not None
        assert result.paper_title == self.test_paper_title
        assert len(result.innovations) == 1
        assert result.innovations[0].title == "Test Innovation"
        assert result.summary == "Test summary"
    
    def test_parse_extraction_result_invalid_json(self):
        """测试解析无效的JSON结果"""
        invalid_result = "This is not a JSON string"
        
        result = self.extractor._parse_extraction_result(invalid_result, self.test_paper_title)
        
        assert result is None
    
    def test_parse_extraction_result_missing_json(self):
        """测试解析缺少JSON的结果"""
        result_without_json = "Some text without JSON"
        
        result = self.extractor._parse_extraction_result(result_without_json, self.test_paper_title)
        
        assert result is None
    
    @patch.object(InnovationExtractor, 'extract_innovations_openai')
    def test_extract_innovations_auto_openai(self, mock_openai):
        """测试自动选择OpenAI模型"""
        mock_result = Mock()
        mock_openai.return_value = mock_result
        self.extractor.openai_client = Mock()
        
        result = self.extractor.extract_innovations(
            self.test_paper_content, self.test_paper_title, use_model="auto"
        )
        
        assert result == mock_result
        mock_openai.assert_called_once_with(self.test_paper_content, self.test_paper_title)
    
    @patch.object(InnovationExtractor, 'extract_innovations_anthropic')
    def test_extract_innovations_auto_anthropic(self, mock_anthropic):
        """测试自动选择Anthropic模型"""
        mock_result = Mock()
        mock_anthropic.return_value = mock_result
        self.extractor.openai_client = None
        self.extractor.anthropic_client = Mock()
        
        result = self.extractor.extract_innovations(
            self.test_paper_content, self.test_paper_title, use_model="auto"
        )
        
        assert result == mock_result
        mock_anthropic.assert_called_once_with(self.test_paper_content, self.test_paper_title)
    
    def test_extract_innovations_no_models_available(self):
        """测试没有可用模型"""
        self.extractor.openai_client = None
        self.extractor.anthropic_client = None
        
        result = self.extractor.extract_innovations(
            self.test_paper_content, self.test_paper_title
        )
        
        assert result is None
    
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_extracted_innovations(self, mock_file, mock_json_dump):
        """测试保存提取的创新点"""
        innovation = InnovationPoint(
            title="Test Innovation",
            description="Test description",
            category="测试类别",
            impact="Test impact",
            methodology="Test methodology",
            novelty_score=0.8,
            confidence=0.9
        )
        
        extracted = ExtractedInnovations(
            paper_title="Test Paper",
            paper_id="1234.5678",
            innovations=[innovation],
            summary="Test summary",
            extraction_metadata={"model": "test"}
        )
        
        output_path = Path("test_innovations.json")
        self.extractor.save_extracted_innovations(extracted, output_path)
        
        mock_file.assert_called_once_with(output_path, 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
    
    @patch.object(InnovationExtractor, 'extract_innovations')
    def test_batch_extract_innovations(self, mock_extract):
        """测试批量提取创新点"""
        # 模拟提取结果
        mock_result = Mock()
        mock_extract.return_value = mock_result
        
        # 模拟解析后的论文
        parsed_papers = [
            Mock(full_text="Paper 1 content", title="Paper 1"),
            Mock(full_text="Paper 2 content", title="Paper 2")
        ]
        
        output_dir = Path("test_output")
        
        with patch.object(Path, 'mkdir') as mock_mkdir:
            with patch.object(InnovationExtractor, 'save_extracted_innovations') as mock_save:
                result = self.extractor.batch_extract_innovations(parsed_papers, output_dir)
        
        assert len(result) == 2
        assert mock_extract.call_count == 2
        assert mock_save.call_count == 2
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestInnovationPoint:
    """创新点测试类"""
    
    def test_innovation_point_creation(self):
        """测试创新点创建"""
        innovation = InnovationPoint(
            title="Test Innovation",
            description="Test description",
            category="算法创新",
            impact="Improves performance",
            methodology="Deep learning",
            novelty_score=0.85,
            confidence=0.9
        )
        
        assert innovation.title == "Test Innovation"
        assert innovation.description == "Test description"
        assert innovation.category == "算法创新"
        assert innovation.impact == "Improves performance"
        assert innovation.methodology == "Deep learning"
        assert innovation.novelty_score == 0.85
        assert innovation.confidence == 0.9
    
    def test_innovation_point_default_scores(self):
        """测试创新点默认评分"""
        innovation = InnovationPoint(
            title="Test",
            description="Test",
            category="Test",
            impact="Test",
            methodology="Test",
            novelty_score=0.0,
            confidence=0.0
        )
        
        assert innovation.novelty_score == 0.0
        assert innovation.confidence == 0.0


class TestExtractedInnovations:
    """提取的创新点集合测试类"""
    
    def test_extracted_innovations_creation(self):
        """测试提取的创新点集合创建"""
        innovation = InnovationPoint(
            title="Test Innovation",
            description="Test description",
            category="测试类别",
            impact="Test impact",
            methodology="Test methodology",
            novelty_score=0.8,
            confidence=0.9
        )
        
        extracted = ExtractedInnovations(
            paper_title="Test Paper",
            paper_id="1234.5678",
            innovations=[innovation],
            summary="Test summary",
            extraction_metadata={"model": "test"}
        )
        
        assert extracted.paper_title == "Test Paper"
        assert extracted.paper_id == "1234.5678"
        assert len(extracted.innovations) == 1
        assert extracted.summary == "Test summary"
        assert extracted.extraction_metadata["model"] == "test"
    
    def test_extracted_innovations_empty(self):
        """测试空的创新点集合"""
        extracted = ExtractedInnovations(
            paper_title="Test Paper",
            paper_id="1234.5678",
            innovations=[],
            summary="",
            extraction_metadata={}
        )
        
        assert len(extracted.innovations) == 0
        assert extracted.summary == "" 