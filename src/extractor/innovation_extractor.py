"""
创新点提取模块
"""
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from loguru import logger
from config.settings import settings
from src.utils.ai_client import call_ai


@dataclass
class InnovationPoint:
    """创新点"""
    title: str
    description: str
    category: str
    impact: str
    methodology: str
    novelty_score: float
    confidence: float


@dataclass
class ExtractedInnovations:
    """提取的创新点集合"""
    paper_title: str
    paper_id: str
    innovations: List[InnovationPoint]
    summary: str
    extraction_metadata: Dict


class InnovationExtractor:
    """创新点提取器"""
    
    def __init__(self):
        # 检查DeepSeek API配置
        if not settings.DEEPSEEK_API_KEY:
            logger.warning("未配置DEEPSEEK_API_KEY")
    
    def extract_innovations(self, paper_content: str, paper_title: str) -> Optional[ExtractedInnovations]:
        """
        提取创新点
        
        Args:
            paper_content: 论文内容
            paper_title: 论文标题
            
        Returns:
            提取的创新点
        """
        logger.info(f"开始提取论文创新点: {paper_title}")
        
        if not settings.DEEPSEEK_API_KEY:
            logger.error("DeepSeek API密钥未配置")
            return None
        
        try:
            prompt = self._build_extraction_prompt(paper_content, paper_title)
            logger.info(f"发送AI请求，论文: {paper_title}")
            
            result_text = call_ai(prompt)
            if result_text:
                logger.info(f"AI返回结果，长度: {len(result_text)}")
                parsed_result = self._parse_extraction_result(result_text, paper_title)
                if parsed_result:
                    logger.info(f"成功解析创新点: {len(parsed_result.innovations)} 个")
                    return parsed_result
                else:
                    logger.error("解析AI结果失败")
                    return None
            else:
                logger.error("AI返回空结果")
                return None
        except Exception as e:
            logger.error(f"提取创新点失败: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            return None
    
    def _build_extraction_prompt(self, paper_content: str, paper_title: str) -> str:
        """
        构建提取提示
        
        Args:
            paper_content: 论文内容
            paper_title: 论文标题
            
        Returns:
            提示文本
        """
        return f"""
请分析以下学术论文，提取其中的创新点。请按照以下格式返回JSON结果：

论文标题：{paper_title}

论文内容：
{paper_content[:8000]}  # 限制长度避免token超限

请提取该论文的创新点，并以JSON格式返回：

{{
    "innovations": [
        {{
            "title": "创新点标题",
            "description": "创新点详细描述",
            "category": "创新类别（如：算法创新、架构创新、应用创新等）",
            "impact": "创新影响和意义",
            "methodology": "实现方法",
            "novelty_score": 0.85,
            "confidence": 0.9
        }}
    ],
    "summary": "论文创新点总结",
    "extraction_metadata": {{
        "model_used": "使用的模型",
        "extraction_time": "提取时间",
        "confidence_overall": 0.85
    }}
}}

要求：
1. 创新点要具体、可量化
2. 每个创新点都要有明确的类别和影响评估
3. novelty_score和confidence都是0-1之间的数值
4. 确保JSON格式正确
"""
    
    def _parse_extraction_result(self, result_text: str, paper_title: str) -> Optional[ExtractedInnovations]:
        """
        解析提取结果
        
        Args:
            result_text: AI返回的结果文本
            paper_title: 论文标题
            
        Returns:
            解析后的创新点
        """
        try:
            # 尝试提取JSON部分
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.error("未找到JSON格式的结果")
                return None
            
            json_str = result_text[json_start:json_end]
            data = json.loads(json_str)
            
            # 解析创新点
            innovations = []
            for innovation_data in data.get('innovations', []):
                innovation = InnovationPoint(
                    title=innovation_data.get('title', ''),
                    description=innovation_data.get('description', ''),
                    category=innovation_data.get('category', ''),
                    impact=innovation_data.get('impact', ''),
                    methodology=innovation_data.get('methodology', ''),
                    novelty_score=float(innovation_data.get('novelty_score', 0.5)),
                    confidence=float(innovation_data.get('confidence', 0.5))
                )
                innovations.append(innovation)
            
            return ExtractedInnovations(
                paper_title=paper_title,
                paper_id="",  # 可以从其他地方获取
                innovations=innovations,
                summary=data.get('summary', ''),
                extraction_metadata=data.get('extraction_metadata', {})
            )
            
        except Exception as e:
            logger.error(f"解析提取结果失败: {e}")
            return None
    
    def save_innovations(self, innovations: ExtractedInnovations, output_path: Path):
        """
        保存创新点到文件
        
        Args:
            innovations: 创新点对象
            output_path: 输出路径
        """
        try:
            # 转换为字典格式
            data = {
                "paper_title": innovations.paper_title,
                "paper_id": innovations.paper_id,
                "innovations": [
                    {
                        "title": inn.title,
                        "description": inn.description,
                        "category": inn.category,
                        "impact": inn.impact,
                        "methodology": inn.methodology,
                        "novelty_score": inn.novelty_score,
                        "confidence": inn.confidence
                    }
                    for inn in innovations.innovations
                ],
                "summary": innovations.summary,
                "extraction_metadata": innovations.extraction_metadata
            }
            
            # 保存到JSON文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"创新点已保存到: {output_path}")
            
        except Exception as e:
            logger.error(f"保存创新点失败: {e}")
    
    def load_innovations(self, input_path: Path) -> Optional[ExtractedInnovations]:
        """
        从文件加载创新点
        
        Args:
            input_path: 输入路径
            
        Returns:
            创新点对象
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 构建创新点对象
            innovations = []
            for inn_data in data.get("innovations", []):
                innovation = InnovationPoint(
                    title=inn_data.get("title", ""),
                    description=inn_data.get("description", ""),
                    category=inn_data.get("category", ""),
                    impact=inn_data.get("impact", ""),
                    methodology=inn_data.get("methodology", ""),
                    novelty_score=float(inn_data.get("novelty_score", 0.5)),
                    confidence=float(inn_data.get("confidence", 0.5))
                )
                innovations.append(innovation)
            
            # 构建结果对象
            extracted = ExtractedInnovations(
                paper_title=data.get("paper_title", ""),
                paper_id=data.get("paper_id", ""),
                innovations=innovations,
                summary=data.get("summary", ""),
                extraction_metadata=data.get("extraction_metadata", {})
            )
            
            logger.info(f"成功加载 {len(innovations)} 个创新点")
            return extracted
            
        except Exception as e:
            logger.error(f"加载创新点失败: {e}")
            return None
    
    def save_extracted_innovations(self, extracted: ExtractedInnovations, output_path: Path):
        """
        保存提取的创新点
        
        Args:
            extracted: 提取的创新点
            output_path: 输出文件路径
        """
        try:
            data = {
                'paper_title': extracted.paper_title,
                'paper_id': extracted.paper_id,
                'innovations': [
                    {
                        'title': innovation.title,
                        'description': innovation.description,
                        'category': innovation.category,
                        'impact': innovation.impact,
                        'methodology': innovation.methodology,
                        'novelty_score': innovation.novelty_score,
                        'confidence': innovation.confidence
                    }
                    for innovation in extracted.innovations
                ],
                'summary': extracted.summary,
                'extraction_metadata': extracted.extraction_metadata
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"创新点已保存: {output_path}")
            
        except Exception as e:
            logger.error(f"保存创新点失败: {e}")
    
    def batch_extract_innovations(self, parsed_papers: List, output_dir: Path) -> List[ExtractedInnovations]:
        """
        批量提取创新点
        
        Args:
            parsed_papers: 解析后的论文列表
            output_dir: 输出目录
            
        Returns:
            提取的创新点列表
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted_innovations = []
        
        logger.info(f"开始批量提取创新点，共 {len(parsed_papers)} 篇论文")
        
        for i, paper in enumerate(parsed_papers, 1):
            logger.info(f"提取进度: {i}/{len(parsed_papers)}")
            
            # 提取创新点
            extracted = self.extract_innovations(paper.full_text, paper.title)
            if extracted:
                # 保存结果
                output_file = output_dir / f"{paper.title.replace(' ', '_')[:50]}_innovations.json"
                self.save_extracted_innovations(extracted, output_file)
                extracted_innovations.append(extracted)
        
        logger.info(f"批量提取完成，成功提取 {len(extracted_innovations)} 篇论文的创新点")
        return extracted_innovations 