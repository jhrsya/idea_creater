"""
创新点组合生成模块
"""
import json
import itertools
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import openai
import anthropic
from loguru import logger
from config.settings import settings
from src.extractor.innovation_extractor import InnovationPoint, ExtractedInnovations
from src.utils.ai_client import call_ai


@dataclass
class GeneratedIdea:
    """生成的新想法"""
    title: str
    description: str
    source_innovations: List[str]
    combination_type: str
    feasibility_score: float
    novelty_score: float
    impact_potential: float
    implementation_path: str
    research_directions: List[str]


@dataclass
class IdeaGenerationResult:
    """想法生成结果"""
    topic: str
    generated_ideas: List[GeneratedIdea]
    analysis_summary: str
    generation_metadata: Dict


class IdeaGenerator:
    """创新想法生成器"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # 初始化AI客户端
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def generate_ideas_from_innovations(self, innovations_list: List[ExtractedInnovations], 
                                      topic: str) -> Optional[IdeaGenerationResult]:
        """
        从创新点生成新想法
        
        Args:
            innovations_list: 创新点列表
            topic: 研究主题
            
        Returns:
            生成的想法结果
        """
        logger.info(f"开始从 {len(innovations_list)} 篇论文的创新点生成新想法")
        
        # 收集所有创新点
        all_innovations = []
        for extracted in innovations_list:
            all_innovations.extend(extracted.innovations)
        
        if not all_innovations:
            logger.error("没有可用的创新点")
            return None
        
        # 生成组合想法
        combined_ideas = self._generate_combination_ideas(all_innovations, topic)
        
        # 使用AI生成新想法
        ai_generated_ideas = self._generate_ai_ideas(all_innovations, topic)
        
        # 合并所有想法
        all_ideas = combined_ideas + ai_generated_ideas
        
        # 排序和筛选
        filtered_ideas = self._filter_and_rank_ideas(all_ideas)
        
        return IdeaGenerationResult(
            topic=topic,
            generated_ideas=filtered_ideas,
            analysis_summary=self._generate_analysis_summary(all_innovations, filtered_ideas),
            generation_metadata={
                "total_innovations": len(all_innovations),
                "total_papers": len(innovations_list),
                "generation_method": "combination_and_ai"
            }
        )
    
    def _generate_combination_ideas(self, innovations: List[InnovationPoint], 
                                  topic: str) -> List[GeneratedIdea]:
        """
        通过组合生成想法
        
        Args:
            innovations: 创新点列表
            topic: 研究主题
            
        Returns:
            组合生成的想法
        """
        ideas = []
        
        # 按类别分组创新点
        categories = {}
        for innovation in innovations:
            category = innovation.category
            if category not in categories:
                categories[category] = []
            categories[category].append(innovation)
        
        # 同类别内组合
        for category, category_innovations in categories.items():
            if len(category_innovations) >= 2:
                combinations = list(itertools.combinations(category_innovations, 2))
                for combo in combinations[:10]:  # 限制组合数量
                    idea = self._create_combination_idea(combo, "intra_category")
                    if idea:
                        ideas.append(idea)
        
        # 跨类别组合
        if len(categories) >= 2:
            category_names = list(categories.keys())
            for i in range(len(category_names)):
                for j in range(i + 1, len(category_names)):
                    cat1, cat2 = category_names[i], category_names[j]
                    innovations1 = categories[cat1][:3]  # 取前3个
                    innovations2 = categories[cat2][:3]
                    
                    for inv1 in innovations1:
                        for inv2 in innovations2:
                            idea = self._create_combination_idea([inv1, inv2], "cross_category")
                            if idea:
                                ideas.append(idea)
        
        return ideas
    
    def _create_combination_idea(self, innovations: List[InnovationPoint], 
                               combination_type: str) -> Optional[GeneratedIdea]:
        """
        创建组合想法
        
        Args:
            innovations: 要组合的创新点
            combination_type: 组合类型
            
        Returns:
            生成的想法
        """
        if len(innovations) < 2:
            return None
        
        # 计算综合评分
        avg_novelty = sum(inv.novelty_score for inv in innovations) / len(innovations)
        avg_confidence = sum(inv.confidence for inv in innovations) / len(innovations)
        
        # 生成想法标题和描述
        titles = [inv.title for inv in innovations]
        descriptions = [inv.description for inv in innovations]
        
        combined_title = f"Combined: {' + '.join(titles[:2])}"
        combined_description = f"结合了以下创新点：\n" + "\n".join(
            f"- {title}: {desc[:100]}..." for title, desc in zip(titles, descriptions)
        )
        
        return GeneratedIdea(
            title=combined_title,
            description=combined_description,
            source_innovations=titles,
            combination_type=combination_type,
            feasibility_score=avg_confidence * 0.8,
            novelty_score=avg_novelty * 1.2,  # 组合可能产生更高新颖性
            impact_potential=avg_novelty * avg_confidence,
            implementation_path="需要进一步研究和实验验证",
            research_directions=[f"结合{title}的方法" for title in titles]
        )
    
    def _generate_ai_ideas(self, innovations: List[InnovationPoint], 
                          topic: str) -> List[GeneratedIdea]:
        """
        使用AI生成新想法
        
        Args:
            innovations: 创新点列表
            topic: 研究主题
            
        Returns:
            AI生成的想法
        """
        if not self.openai_client and not self.anthropic_client and not settings.DEEPSEEK_API_KEY:
            logger.warning("AI客户端不可用，跳过AI想法生成")
            return []
        
        try:
            # 准备创新点数据
            innovations_data = []
            for inv in innovations[:20]:  # 限制数量避免token超限
                innovations_data.append({
                    "title": inv.title,
                    "description": inv.description,
                    "category": inv.category,
                    "novelty_score": inv.novelty_score
                })
            
            prompt = self._build_ai_generation_prompt(innovations_data, topic)
            
            if not self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个创新研究专家，擅长基于现有创新点提出新的研究方向。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=settings.OPENAI_MAX_TOKENS,
                    temperature=0.8
                )
                result_text = response.choices[0].message.content
            elif not self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.content[0].text
            elif settings.DEEPSEEK_API_KEY:
                # 使用 DeepSeek 生成新想法
                system_prompt = "你是一个创新研究专家，擅长基于现有创新点提出新的研究方向。"
                full_prompt = f"{system_prompt}\n\n{prompt}"
                result_text = call_ai(full_prompt, provider="deepseek")
            else:
                logger.warning("没有可用的AI客户端")
                return []
            
            return self._parse_ai_generation_result(result_text)
            
        except Exception as e:
            logger.error(f"AI生成想法失败: {e}")
            return []
    
    def _build_ai_generation_prompt(self, innovations_data: List[Dict], topic: str) -> str:
        """
        构建AI生成提示
        
        Args:
            innovations_data: 创新点数据
            topic: 研究主题
            
        Returns:
            提示文本
        """
        innovations_text = "\n".join([
            f"- {inv['title']}: {inv['description'][:200]}... (类别: {inv['category']}, 新颖性: {inv['novelty_score']})"
            for inv in innovations_data
        ])
        
        return f"""
基于以下研究主题和现有创新点，请提出5-10个新的研究方向和创新想法：

研究主题：{topic}

现有创新点：
{innovations_text}

请分析这些创新点的模式和趋势，提出新的研究方向。要求：

1. 每个想法都要有明确的标题和详细描述
2. 评估可行性和潜在影响
3. 提供实施路径和研究方向
4. 确保想法具有创新性和实用性

请以JSON格式返回：

{{
    "generated_ideas": [
        {{
            "title": "新想法标题",
            "description": "详细描述",
            "source_innovations": ["相关创新点1", "相关创新点2"],
            "combination_type": "ai_generated",
            "feasibility_score": 0.8,
            "novelty_score": 0.9,
            "impact_potential": 0.85,
            "implementation_path": "实施路径",
            "research_directions": ["研究方向1", "研究方向2"]
        }}
    ]
}}

确保JSON格式正确，所有评分都是0-1之间的数值。
"""
    
    def _parse_ai_generation_result(self, result_text: str) -> List[GeneratedIdea]:
        """
        解析AI生成结果
        
        Args:
            result_text: AI返回的结果文本
            
        Returns:
            解析后的想法列表
        """
        try:
            # 提取JSON部分
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.error("未找到JSON格式的AI生成结果")
                return []
            
            json_str = result_text[json_start:json_end]
            data = json.loads(json_str)
            
            ideas = []
            for idea_data in data.get('generated_ideas', []):
                idea = GeneratedIdea(
                    title=idea_data.get('title', ''),
                    description=idea_data.get('description', ''),
                    source_innovations=idea_data.get('source_innovations', []),
                    combination_type=idea_data.get('combination_type', 'ai_generated'),
                    feasibility_score=float(idea_data.get('feasibility_score', 0.5)),
                    novelty_score=float(idea_data.get('novelty_score', 0.5)),
                    impact_potential=float(idea_data.get('impact_potential', 0.5)),
                    implementation_path=idea_data.get('implementation_path', ''),
                    research_directions=idea_data.get('research_directions', [])
                )
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"解析AI生成结果失败: {e}")
            return []
    
    def _filter_and_rank_ideas(self, ideas: List[GeneratedIdea]) -> List[GeneratedIdea]:
        """
        筛选和排序想法
        
        Args:
            ideas: 想法列表
            
        Returns:
            筛选排序后的想法
        """
        # 计算综合评分
        for idea in ideas:
            idea.impact_potential = (idea.novelty_score + idea.feasibility_score) / 2
        
        # 按综合评分排序
        ideas.sort(key=lambda x: x.impact_potential, reverse=True)
        
        # 返回前20个想法
        return ideas[:20]
    
    def _generate_analysis_summary(self, innovations: List[InnovationPoint], 
                                 ideas: List[GeneratedIdea]) -> str:
        """
        生成分析总结
        
        Args:
            innovations: 创新点列表
            ideas: 生成的想法列表
            
        Returns:
            分析总结
        """
        # 统计创新点类别
        categories = {}
        for inv in innovations:
            category = inv.category
            categories[category] = categories.get(category, 0) + 1
        
        # 统计想法类型
        combination_types = {}
        for idea in ideas:
            combo_type = idea.combination_type
            combination_types[combo_type] = combination_types.get(combo_type, 0) + 1
        
        summary = f"""
分析总结：
- 共分析了 {len(innovations)} 个创新点
- 生成了 {len(ideas)} 个新想法
- 创新点类别分布：{dict(categories)}
- 想法类型分布：{dict(combination_types)}
- 平均新颖性评分：{sum(idea.novelty_score for idea in ideas) / len(ideas):.2f}
- 平均可行性评分：{sum(idea.feasibility_score for idea in ideas) / len(ideas):.2f}
"""
        
        return summary
    
    def save_generation_result(self, result: IdeaGenerationResult, output_path: Path):
        """
        保存生成结果
        
        Args:
            result: 生成结果
            output_path: 输出文件路径
        """
        try:
            data = {
                'topic': result.topic,
                'generated_ideas': [
                    {
                        'title': idea.title,
                        'description': idea.description,
                        'source_innovations': idea.source_innovations,
                        'combination_type': idea.combination_type,
                        'feasibility_score': idea.feasibility_score,
                        'novelty_score': idea.novelty_score,
                        'impact_potential': idea.impact_potential,
                        'implementation_path': idea.implementation_path,
                        'research_directions': idea.research_directions
                    }
                    for idea in result.generated_ideas
                ],
                'analysis_summary': result.analysis_summary,
                'generation_metadata': result.generation_metadata
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"生成结果已保存: {output_path}")
            
        except Exception as e:
            logger.error(f"保存生成结果失败: {e}") 