"""
Streamlit用户界面
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

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import settings
from src.crawler.arxiv_crawler import ArXivCrawler
from src.parser.pdf_parser import PDFParser
from src.extractor.innovation_extractor import InnovationExtractor
from src.generator.idea_generator import IdeaGenerator


def main():
    """主应用函数"""
    st.set_page_config(
        page_title="智能论文创新点生成器",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧠 智能论文创新点生成器")
    st.markdown("基于ArXiv论文分析，提取创新点并生成新的研究方向")
    
    # 侧边栏
    with st.sidebar:
        st.header("📋 功能导航")
        page = st.selectbox(
            "选择功能",
            ["论文搜索", "论文解析", "创新点提取", "想法生成", "结果查看"]
        )
        
        st.header("⚙️ 设置")
        max_papers = st.slider("最大论文数量", 5, 100, 20)
        use_ai = st.checkbox("使用AI模型", value=True)
        
        if use_ai:
            ai_model = st.selectbox("AI模型", ["OpenAI GPT-4", "Claude-3", "DeepSeek", "自动选择"])
            provider_map = {
                "OpenAI GPT-4": "openai",
                "Claude-3": "anthropic",
                "DeepSeek": "deepseek",
                "自动选择": settings.AI_PROVIDER
            }
            provider = provider_map[ai_model] if ai_model in provider_map else str(settings.AI_PROVIDER)
    
    # 主内容区域
    if page == "论文搜索":
        show_paper_search_page(max_papers)
    elif page == "论文解析":
        show_paper_parsing_page()
    elif page == "创新点提取":
        show_innovation_extraction_page(use_ai, str(ai_model), provider)
    elif page == "想法生成":
        show_idea_generation_page(use_ai, str(ai_model), provider)
    elif page == "结果查看":
        show_results_page()


def show_paper_search_page(max_papers: int):
    """论文搜索页面"""
    st.header("🔍 论文搜索")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "搜索查询",
            placeholder="例如：machine learning, deep learning, transformer"
        )
        
        search_options = st.expander("高级搜索选项")
        with search_options:
            col_a, col_b = st.columns(2)
            with col_a:
                category = st.selectbox(
                    "论文类别",
                    ["全部", "cs.AI", "cs.LG", "cs.CV", "cs.NLP", "cs.CL"]
                )
                sort_by = st.selectbox("排序方式", ["提交日期", "相关性", "引用次数"])
            
            with col_b:
                date_range = st.selectbox("时间范围", ["全部", "最近一周", "最近一月", "最近三月"])
                max_results = int(st.number_input("最大结果数", min_value=1, max_value=max_papers, value=10))
    
    with col2:
        st.subheader("搜索统计")
        if st.button("🔍 开始搜索", type="primary"):
            if search_query:
                with st.spinner("正在搜索论文..."):
                    try:
                        crawler = ArXivCrawler()
                        
                        # 构建搜索查询
                        query = search_query
                        if category != "全部":
                            query += f" AND cat:{category}"
                        
                        papers = crawler.search_papers(query, max_results)
                        
                        if papers:
                            st.success(f"找到 {len(papers)} 篇论文")
                            
                            # 显示论文列表
                            st.subheader("📄 搜索结果")
                            for i, paper in enumerate(papers, 1):
                                with st.expander(f"{i}. {paper.title}"):
                                    st.write(f"**作者:** {', '.join(paper.authors)}")
                                    st.write(f"**摘要:** {paper.abstract[:300]}...")
                                    st.write(f"**类别:** {', '.join(paper.categories)}")
                                    st.write(f"**发布日期:** {paper.published_date.strftime('%Y-%m-%d')}")
                            
                            # 下载选项
                            if st.button("📥 下载论文"):
                                with st.spinner("正在下载论文..."):
                                    downloaded = crawler.download_papers(papers)
                                    st.success(f"成功下载 {len(downloaded)} 篇论文")
                        else:
                            st.warning("未找到相关论文")
                            
                    except Exception as e:
                        st.error(f"搜索失败: {e}")
            else:
                st.warning("请输入搜索查询")


def show_paper_parsing_page():
    """论文解析页面"""
    st.header("📖 论文解析")
    
    # 检查是否有PDF文件
    pdf_dir = settings.DATA_DIR / "papers"
    pdf_files = list(pdf_dir.glob("*.pdf")) if pdf_dir.exists() else []
    
    if not pdf_files:
        st.warning("未找到PDF文件，请先下载论文")
        return
    
    st.subheader(f"📁 发现 {len(pdf_files)} 个PDF文件")
    
    # 显示文件列表
    for pdf_file in pdf_files:
        st.write(f"📄 {pdf_file.name}")
    
    if st.button("🔍 开始解析", type="primary"):
        with st.spinner("正在解析论文..."):
            try:
                parser = PDFParser()
                output_dir = settings.DATA_DIR / "extracted"
                
                parsed_papers = parser.batch_parse_papers(pdf_dir, output_dir)
                
                if parsed_papers:
                    st.success(f"成功解析 {len(parsed_papers)} 篇论文")
                    
                    # 显示解析结果
                    st.subheader("📊 解析统计")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("总论文数", len(parsed_papers))
                    
                    with col2:
                        total_sections = sum(len(paper.sections) for paper in parsed_papers)
                        st.metric("总章节数", total_sections)
                    
                    with col3:
                        avg_sections = total_sections / len(parsed_papers) if parsed_papers else 0
                        st.metric("平均章节数", f"{avg_sections:.1f}")
                    
                    # 显示解析详情
                    st.subheader("📋 解析详情")
                    for paper in parsed_papers:
                        with st.expander(f"📄 {paper.title}"):
                            st.write(f"**摘要:** {paper.abstract[:200]}...")
                            st.write(f"**章节数:** {len(paper.sections)}")
                            st.write(f"**参考文献数:** {len(paper.references)}")
                            
                            if paper.sections:
                                st.write("**章节列表:**")
                                for section in paper.sections[:5]:  # 显示前5个章节
                                    st.write(f"- {section.title}")
                else:
                    st.error("解析失败")
                    
            except Exception as e:
                st.error(f"解析失败: {e}")


def show_innovation_extraction_page(use_ai: bool, ai_model: str, provider: str):
    """创新点提取页面"""
    st.header("💡 创新点提取")
    
    # 检查是否有解析后的论文
    extracted_dir = settings.DATA_DIR / "extracted"
    json_files = list(extracted_dir.glob("*_parsed.json")) if extracted_dir.exists() else []
    
    if not json_files:
        st.warning("未找到解析后的论文，请先解析论文")
        return
    
    st.subheader(f"📁 发现 {len(json_files)} 个解析文件")
    
    if not use_ai:
        st.warning("AI功能已禁用，无法提取创新点")
        return
    
    if st.button("🔍 开始提取", type="primary"):
        with st.spinner("正在提取创新点..."):
            try:
                extractor = InnovationExtractor()
                
                # 加载解析后的论文
                parsed_papers = []
                for json_file in json_files:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 这里需要将JSON数据转换为ParsedPaper对象
                        # 简化处理，直接使用文本内容
                        parsed_papers.append({
                            'title': data.get('title', ''),
                            'full_text': data.get('full_text', '')
                        })
                
                # 提取创新点
                output_dir = settings.DATA_DIR / "innovations"
                extracted_innovations = []
                
                for paper in parsed_papers[:5]:  # 限制处理数量
                    extracted = extractor.extract_innovations(
                        paper['full_text'], 
                        paper['title'],
                        use_model="auto"
                    )
                    if extracted:
                        extracted_innovations.append(extracted)
                
                if extracted_innovations:
                    st.success(f"成功提取 {len(extracted_innovations)} 篇论文的创新点")
                    
                    # 显示提取结果
                    st.subheader("📊 提取统计")
                    total_innovations = sum(len(ext.innovations) for ext in extracted_innovations)
                    st.metric("总创新点数", total_innovations)
                    
                    # 显示创新点详情
                    st.subheader("💡 创新点详情")
                    for extracted in extracted_innovations:
                        with st.expander(f"📄 {extracted.paper_title}"):
                            st.write(f"**创新点数量:** {len(extracted.innovations)}")
                            st.write(f"**总结:** {extracted.summary[:200]}...")
                            
                            for i, innovation in enumerate(extracted.innovations, 1):
                                st.write(f"**创新点 {i}:** {innovation.title}")
                                st.write(f"描述: {innovation.description[:150]}...")
                                st.write(f"类别: {innovation.category}")
                                st.write(f"新颖性: {innovation.novelty_score:.2f}")
                                st.write("---")
                else:
                    st.error("提取失败")
                    
            except Exception as e:
                st.error(f"提取失败: {e}")


def show_idea_generation_page(use_ai: bool, ai_model: str, provider: str):
    """想法生成页面"""
    st.header("💡 想法生成")
    
    # 检查是否有提取的创新点
    innovations_dir = settings.DATA_DIR / "innovations"
    innovation_files = list(innovations_dir.glob("*_innovations.json")) if innovations_dir.exists() else []
    
    if not innovation_files:
        st.warning("未找到创新点文件，请先提取创新点")
        return
    
    st.subheader(f"📁 发现 {len(innovation_files)} 个创新点文件")
    
    topic = st.text_input("研究主题", placeholder="例如：深度学习在自然语言处理中的应用")
    
    if st.button("🚀 生成想法", type="primary"):
        if not topic:
            st.warning("请输入研究主题")
            return
        
        with st.spinner("正在生成想法..."):
            try:
                generator = IdeaGenerator()
                
                # 加载创新点
                innovations_list = []
                for json_file in innovation_files:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 这里需要将JSON数据转换为ExtractedInnovations对象
                        # 简化处理
                        innovations_list.append(data)
                
                # 生成想法
                result = generator.generate_ideas_from_innovations(innovations_list, topic)
                
                if result:
                    st.success(f"成功生成 {len(result.generated_ideas)} 个新想法")
                    
                    # 显示生成结果
                    st.subheader("📊 生成统计")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("生成想法数", len(result.generated_ideas))
                    
                    with col2:
                        avg_novelty = sum(idea.novelty_score for idea in result.generated_ideas) / len(result.generated_ideas)
                        st.metric("平均新颖性", f"{avg_novelty:.2f}")
                    
                    with col3:
                        avg_feasibility = sum(idea.feasibility_score for idea in result.generated_ideas) / len(result.generated_ideas)
                        st.metric("平均可行性", f"{avg_feasibility:.2f}")
                    
                    # 显示想法详情
                    st.subheader("💡 生成的想法")
                    for i, idea in enumerate(result.generated_ideas, 1):
                        with st.expander(f"💡 {idea.title}"):
                            st.write(f"**描述:** {idea.description}")
                            st.write(f"**来源创新点:** {', '.join(idea.source_innovations)}")
                            st.write(f"**组合类型:** {idea.combination_type}")
                            st.write(f"**可行性:** {idea.feasibility_score:.2f}")
                            st.write(f"**新颖性:** {idea.novelty_score:.2f}")
                            st.write(f"**潜在影响:** {idea.impact_potential:.2f}")
                            st.write(f"**实施路径:** {idea.implementation_path}")
                            
                            if idea.research_directions:
                                st.write("**研究方向:**")
                                for direction in idea.research_directions:
                                    st.write(f"- {direction}")
                    
                    # 保存结果
                    output_file = settings.DATA_DIR / "results" / f"{topic.replace(' ', '_')}_ideas.json"
                    generator.save_generation_result(result, output_file)
                    st.success(f"结果已保存到: {output_file}")
                else:
                    st.error("生成失败")
                    
            except Exception as e:
                st.error(f"生成失败: {e}")


def show_results_page():
    """结果查看页面"""
    st.header("📊 结果查看")
    
    # 检查结果文件
    results_dir = settings.DATA_DIR / "results"
    result_files = list(results_dir.glob("*.json")) if results_dir.exists() else []
    
    if not result_files:
        st.warning("未找到结果文件")
        return
    
    st.subheader(f"📁 发现 {len(result_files)} 个结果文件")
    
    # 选择要查看的结果文件
    selected_file = st.selectbox("选择结果文件", result_files)
    
    if selected_file and st.button("📊 加载结果"):
        try:
            with open(selected_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            st.success(f"成功加载结果: {selected_file.name}")
            
            # 显示基本信息
            st.subheader("📋 基本信息")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**研究主题:** {data.get('topic', 'N/A')}")
                st.write(f"**生成想法数:** {len(data.get('generated_ideas', []))}")
            
            with col2:
                metadata = data.get('generation_metadata', {})
                st.write(f"**总创新点数:** {metadata.get('total_innovations', 'N/A')}")
                st.write(f"**总论文数:** {metadata.get('total_papers', 'N/A')}")
            
            # 显示分析总结
            st.subheader("📈 分析总结")
            st.text(data.get('analysis_summary', 'N/A'))
            
            # 创建可视化图表
            st.subheader("📊 可视化分析")
            
            ideas = data.get('generated_ideas', [])
            if ideas:
                # 创建数据框
                df = pd.DataFrame([
                    {
                        'title': idea['title'],
                        'novelty_score': idea['novelty_score'],
                        'feasibility_score': idea['feasibility_score'],
                        'impact_potential': idea['impact_potential'],
                        'combination_type': idea['combination_type']
                    }
                    for idea in ideas
                ])
                
                # 散点图：新颖性 vs 可行性
                fig1 = px.scatter(
                    df, x='novelty_score', y='feasibility_score',
                    title='创新点分布：新颖性 vs 可行性',
                    hover_data=['title']
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                # 条形图：按组合类型统计
                type_counts = df['combination_type'].value_counts()
                fig2 = px.bar(
                    x=type_counts.index, y=type_counts.values,
                    title='想法类型分布'
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # 雷达图：平均评分
                avg_scores = {
                    '新颖性': df['novelty_score'].mean(),
                    '可行性': df['feasibility_score'].mean(),
                    '潜在影响': df['impact_potential'].mean()
                }
                
                fig3 = go.Figure()
                fig3.add_trace(go.Scatterpolar(
                    r=list(avg_scores.values()),
                    theta=list(avg_scores.keys()),
                    fill='toself',
                    name='平均评分'
                ))
                fig3.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    title='平均评分雷达图'
                )
                st.plotly_chart(fig3, use_container_width=True)
            
        except Exception as e:
            st.error(f"加载结果失败: {e}")


if __name__ == "__main__":
    main() 