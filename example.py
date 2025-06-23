"""
智能论文创新点生成器 - 使用示例
"""
import os
import sys
from pathlib import Path
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))

from config.settings import settings
from src.utils.logger import setup_logger
from loguru import logger


def example_workflow():
    """完整工作流程示例"""
    logger.info("开始智能论文创新点生成器示例")
    
    # 1. 初始化项目
    logger.info("步骤1: 初始化项目")
    try:
        from main import setup
        # setup()
        logger.success("项目初始化完成")
        logger.info("setup() 执行完毕，准备搜索论文")
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        return
    
    # # 2. 搜索论文
    # logger.info("步骤2: 搜索论文")
    # try:
    #     from src.crawler.arxiv_crawler import ArXivCrawler
        
    #     crawler = ArXivCrawler()
    #     query = "reinforcement learning, llm, reason, code, math"
    #     papers = crawler.search_papers(query, max_results=5)
        
    #     if papers:
    #         logger.success(f"找到 {len(papers)} 篇论文")
            
    #         # 显示论文信息
    #         for i, paper in enumerate(papers, 1):
    #             logger.info(f"{i}. {paper.title}")
    #             logger.info(f"   作者: {', '.join(paper.authors)}")
    #             logger.info(f"   类别: {', '.join(paper.categories)}")
    #             logger.info("---")
            
    #         # 下载论文
    #         logger.info("开始下载论文...")
    #         downloaded = crawler.download_papers(papers)
    #         logger.success(f"成功下载 {len(downloaded)} 篇论文")
    #     else:
    #         logger.warning("未找到相关论文")
            
    # except Exception as e:
    #     logger.error(f"搜索论文失败: {e}")
    #     return
    
    # # 3. 解析论文
    # logger.info("步骤3: 解析论文")
    # try:
    #     from src.parser.pdf_parser import PDFParser
        
    #     parser = PDFParser()
    #     pdf_dir = settings.DATA_DIR / "papers"
    #     output_dir = settings.DATA_DIR / "extracted"
        
    #     if pdf_dir.exists() and list(pdf_dir.glob("*.pdf")):
    #         parsed_papers = parser.batch_parse_papers(pdf_dir, output_dir)
            
    #         if parsed_papers:
    #             logger.success(f"成功解析 {len(parsed_papers)} 篇论文")
                
    #             # 显示解析统计
    #             total_sections = sum(len(paper.sections) for paper in parsed_papers)
    #             logger.info(f"总章节数: {total_sections}")
    #             logger.info(f"平均章节数: {total_sections / len(parsed_papers):.1f}")

    #             # 补全：保存每篇论文的全文和标题为 *_parsed.json
    #             for paper in parsed_papers:
    #                 # 优先用 paper.full_text，否则拼接所有章节内容
    #                 full_text = getattr(paper, "full_text", "")
    #                 if not full_text and hasattr(paper, "sections"):
    #                     full_text = "\n".join(getattr(section, "text", "") for section in paper.sections)
    #                 parsed_json = {
    #                     "title": getattr(paper, "title", ""),
    #                     "full_text": full_text
    #                 }
    #                 output_json = output_dir / f"{parsed_json['title'].replace(' ', '_')[:50]}_parsed.json"
    #                 try:
    #                     with open(output_json, "w", encoding="utf-8") as f:
    #                         json.dump(parsed_json, f, ensure_ascii=False, indent=2)
    #                     logger.info(f"已保存解析结果: {output_json}")
    #                 except Exception as e:
    #                     logger.error(f"保存解析结果失败: {e}")
    #         else:
    #             logger.warning("没有成功解析的论文")
    #     else:
    #         logger.warning("没有找到PDF文件")
            
    # except Exception as e:
    #     logger.error(f"解析论文失败: {e}")
    #     return
    
    # # 4. 提取创新点（需要AI API密钥）
    # logger.info("步骤4: 提取创新点")
    # if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
    #     logger.warning("未配置AI API密钥，跳过创新点提取")
    #     logger.info("请配置.env文件中的OPENAI_API_KEY或ANTHROPIC_API_KEY")
    # else:
    #     try:
    #         from src.extractor.innovation_extractor import InnovationExtractor
            
    #         extractor = InnovationExtractor()
    #         extracted_dir = settings.DATA_DIR / "extracted"
    #         output_dir = settings.DATA_DIR / "innovations"
            
    #         json_files = list(extracted_dir.glob("*_parsed.json"))
    #         if json_files:
    #             logger.info(f"找到 {len(json_files)} 个解析文件")
    #             for json_file in json_files:
    #                 try:
    #                     with open(json_file, "r", encoding="utf-8") as f:
    #                         paper_data = json.load(f)
    #                     paper_title = paper_data.get("title", "")
    #                     paper_content = paper_data.get("full_text", "")
    #                     if not paper_title or not paper_content:
    #                         logger.warning(f"{json_file} 缺少 title 或 full_text 字段，跳过")
    #                         continue
    #                     logger.info(f"开始提取创新点: {paper_title}")
    #                     # 调用创新点提取
    #                     extracted = extractor.extract_innovations(paper_content, paper_title, use_model="deepseek")
    #                     if extracted:
    #                         output_file = output_dir / f"{paper_title.replace(' ', '_')[:50]}_innovations.json"
    #                         extractor.save_extracted_innovations(extracted, output_file)
    #                         logger.success(f"已提取并保存: {output_file}")
    #                     else:
    #                         logger.warning(f"未能提取创新点: {paper_title}")
    #                 except Exception as e:
    #                     logger.error(f"处理文件 {json_file} 时出错: {e}")
    #         else:
    #             logger.warning("未找到解析文件")
                
    #     except Exception as e:
    #         logger.error(f"提取创新点失败: {e}")
    
    # 5. 生成新想法（需要AI API密钥）
    logger.info("步骤5: 生成新想法")
    if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
        logger.warning("未配置AI API密钥，跳过想法生成")
    else:
        try:
            from src.generator.idea_generator import IdeaGenerator
            
            generator = IdeaGenerator()
            innovations_dir = settings.DATA_DIR / "innovations"
            output_dir = settings.DATA_DIR / "results"
            
            json_files = list(innovations_dir.glob("*_innovations.json"))
            if json_files:
                logger.info(f"找到 {len(json_files)} 个创新点文件")
                
                innovations_list = []
                for json_file in json_files:
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        # 将字典转换为 ExtractedInnovations 对象
                        from src.extractor.innovation_extractor import ExtractedInnovations, InnovationPoint
                        
                        innovations = []
                        for inv_data in data.get("innovations", []):
                            innovation = InnovationPoint(
                                title=inv_data.get("title", ""),
                                description=inv_data.get("description", ""),
                                category=inv_data.get("category", ""),
                                impact=inv_data.get("impact", ""),
                                methodology=inv_data.get("methodology", ""),
                                novelty_score=float(inv_data.get("novelty_score", 0.5)),
                                confidence=float(inv_data.get("confidence", 0.5))
                            )
                            innovations.append(innovation)
                        
                        extracted_innovations = ExtractedInnovations(
                            paper_title=data.get("paper_title", ""),
                            paper_id=data.get("paper_id", ""),
                            innovations=innovations,
                            summary=data.get("summary", ""),
                            extraction_metadata=data.get("extraction_metadata", {})
                        )
                        innovations_list.append(extracted_innovations)
                        logger.info(f"已加载创新点文件: {json_file.name}")
                    except Exception as e:
                        logger.error(f"加载创新点文件 {json_file} 失败: {e}")

                if innovations_list:
                    topic = "reinforcement learning, llm, reasoning"  # 基于搜索主题
                    logger.info(f"开始生成新想法，主题: {topic}")
                    
                    # 调用生成器生成新想法
                    result = generator.generate_ideas_from_innovations(innovations_list, topic)
                    if result:
                        output_file = output_dir / f"generated_ideas_{topic.replace(' ', '_')}.json"
                        try:
                            # 将结果转换为可序列化的格式
                            result_data = {
                                "topic": result.topic,
                                "generated_ideas": [
                                    {
                                        "title": idea.title,
                                        "description": idea.description,
                                        "source_innovations": idea.source_innovations,
                                        "combination_type": idea.combination_type,
                                        "feasibility_score": idea.feasibility_score,
                                        "novelty_score": idea.novelty_score,
                                        "impact_potential": idea.impact_potential,
                                        "implementation_path": idea.implementation_path,
                                        "research_directions": idea.research_directions
                                    }
                                    for idea in result.generated_ideas
                                ],
                                "analysis_summary": result.analysis_summary,
                                "generation_metadata": result.generation_metadata
                            }
                            with open(output_file, "w", encoding="utf-8") as f:
                                json.dump(result_data, f, ensure_ascii=False, indent=2)
                            logger.success(f"已生成新想法并保存: {output_file}")
                        except Exception as e:
                            logger.error(f"保存新想法失败: {e}")
                    else:
                        logger.warning("未能生成新想法")
                else:
                    logger.warning("未能加载任何创新点数据")
            else:
                logger.warning("未找到创新点文件")
                
        except Exception as e:
            logger.error(f"生成想法失败: {e}")
    
    logger.success("示例工作流程完成")
    logger.info("请查看data目录中的结果文件")


def quick_start():
    """快速开始指南"""
    logger.info("=== 智能论文创新点生成器 - 快速开始 ===")
    
    print("""
使用步骤：

1. 安装依赖：
   pip install -r requirements.txt

2. 配置API密钥：
   编辑.env文件，添加你的OpenAI或Anthropic API密钥

3. 初始化项目：
   python main.py setup

4. 搜索论文：
   python main.py search -q "machine learning" -d

5. 解析论文：
   python main.py parse

6. 提取创新点：
   python main.py extract

7. 生成新想法：
   python main.py generate -t "深度学习应用"

8. 启动Web界面：
   python main.py web

或者运行完整示例：
   python example.py
    """)


if __name__ == "__main__":
    # 初始化日志
    setup_logger()
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_start()
    else:
        example_workflow() 