"""
智能论文创新点生成器 - 主程序
"""
import click
from pathlib import Path
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(__file__))

from config.settings import settings
from src.utils.logger import setup_logger
from src.crawler.arxiv_crawler import ArXivCrawler
from src.parser.pdf_parser import PDFParser
from src.extractor.innovation_extractor import InnovationExtractor
from src.generator.idea_generator import IdeaGenerator
from loguru import logger


@click.group()
def cli():
    """智能论文创新点生成器"""
    pass


@cli.command()
@click.option('--query', '-q', required=True, help='搜索查询')
@click.option('--max-results', '-m', default=20, help='最大结果数量')
@click.option('--category', '-c', help='论文类别')
@click.option('--download', '-d', is_flag=True, help='下载论文PDF')
def search(query, max_results, category, download):
    """搜索ArXiv论文"""
    logger.info(f"开始搜索论文: {query}")
    
    try:
        crawler = ArXivCrawler()
        
        # 构建搜索查询
        search_query = query
        if category:
            search_query += f" AND cat:{category}"
        
        # 搜索论文
        papers = crawler.search_papers(search_query, max_results)
        
        if papers:
            logger.info(f"找到 {len(papers)} 篇论文")
            
            # 显示论文信息
            for i, paper in enumerate(papers, 1):
                logger.info(f"{i}. {paper.title}")
                logger.info(f"   作者: {', '.join(paper.authors)}")
                logger.info(f"   类别: {', '.join(paper.categories)}")
                logger.info(f"   发布日期: {paper.published_date.strftime('%Y-%m-%d')}")
                logger.info(f"   摘要: {paper.abstract[:200]}...")
                logger.info("---")
            
            # 下载论文
            if download:
                logger.info("开始下载论文...")
                downloaded = crawler.download_papers(papers)
                logger.info(f"成功下载 {len(downloaded)} 篇论文")
        else:
            logger.warning("未找到相关论文")
            
    except Exception as e:
        logger.error(f"搜索失败: {e}")


@cli.command()
@click.option('--input-dir', '-i', default='data/papers', help='PDF文件目录')
@click.option('--output-dir', '-o', default='data/extracted', help='输出目录')
def parse(input_dir, output_dir):
    """解析PDF论文"""
    logger.info("开始解析PDF论文")
    
    try:
        pdf_dir = Path(input_dir)
        output_path = Path(output_dir)
        
        if not pdf_dir.exists():
            logger.error(f"PDF目录不存在: {pdf_dir}")
            return
        
        parser = PDFParser()
        parsed_papers = parser.batch_parse_papers(pdf_dir, output_path)
        
        if parsed_papers:
            logger.info(f"成功解析 {len(parsed_papers)} 篇论文")
            
            # 显示解析统计
            total_sections = sum(len(paper.sections) for paper in parsed_papers)
            total_refs = sum(len(paper.references) for paper in parsed_papers)
            
            logger.info(f"总章节数: {total_sections}")
            logger.info(f"总参考文献数: {total_refs}")
            logger.info(f"平均章节数: {total_sections / len(parsed_papers):.1f}")
        else:
            logger.warning("没有成功解析的论文")
            
    except Exception as e:
        logger.error(f"解析失败: {e}")


@cli.command()
@click.option('--input-dir', '-i', default='data/extracted', help='解析文件目录')
@click.option('--output-dir', '-o', default='data/innovations', help='输出目录')
def extract(input_dir, output_dir):
    """提取创新点"""
    logger.info("开始提取创新点")
    
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            logger.error(f"输入目录不存在: {input_path}")
            return
        
        # 检查AI配置
        if not settings.DEEPSEEK_API_KEY:
            logger.error("未配置DeepSeek API密钥")
            return
        
        extractor = InnovationExtractor()
        
        # 加载解析后的论文
        json_files = list(input_path.glob("*_parsed.json"))
        if not json_files:
            logger.error("未找到解析文件")
            return
        
        logger.info(f"找到 {len(json_files)} 个解析文件")
        
        # 提取创新点
        extracted_innovations = []
        for json_file in json_files:
            logger.info(f"处理文件: {json_file.name}")
            
            # 这里需要实现从JSON文件加载ParsedPaper对象的逻辑
            # 简化处理，跳过实际提取
            logger.info(f"跳过文件: {json_file.name} (需要实现JSON加载逻辑)")
        
        logger.info("创新点提取完成")
        
    except Exception as e:
        logger.error(f"提取失败: {e}")


@cli.command()
@click.option('--input-dir', '-i', default='data/innovations', help='创新点文件目录')
@click.option('--output-dir', '-o', default='data/results', help='输出目录')
@click.option('--topic', '-t', required=True, help='研究主题')
def generate(input_dir, output_dir, topic):
    """生成新想法"""
    logger.info(f"开始生成想法，主题: {topic}")
    
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            logger.error(f"输入目录不存在: {input_path}")
            return
        
        # 检查AI配置
        if not settings.DEEPSEEK_API_KEY:
            logger.error("未配置DeepSeek API密钥")
            return
        
        generator = IdeaGenerator()
        
        # 加载创新点
        json_files = list(input_path.glob("*_innovations.json"))
        if not json_files:
            logger.error("未找到创新点文件")
            return
        
        logger.info(f"找到 {len(json_files)} 个创新点文件")
        
        # 这里需要实现从JSON文件加载ExtractedInnovations对象的逻辑
        # 简化处理，跳过实际生成
        logger.info("跳过想法生成 (需要实现JSON加载逻辑)")
        
    except Exception as e:
        logger.error(f"生成失败: {e}")


@cli.command()
@click.option('--port', '-p', default=8501, help='端口号')
@click.option('--host', '-h', default='localhost', help='主机地址')
def web(port, host):
    """启动Web界面"""
    logger.info(f"启动Web界面: http://{host}:{port}")
    
    try:
        import subprocess
        import sys
        
        # 启动Streamlit应用
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "src/ui/streamlit_app.py",
            "--server.port", str(port),
            "--server.address", host
        ]
        
        subprocess.run(cmd)
        
    except Exception as e:
        logger.error(f"启动Web界面失败: {e}")


@cli.command()
def setup():
    """初始化项目"""
    logger.info("初始化项目...")
    
    try:
        # 创建必要的目录
        directories = [
            settings.DATA_DIR,
            settings.LOGS_DIR,
            settings.DATA_DIR / "papers",
            settings.DATA_DIR / "extracted",
            settings.DATA_DIR / "innovations",
            settings.DATA_DIR / "results"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录: {directory}")
        
        # 创建示例配置文件
        env_file = Path(".env")
        if not env_file.exists():
            env_content = """# AI API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 其他配置
DEBUG=True
LOG_LEVEL=INFO
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            logger.info("创建配置文件: .env")
        
        logger.info("项目初始化完成")
        logger.info("请配置.env文件中的API密钥")
        
    except Exception as e:
        logger.error(f"初始化失败: {e}")


@cli.command()
def test():
    """运行测试"""
    logger.info("运行测试...")
    
    try:
        import pytest
        
        # 运行测试
        pytest.main(["tests/"])
        
    except ImportError:
        logger.error("pytest未安装，请运行: pip install pytest")
    except Exception as e:
        logger.error(f"测试失败: {e}")


if __name__ == "__main__":
    # 初始化日志
    setup_logger()
    
    # 运行CLI
    cli() 