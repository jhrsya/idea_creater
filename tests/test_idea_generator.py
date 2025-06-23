"""
创新点组合生成模块测试
"""
import pytest
import itertools
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.generator.idea_generator import (
    IdeaGenerator, GeneratedIdea, IdeaGenerationResult
)
from src.extractor.innovation_extractor import InnovationPoint, ExtractedInnovations


class TestIdeaGenerator:
    """创新想法生成器测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.generator = IdeaGenerator()
        self.test_topic = "Machine Learning Applications"
        
        # 创建测试创新点
        self.test_innovations = [
            InnovationPoint(
                title="Algorithm A",
                description="A novel algorithm for classification",
                category="算法创新",
                impact="Improves accuracy by 15%",
                methodology="Deep learning",
                novelty_score=0.8,
                confidence=0.9
            ),
            InnovationPoint(
                title="Architecture B",
                description="A new neural network architecture",
                category="架构创新",
                impact="Reduces training time by 30%",
                methodology="Attention mechanism",
                novelty_score=0.9,
                confidence=0.85
            ),
            InnovationPoint(
                title="Method C",
                description="A new training method",
                category="方法创新",
                impact="Improves convergence speed",
                methodology="Optimization technique",
                novelty_score=0.7,
                confidence=0.8
            )
        ]
        
        # 创建测试创新点集合
        self.test_innovations_list = [
            ExtractedInnovations(
                paper_title="Paper 1",
                paper_id="1234.5678",
                innovations=[self.test_innovations[0], self.test_innovations[1]],
                summary="Paper 1 summary",
                extraction_metadata={}
            ),
            ExtractedInnovations(
                paper_title="Paper 2",
                paper_id="2345.6789",
                innovations=[self.test_innovations[2]],
                summary="Paper 2 summary",
                extraction_metadata={}
            )
        ]
    
    def test_init_without_api_keys(self):
        """测试没有API密钥的初始化"""
        generator = IdeaGenerator()
        assert generator.openai_client is None
        assert generator.anthropic_client is None
    
    @patch('src.generator.idea_generator.openai')
    def test_init_with_openai_key(self, mock_openai):
        """测试有OpenAI密钥的初始化"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            generator = IdeaGenerator()
            assert generator.openai_client is not None
            mock_openai.OpenAI.assert_called_once_with(api_key='test_key')
    
    def test_generate_ideas_from_innovations_empty_list(self):
        """测试空创新点列表"""
        result = self.generator.generate_ideas_from_innovations([], self.test_topic)
        
        assert result is None
    
    def test_generate_ideas_from_innovations_no_innovations(self):
        """测试没有创新点的列表"""
        empty_list = [
            ExtractedInnovations(
                paper_title="Paper 1",
                paper_id="1234.5678",
                innovations=[],
                summary="Empty paper",
                extraction_metadata={}
            )
        ]
        
        result = self.generator.generate_ideas_from_innovations(empty_list, self.test_topic)
        
        assert result is None
    
    def test_generate_combination_ideas_intra_category(self):
        """测试同类别内组合想法生成"""
        ideas = self.generator._generate_combination_ideas(self.test_innovations, self.test_topic)
        
        # 应该有同类别内的组合
        intra_category_ideas = [idea for idea in ideas if idea.combination_type == "intra_category"]
        assert len(intra_category_ideas) > 0
    
    def test_generate_combination_ideas_cross_category(self):
        """测试跨类别组合想法生成"""
        ideas = self.generator._generate_combination_ideas(self.test_innovations, self.test_topic)
        
        # 应该有跨类别的组合
        cross_category_ideas = [idea for idea in ideas if idea.combination_type == "cross_category"]
        assert len(cross_category_ideas) > 0
    
    def test_create_combination_idea_success(self):
        """测试成功创建组合想法"""
        innovations = [self.test_innovations[0], self.test_innovations[1]]
        
        idea = self.generator._create_combination_idea(innovations, "test_type")
        
        assert idea is not None
        assert idea.title.startswith("Combined:")
        assert len(idea.source_innovations) == 2
        assert idea.combination_type == "test_type"
        assert 0 <= idea.feasibility_score <= 1
        assert 0 <= idea.novelty_score <= 1
        assert 0 <= idea.impact_potential <= 1
    
    def test_create_combination_idea_insufficient_innovations(self):
        """测试创新点不足的情况"""
        idea = self.generator._create_combination_idea([self.test_innovations[0]], "test_type")
        
        assert idea is None
    
    def test_create_combination_idea_empty_list(self):
        """测试空列表的情况"""
        idea = self.generator._create_combination_idea([], "test_type")
        
        assert idea is None
    
    @patch('src.generator.idea_generator.openai')
    def test_generate_ai_ideas_openai_success(self, mock_openai):
        """测试OpenAI成功生成AI想法"""
        # 模拟OpenAI客户端
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "generated_ideas": [
                {
                    "title": "AI Generated Idea",
                    "description": "A new idea generated by AI",
                    "source_innovations": ["Algorithm A", "Architecture B"],
                    "combination_type": "ai_generated",
                    "feasibility_score": 0.8,
                    "novelty_score": 0.9,
                    "impact_potential": 0.85,
                    "implementation_path": "Implement using deep learning",
                    "research_directions": ["Direction 1", "Direction 2"]
                }
            ]
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        self.generator.openai_client = mock_client
        
        ideas = self.generator._generate_ai_ideas(self.test_innovations, self.test_topic)
        
        assert len(ideas) == 1
        assert ideas[0].title == "AI Generated Idea"
        assert ideas[0].combination_type == "ai_generated"
        assert ideas[0].feasibility_score == 0.8
    
    def test_generate_ai_ideas_no_models_available(self):
        """测试没有可用AI模型"""
        self.generator.openai_client = None
        self.generator.anthropic_client = None
        
        ideas = self.generator._generate_ai_ideas(self.test_innovations, self.test_topic)
        
        assert ideas == []
    
    def test_build_ai_generation_prompt(self):
        """测试构建AI生成提示"""
        innovations_data = [
            {
                "title": "Test Innovation",
                "description": "Test description",
                "category": "测试类别",
                "novelty_score": 0.8
            }
        ]
        
        prompt = self.generator._build_ai_generation_prompt(innovations_data, self.test_topic)
        
        assert self.test_topic in prompt
        assert "Test Innovation" in prompt
        assert "JSON" in prompt
        assert "generated_ideas" in prompt
    
    def test_parse_ai_generation_result_valid_json(self):
        """测试解析有效的AI生成结果"""
        json_result = '''
        {
            "generated_ideas": [
                {
                    "title": "Test Idea",
                    "description": "Test description",
                    "source_innovations": ["Source 1", "Source 2"],
                    "combination_type": "ai_generated",
                    "feasibility_score": 0.8,
                    "novelty_score": 0.9,
                    "impact_potential": 0.85,
                    "implementation_path": "Test path",
                    "research_directions": ["Direction 1", "Direction 2"]
                }
            ]
        }
        '''
        
        ideas = self.generator._parse_ai_generation_result(json_result)
        
        assert len(ideas) == 1
        assert ideas[0].title == "Test Idea"
        assert ideas[0].combination_type == "ai_generated"
        assert len(ideas[0].source_innovations) == 2
        assert len(ideas[0].research_directions) == 2
    
    def test_parse_ai_generation_result_invalid_json(self):
        """测试解析无效的AI生成结果"""
        invalid_result = "This is not a JSON string"
        
        ideas = self.generator._parse_ai_generation_result(invalid_result)
        
        assert ideas == []
    
    def test_parse_ai_generation_result_missing_json(self):
        """测试解析缺少JSON的结果"""
        result_without_json = "Some text without JSON"
        
        ideas = self.generator._parse_ai_generation_result(result_without_json)
        
        assert ideas == []
    
    def test_filter_and_rank_ideas(self):
        """测试筛选和排序想法"""
        ideas = [
            GeneratedIdea(
                title="Idea 1",
                description="Description 1",
                source_innovations=["Source 1"],
                combination_type="test",
                feasibility_score=0.8,
                novelty_score=0.9,
                impact_potential=0.0,  # 会被重新计算
                implementation_path="Path 1",
                research_directions=["Direction 1"]
            ),
            GeneratedIdea(
                title="Idea 2",
                description="Description 2",
                source_innovations=["Source 2"],
                combination_type="test",
                feasibility_score=0.6,
                novelty_score=0.7,
                impact_potential=0.0,  # 会被重新计算
                implementation_path="Path 2",
                research_directions=["Direction 2"]
            )
        ]
        
        filtered_ideas = self.generator._filter_and_rank_ideas(ideas)
        
        assert len(filtered_ideas) == 2
        # 第一个想法应该有更高的impact_potential
        assert filtered_ideas[0].impact_potential > filtered_ideas[1].impact_potential
    
    def test_filter_and_rank_ideas_limit(self):
        """测试想法数量限制"""
        # 创建超过20个想法
        ideas = []
        for i in range(25):
            idea = GeneratedIdea(
                title=f"Idea {i}",
                description=f"Description {i}",
                source_innovations=[f"Source {i}"],
                combination_type="test",
                feasibility_score=0.5,
                novelty_score=0.5,
                impact_potential=0.5,
                implementation_path=f"Path {i}",
                research_directions=[f"Direction {i}"]
            )
            ideas.append(idea)
        
        filtered_ideas = self.generator._filter_and_rank_ideas(ideas)
        
        assert len(filtered_ideas) == 20
    
    def test_generate_analysis_summary(self):
        """测试生成分析总结"""
        ideas = [
            GeneratedIdea(
                title="Idea 1",
                description="Description 1",
                source_innovations=["Source 1"],
                combination_type="intra_category",
                feasibility_score=0.8,
                novelty_score=0.9,
                impact_potential=0.85,
                implementation_path="Path 1",
                research_directions=["Direction 1"]
            ),
            GeneratedIdea(
                title="Idea 2",
                description="Description 2",
                source_innovations=["Source 2"],
                combination_type="cross_category",
                feasibility_score=0.6,
                novelty_score=0.7,
                impact_potential=0.65,
                implementation_path="Path 2",
                research_directions=["Direction 2"]
            )
        ]
        
        summary = self.generator._generate_analysis_summary(self.test_innovations, ideas)
        
        assert "分析总结" in summary
        assert "3" in summary  # 创新点数量
        assert "2" in summary  # 想法数量
        assert "intra_category" in summary
        assert "cross_category" in summary
    
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_generation_result(self, mock_file, mock_json_dump):
        """测试保存生成结果"""
        ideas = [
            GeneratedIdea(
                title="Test Idea",
                description="Test description",
                source_innovations=["Source 1"],
                combination_type="test",
                feasibility_score=0.8,
                novelty_score=0.9,
                impact_potential=0.85,
                implementation_path="Test path",
                research_directions=["Direction 1"]
            )
        ]
        
        result = IdeaGenerationResult(
            topic=self.test_topic,
            generated_ideas=ideas,
            analysis_summary="Test summary",
            generation_metadata={"test": "data"}
        )
        
        output_path = Path("test_result.json")
        self.generator.save_generation_result(result, output_path)
        
        mock_file.assert_called_once_with(output_path, 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
    
    @patch.object(IdeaGenerator, '_generate_combination_ideas')
    @patch.object(IdeaGenerator, '_generate_ai_ideas')
    def test_generate_ideas_from_innovations_success(self, mock_ai_ideas, mock_combination_ideas):
        """测试成功生成想法"""
        # 模拟组合想法
        mock_combination_ideas.return_value = [
            GeneratedIdea(
                title="Combined Idea",
                description="Combined description",
                source_innovations=["Source 1", "Source 2"],
                combination_type="intra_category",
                feasibility_score=0.8,
                novelty_score=0.9,
                impact_potential=0.85,
                implementation_path="Combined path",
                research_directions=["Combined direction"]
            )
        ]
        
        # 模拟AI想法
        mock_ai_ideas.return_value = [
            GeneratedIdea(
                title="AI Idea",
                description="AI description",
                source_innovations=["Source 3"],
                combination_type="ai_generated",
                feasibility_score=0.7,
                novelty_score=0.8,
                impact_potential=0.75,
                implementation_path="AI path",
                research_directions=["AI direction"]
            )
        ]
        
        result = self.generator.generate_ideas_from_innovations(self.test_innovations_list, self.test_topic)
        
        assert result is not None
        assert result.topic == self.test_topic
        assert len(result.generated_ideas) == 2
        assert result.generation_metadata["total_innovations"] == 3
        assert result.generation_metadata["total_papers"] == 2


class TestGeneratedIdea:
    """生成的想法测试类"""
    
    def test_generated_idea_creation(self):
        """测试生成的想法创建"""
        idea = GeneratedIdea(
            title="Test Idea",
            description="Test description",
            source_innovations=["Source 1", "Source 2"],
            combination_type="test_type",
            feasibility_score=0.8,
            novelty_score=0.9,
            impact_potential=0.85,
            implementation_path="Test path",
            research_directions=["Direction 1", "Direction 2"]
        )
        
        assert idea.title == "Test Idea"
        assert idea.description == "Test description"
        assert len(idea.source_innovations) == 2
        assert idea.combination_type == "test_type"
        assert idea.feasibility_score == 0.8
        assert idea.novelty_score == 0.9
        assert idea.impact_potential == 0.85
        assert idea.implementation_path == "Test path"
        assert len(idea.research_directions) == 2
    
    def test_generated_idea_default_scores(self):
        """测试生成想法的默认评分"""
        idea = GeneratedIdea(
            title="Test",
            description="Test",
            source_innovations=[],
            combination_type="test",
            feasibility_score=0.0,
            novelty_score=0.0,
            impact_potential=0.0,
            implementation_path="",
            research_directions=[]
        )
        
        assert idea.feasibility_score == 0.0
        assert idea.novelty_score == 0.0
        assert idea.impact_potential == 0.0


class TestIdeaGenerationResult:
    """想法生成结果测试类"""
    
    def test_idea_generation_result_creation(self):
        """测试想法生成结果创建"""
        ideas = [
            GeneratedIdea(
                title="Test Idea",
                description="Test description",
                source_innovations=["Source 1"],
                combination_type="test",
                feasibility_score=0.8,
                novelty_score=0.9,
                impact_potential=0.85,
                implementation_path="Test path",
                research_directions=["Direction 1"]
            )
        ]
        
        result = IdeaGenerationResult(
            topic="Test Topic",
            generated_ideas=ideas,
            analysis_summary="Test summary",
            generation_metadata={"test": "data"}
        )
        
        assert result.topic == "Test Topic"
        assert len(result.generated_ideas) == 1
        assert result.analysis_summary == "Test summary"
        assert result.generation_metadata["test"] == "data"
    
    def test_idea_generation_result_empty(self):
        """测试空的生成结果"""
        result = IdeaGenerationResult(
            topic="Test Topic",
            generated_ideas=[],
            analysis_summary="",
            generation_metadata={}
        )
        
        assert len(result.generated_ideas) == 0
        assert result.analysis_summary == "" 