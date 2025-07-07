"""
Streamlit用户界面 - 一键式创新点生成器
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from typing import List, Dict
import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import settings
from src.crawler.arxiv_crawler import ArXivCrawler
from src.parser.pdf_parser import PDFParser
from src.extractor.innovation_extractor import InnovationExtractor, ExtractedInnovations, InnovationPoint
from src.generator.idea_generator import IdeaGenerator


def main():
    """主应用函数"""
    st.set_page_config(
        page_title="智能论文创新点生成器",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 自定义CSS样式
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .innovation-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .idea-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #ff6b6b;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .progress-step {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196f3;
    }
    
    .success-step {
        background: #e8f5e8;
        border-left-color: #4caf50;
    }
    
    .error-step {
        background: #ffebee;
        border-left-color: #f44336;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 主标题
    st.markdown("""
    <div class="main-header">
        <h1>🧠 智能论文创新点生成器</h1>
        <p>一键搜索论文，自动提取创新点，生成新的研究方向</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 设置")
        
        # 检查API配置
        if not settings.DEEPSEEK_API_KEY:
            st.error("⚠️ 未配置DeepSeek API密钥")
            st.info("请在.env文件中配置DEEPSEEK_API_KEY")
            return
        else:
            st.success("✅ API配置正常")
        
        st.divider()
        
        # 搜索设置
        max_papers = st.slider("最大论文数量", 3, 20, 5)
        st.info(f"将搜索最多 {max_papers} 篇论文")
        
        # 历史记录
        st.header("📚 历史记录")
        show_history_sidebar()
    
    # 主内容
    tab1, tab2, tab3 = st.tabs(["🚀 一键生成", "📊 结果分析", "📋 详细流程"])
    
    with tab1:
        show_one_click_generation_page(max_papers)
    
    with tab2:
        show_analysis_page()
    
    with tab3:
        show_detailed_process_page()


def show_one_click_generation_page(max_papers: int):
    """一键生成页面"""
    st.header("🚀 一键生成创新点")
    
    # 搜索输入
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 输入研究主题",
            placeholder="例如：reinforcement learning, transformer, computer vision",
            help="输入您感兴趣的研究领域关键词，系统将自动搜索相关论文并提取创新点"
        )
    
    with col2:
        st.write("")  # 占位符
        generate_button = st.button("🚀 开始生成", type="primary", use_container_width=True)
    
    if generate_button and search_query:
        # 创建会话目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = settings.DATA_DIR / f"session_{timestamp}"
        
        # 执行完整流程
        result = run_complete_pipeline(search_query, max_papers, session_dir)
        
        if result:
            st.success("🎉 创新点生成完成！")
            
            # 显示结果
            display_innovation_results(result)
            
            # 保存结果到会话目录
            save_session_results(result, session_dir, search_query)
        else:
            st.error("❌ 生成失败，请检查网络连接和API配置")
    
    elif generate_button and not search_query:
        st.warning("⚠️ 请输入搜索主题")
    
    # 显示示例
    st.markdown("---")
    st.subheader("💡 搜索示例")
    
    examples = [
        "machine learning interpretability",
        "natural language processing transformer",
        "computer vision object detection",
        "reinforcement learning robotics",
        "deep learning optimization"
    ]
    
    cols = st.columns(len(examples))
    for i, example in enumerate(examples):
        with cols[i]:
            if st.button(f"🔍 {example}", key=f"example_{i}"):
                st.session_state.search_query = example
                st.rerun()


def run_complete_pipeline(search_query: str, max_papers: int, session_dir: Path) -> Dict | None:
    """运行完整的论文分析流程"""
    
    # 创建目录结构
    papers_dir = session_dir / "papers"
    extracted_dir = session_dir / "extracted"
    innovations_dir = session_dir / "innovations"
    results_dir = session_dir / "results"
    
    for directory in [papers_dir, extracted_dir, innovations_dir, results_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # 进度追踪
    progress_container = st.container()
    
    with progress_container:
        st.markdown("### 📋 处理进度")
        
        # 步骤1: 搜索论文
        step1_placeholder = st.empty()
        step1_placeholder.markdown('<div class="progress-step">🔍 步骤1: 搜索论文中...</div>', unsafe_allow_html=True)
        
        try:
            crawler = ArXivCrawler()
            crawler.papers_dir = papers_dir
            
            papers = crawler.search_papers(search_query, max_papers)
            
            if not papers:
                step1_placeholder.markdown('<div class="progress-step error-step">❌ 步骤1: 未找到相关论文</div>', unsafe_allow_html=True)
                return None
            
            step1_placeholder.markdown(f'<div class="progress-step success-step">✅ 步骤1: 找到 {len(papers)} 篇论文</div>', unsafe_allow_html=True)
            
            # 显示论文信息
            with st.expander(f"📄 查看找到的 {len(papers)} 篇论文"):
                for i, paper in enumerate(papers, 1):
                    st.write(f"**{i}. {paper.title}**")
                    st.write(f"作者: {', '.join(paper.authors)}")
                    st.write(f"摘要: {paper.abstract[:200]}...")
                    st.write("---")
            
        except Exception as e:
            step1_placeholder.markdown(f'<div class="progress-step error-step">❌ 步骤1: 搜索失败 - {str(e)}</div>', unsafe_allow_html=True)
            return None
        
        # 步骤2: 下载论文
        step2_placeholder = st.empty()
        step2_placeholder.markdown('<div class="progress-step">📥 步骤2: 下载论文中...</div>', unsafe_allow_html=True)
        
        try:
            downloaded = crawler.download_papers(papers)
            
            if not downloaded:
                step2_placeholder.markdown('<div class="progress-step error-step">❌ 步骤2: 论文下载失败</div>', unsafe_allow_html=True)
                return None
            
            step2_placeholder.markdown(f'<div class="progress-step success-step">✅ 步骤2: 成功下载 {len(downloaded)} 篇论文</div>', unsafe_allow_html=True)
            
        except Exception as e:
            step2_placeholder.markdown(f'<div class="progress-step error-step">❌ 步骤2: 下载失败 - {str(e)}</div>', unsafe_allow_html=True)
            return None
        
        # 步骤3: 解析论文
        step3_placeholder = st.empty()
        step3_placeholder.markdown('<div class="progress-step">📖 步骤3: 解析论文中...</div>', unsafe_allow_html=True)
        
        try:
            parser = PDFParser()
            parsed_papers = parser.batch_parse_papers(papers_dir, extracted_dir)
            
            if not parsed_papers:
                step3_placeholder.markdown('<div class="progress-step error-step">❌ 步骤3: 论文解析失败</div>', unsafe_allow_html=True)
                return None
            
            step3_placeholder.markdown(f'<div class="progress-step success-step">✅ 步骤3: 成功解析 {len(parsed_papers)} 篇论文</div>', unsafe_allow_html=True)
            
            # 获取已下载的PDF文件列表，用于提取标题
            pdf_files = list(papers_dir.glob("*.pdf"))
            
            # 保存解析结果为JSON
            for i, paper in enumerate(parsed_papers):
                full_text = getattr(paper, "full_text", "")
                if not full_text and hasattr(paper, "sections"):
                    full_text = "\n".join(getattr(section, "text", "") for section in paper.sections)
                
                # 获取标题，如果没有标题则从PDF文件名中提取
                paper_title = getattr(paper, "title", "")
                if not paper_title and i < len(pdf_files):
                    # 从PDF文件名提取标题
                    pdf_file = pdf_files[i]
                    file_name = pdf_file.name.replace(".pdf", "")
                    # 清理文件名，去掉ArXiv ID部分
                    parts = file_name.split("_", 1)
                    if len(parts) > 1:
                        paper_title = parts[1].replace("_", " ")
                    else:
                        paper_title = file_name.replace("_", " ")
                
                # 如果仍然没有标题，尝试从内容开头提取
                if not paper_title or paper_title.startswith("Paper_"):
                    lines = full_text.split('\n')[:15]  # 检查前15行
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 10 and len(line) < 200:
                            # 可能是标题，排除常见的章节标题
                            line_lower = line.lower()
                            if not any(keyword in line_lower for keyword in 
                                     ['abstract', 'introduction', 'method', 'result', 'conclusion', 
                                      'references', 'appendix', 'acknowledgment', 'figure', 'table']):
                                paper_title = line
                                break
                
                # 最后的备选方案
                if not paper_title:
                    paper_title = f"Paper_{i+1}"
                
                parsed_json = {
                    "title": paper_title,
                    "full_text": full_text
                }
                
                # 使用安全的文件名
                safe_title = "".join(c for c in paper_title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                if not safe_title:
                    safe_title = f"paper_{i+1}"
                
                output_json = extracted_dir / f"{safe_title.replace(' ', '_')}_parsed.json"
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(parsed_json, f, ensure_ascii=False, indent=2)
                    
                st.write(f"💾 保存解析结果: {paper_title}")
            
        except Exception as e:
            step3_placeholder.markdown(f'<div class="progress-step error-step">❌ 步骤3: 解析失败 - {str(e)}</div>', unsafe_allow_html=True)
            return None
        
        # 步骤4: 提取创新点
        step4_placeholder = st.empty()
        step4_placeholder.markdown('<div class="progress-step">💡 步骤4: 提取创新点中...</div>', unsafe_allow_html=True)
        
        try:
            extractor = InnovationExtractor()
            
            json_files = list(extracted_dir.glob("*_parsed.json"))
            extracted_innovations = []
            
            st.write(f"🔍 找到 {len(json_files)} 个解析文件")
            
            for i, json_file in enumerate(json_files, 1):
                try:
                    st.write(f"📄 处理文件 {i}/{len(json_files)}: {json_file.name}")
                    
                    with open(json_file, "r", encoding="utf-8") as f:
                        paper_data = json.load(f)
                    
                    paper_title = paper_data.get("title", "")
                    paper_content = paper_data.get("full_text", "")
                    
                    if not paper_title:
                        st.write(f"⚠️ 文件 {json_file.name} 缺少标题，跳过")
                        continue
                        
                    if not paper_content:
                        st.write(f"⚠️ 文件 {json_file.name} 缺少内容，跳过")
                        continue
                    
                    st.write(f"🤖 正在提取创新点: {paper_title[:50]}...")
                    
                    extracted = extractor.extract_innovations(paper_content, paper_title)
                    if extracted:
                        extracted_innovations.append(extracted)
                        
                        # 保存创新点
                        output_file = innovations_dir / f"{paper_title.replace(' ', '_')[:50]}_innovations.json"
                        extractor.save_innovations(extracted, output_file)
                        
                        st.write(f"✅ 成功提取 {len(extracted.innovations)} 个创新点")
                    else:
                        st.write(f"❌ 提取失败: {paper_title[:50]}")
                        
                except Exception as file_error:
                    st.write(f"❌ 处理文件 {json_file.name} 时出错: {str(file_error)}")
                    continue
            
            if not extracted_innovations:
                step4_placeholder.markdown('<div class="progress-step error-step">❌ 步骤4: 创新点提取失败 - 没有成功提取任何创新点</div>', unsafe_allow_html=True)
                return None
            
            total_innovations = sum(len(ext.innovations) for ext in extracted_innovations)
            step4_placeholder.markdown(f'<div class="progress-step success-step">✅ 步骤4: 成功提取 {total_innovations} 个创新点</div>', unsafe_allow_html=True)
            
        except Exception as e:
            step4_placeholder.markdown(f'<div class="progress-step error-step">❌ 步骤4: 提取失败 - {str(e)}</div>', unsafe_allow_html=True)
            return None
        
        # 步骤5: 生成新想法
        step5_placeholder = st.empty()
        step5_placeholder.markdown('<div class="progress-step">🚀 步骤5: 生成新想法中...</div>', unsafe_allow_html=True)
        
        try:
            generator = IdeaGenerator()
            
            result = generator.generate_ideas_from_innovations(extracted_innovations, search_query)
            
            if not result:
                step5_placeholder.markdown('<div class="progress-step error-step">❌ 步骤5: 想法生成失败</div>', unsafe_allow_html=True)
                return None
            
            step5_placeholder.markdown(f'<div class="progress-step success-step">✅ 步骤5: 成功生成 {len(result.generated_ideas)} 个新想法</div>', unsafe_allow_html=True)
            
            return {
                'search_query': search_query,
                'papers': papers,
                'extracted_innovations': extracted_innovations,
                'generated_ideas': result,
                'session_dir': session_dir
            }
            
        except Exception as e:
            step5_placeholder.markdown(f'<div class="progress-step error-step">❌ 步骤5: 生成失败 - {str(e)}</div>', unsafe_allow_html=True)
            return None


def display_innovation_results(result: Dict):
    """显示创新点结果"""
    st.markdown("---")
    st.header("🎯 创新点分析结果")
    
    # 统计信息
    papers = result['papers']
    extracted_innovations = result['extracted_innovations']
    generated_ideas = result['generated_ideas']
    
    total_innovations = sum(len(ext.innovations) for ext in extracted_innovations)
    
    # 顶部统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📄 {len(papers)}</h3>
            <p>论文数量</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💡 {total_innovations}</h3>
            <p>创新点数量</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🚀 {len(generated_ideas.generated_ideas)}</h3>
            <p>新想法数量</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_novelty = sum(idea.novelty_score for idea in generated_ideas.generated_ideas) / len(generated_ideas.generated_ideas)
        st.markdown(f"""
        <div class="metric-card">
            <h3>⭐ {avg_novelty:.2f}</h3>
            <p>平均新颖性</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 创新点展示
    st.subheader("💡 提取的创新点")
    
    for i, extracted in enumerate(extracted_innovations, 1):
        with st.expander(f"📄 论文 {i}: {extracted.paper_title}"):
            st.markdown(f"**📝 论文摘要:** {extracted.summary}")
            st.markdown(f"**🔢 创新点数量:** {len(extracted.innovations)}")
            
            for j, innovation in enumerate(extracted.innovations, 1):
                st.markdown(f"""
                <div class="innovation-card">
                    <h4>💡 创新点 {j}: {innovation.title}</h4>
                    <p><strong>📋 描述:</strong> {innovation.description}</p>
                    <p><strong>🏷️ 类别:</strong> {innovation.category}</p>
                    <p><strong>🎯 影响:</strong> {innovation.impact}</p>
                    <p><strong>🔬 方法:</strong> {innovation.methodology}</p>
                    <div style="display: flex; gap: 20px; margin-top: 10px;">
                        <span><strong>⭐ 新颖性:</strong> {innovation.novelty_score:.2f}</span>
                        <span><strong>🎯 置信度:</strong> {innovation.confidence:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 生成的新想法
    st.subheader("🚀 生成的新想法")
    
    for i, idea in enumerate(generated_ideas.generated_ideas, 1):
        st.markdown(f"""
        <div class="idea-card">
            <h4>🚀 想法 {i}: {idea.title}</h4>
            <p><strong>📋 描述:</strong> {idea.description}</p>
            <p><strong>🔗 来源创新点:</strong> {', '.join(idea.source_innovations)}</p>
            <p><strong>🔄 组合类型:</strong> {idea.combination_type}</p>
            <p><strong>🛤️ 实施路径:</strong> {idea.implementation_path}</p>
            
            <div style="display: flex; gap: 20px; margin: 10px 0;">
                <span><strong>⭐ 新颖性:</strong> {idea.novelty_score:.2f}</span>
                <span><strong>🎯 可行性:</strong> {idea.feasibility_score:.2f}</span>
                <span><strong>🚀 影响潜力:</strong> {idea.impact_potential:.2f}</span>
            </div>
            
            <div style="margin-top: 15px;">
                <strong>🔬 研究方向:</strong>
                <ul>
                    {''.join(f'<li>{direction}</li>' for direction in idea.research_directions)}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 分析总结
    st.subheader("📊 分析总结")
    st.markdown(f"""
    <div class="innovation-card">
        <h4>🎯 总体分析</h4>
        <p>{generated_ideas.analysis_summary}</p>
    </div>
    """, unsafe_allow_html=True)


def save_session_results(result: Dict, session_dir: Path, search_query: str):
    """保存会话结果"""
    try:
        results_dir = session_dir / "results"
        results_dir.mkdir(exist_ok=True)
        
        # 保存完整结果
        output_file = results_dir / f"complete_results_{search_query.replace(' ', '_')}.json"
        
        # 转换为可序列化的格式
        serializable_result = {
            "search_query": search_query,
            "timestamp": datetime.now().isoformat(),
            "papers": [
                {
                    "title": paper.title,
                    "authors": paper.authors,
                    "abstract": paper.abstract,
                    "categories": paper.categories,
                    "arxiv_id": paper.arxiv_id
                }
                for paper in result['papers']
            ],
            "innovations": [
                {
                    "paper_title": ext.paper_title,
                    "summary": ext.summary,
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
                        for inn in ext.innovations
                    ]
                }
                for ext in result['extracted_innovations']
            ],
            "generated_ideas": {
                "topic": result['generated_ideas'].topic,
                "analysis_summary": result['generated_ideas'].analysis_summary,
                "ideas": [
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
                    for idea in result['generated_ideas'].generated_ideas
                ]
            }
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(serializable_result, f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ 结果已保存到: {output_file}")
        
    except Exception as e:
        st.error(f"❌ 保存结果失败: {e}")


def show_history_sidebar():
    """显示历史记录侧边栏"""
    data_dir = settings.DATA_DIR
    if not data_dir.exists():
        st.info("暂无历史记录")
        return
    
    # 查找会话目录
    session_dirs = [d for d in data_dir.iterdir() 
                   if d.is_dir() and d.name.startswith("session_")]
    
    if not session_dirs:
        st.info("暂无历史记录")
        return
    
    # 按时间排序
    session_dirs.sort(key=lambda x: x.name, reverse=True)
    
    st.write("最近的搜索:")
    for session_dir in session_dirs[:5]:  # 显示最近5次
        results_dir = session_dir / "results"
        if results_dir.exists():
            result_files = list(results_dir.glob("complete_results_*.json"))
            if result_files:
                try:
                    with open(result_files[0], 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    timestamp = session_dir.name.replace("session_", "")
                    query = data.get("search_query", "未知")
                    
                    if st.button(f"📅 {timestamp[:8]}\n🔍 {query[:20]}...", key=f"history_{timestamp}"):
                        st.session_state.selected_history = result_files[0]
                        st.rerun()
                        
                except Exception:
                    continue


def show_analysis_page():
    """结果分析页面"""
    st.header("📊 结果分析")
    
    if 'selected_history' in st.session_state:
        # 显示选中的历史结果
        display_historical_results(st.session_state.selected_history)
    else:
        st.info("请先在侧边栏选择历史记录，或在'一键生成'页面生成新的结果")


def display_historical_results(result_file: Path):
    """显示历史结果"""
    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        st.success(f"已加载结果: {result_file.name}")
        
        # 基本信息
        st.subheader("📋 基本信息")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("搜索主题", data.get('search_query', 'N/A'))
            st.metric("论文数量", len(data.get('papers', [])))
        
        with col2:
            st.metric("创新点数量", sum(len(inn['innovations']) for inn in data.get('innovations', [])))
            st.metric("生成想法数量", len(data.get('generated_ideas', {}).get('ideas', [])))
        
        # 可视化分析
        st.subheader("📊 可视化分析")
        
        ideas = data.get('generated_ideas', {}).get('ideas', [])
        if ideas:
            # 创建数据框
            df = pd.DataFrame(ideas)
            
            # 散点图
            fig1 = px.scatter(
                df, x='novelty_score', y='feasibility_score',
                title='想法分布：新颖性 vs 可行性',
                hover_data=['title'],
                color='impact_potential',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # 组合类型分布
            if 'combination_type' in df.columns:
                type_counts = df['combination_type'].value_counts()
                fig2 = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title='想法组合类型分布'
                )
                st.plotly_chart(fig2, use_container_width=True)
        
    except Exception as e:
        st.error(f"加载结果失败: {e}")


def show_detailed_process_page():
    """详细流程页面"""
    st.header("📋 详细流程说明")
    
    st.markdown("""
    ## 🔄 完整处理流程
    
    ### 1. 🔍 论文搜索
    - 使用ArXiv API搜索相关论文
    - 根据关键词匹配标题、摘要和内容
    - 按相关性和时间排序
    
    ### 2. 📥 论文下载
    - 下载选中论文的PDF文件
    - 验证文件完整性
    - 存储到本地目录
    
    ### 3. 📖 论文解析
    - 使用PDF解析器提取文本内容
    - 识别章节结构和关键信息
    - 清理和格式化文本
    
    ### 4. 💡 创新点提取
    - 使用AI模型分析论文内容
    - 识别技术创新、方法创新和应用创新
    - 评估创新点的新颖性和影响力
    
    ### 5. 🚀 新想法生成
    - 基于提取的创新点进行组合分析
    - 生成跨领域的新研究方向
    - 评估可行性和潜在影响
    
    ## 🎯 评估指标
    
    - **新颖性 (Novelty)**: 想法的原创性和独特性
    - **可行性 (Feasibility)**: 实现的技术可能性
    - **影响潜力 (Impact)**: 对领域发展的潜在贡献
    - **置信度 (Confidence)**: AI模型的判断置信度
    """)


if __name__ == "__main__":
    main() 