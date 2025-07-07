"""
FastAPI 应用 - Vercel 部署版本
"""
import os
import sys
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.settings import settings
from src.crawler.arxiv_crawler import ArXivCrawler
from src.parser.pdf_parser import PDFParser
from src.extractor.innovation_extractor import InnovationExtractor
from src.generator.idea_generator import IdeaGenerator

app = FastAPI(
    title="智能论文创新点生成器 API",
    description="基于 ArXiv 论文分析的创新点生成服务",
    version="1.0.0"
)

# 线程池执行器
executor = ThreadPoolExecutor(max_workers=2)

# 请求模型
class SearchRequest(BaseModel):
    query: str
    max_papers: int = 10

class GenerateRequest(BaseModel):
    query: str
    max_papers: int = 10

# 响应模型
class SearchResponse(BaseModel):
    success: bool
    message: str
    papers: List[Dict] = []
    session_id: str = ""

class GenerateResponse(BaseModel):
    success: bool
    message: str
    session_id: str = ""
    results: Optional[Dict] = None

# 全局变量存储会话数据（在生产环境中应该使用数据库）
session_storage = {}

@app.get("/")
async def root():
    """根路径返回 HTML 页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>智能论文创新点生成器</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
            input, select { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            button { background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; }
            button:hover { background: #5a6fd8; }
            .result { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px; display: none; }
            .loading { text-align: center; color: #666; }
            .error { color: #dc3545; }
            .success { color: #28a745; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 智能论文创新点生成器</h1>
            <form id="generateForm">
                <div class="form-group">
                    <label for="query">研究主题</label>
                    <input type="text" id="query" name="query" placeholder="例如：machine learning, transformer, computer vision" required>
                </div>
                <div class="form-group">
                    <label for="max_papers">最大论文数量</label>
                    <select id="max_papers" name="max_papers">
                        <option value="5">5篇</option>
                        <option value="10" selected>10篇</option>
                        <option value="15">15篇</option>
                        <option value="20">20篇</option>
                    </select>
                </div>
                <button type="submit">🚀 开始生成创新点</button>
            </form>
            <div id="result" class="result">
                <div id="loading" class="loading">正在处理中，请稍候...</div>
                <div id="content"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('generateForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const query = document.getElementById('query').value;
                const maxPapers = document.getElementById('max_papers').value;
                
                document.getElementById('result').style.display = 'block';
                document.getElementById('loading').style.display = 'block';
                document.getElementById('content').innerHTML = '';
                
                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            max_papers: parseInt(maxPapers)
                        })
                    });
                    
                    const data = await response.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.success) {
                        document.getElementById('content').innerHTML = `
                            <div class="success">
                                <h3>✅ 生成成功！</h3>
                                <p><strong>会话ID:</strong> ${data.session_id}</p>
                                <p><strong>处理结果:</strong> ${data.message}</p>
                                <div style="margin-top: 20px;">
                                    <a href="/api/results/${data.session_id}" target="_blank" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">查看详细结果</a>
                                </div>
                            </div>
                        `;
                    } else {
                        document.getElementById('content').innerHTML = `
                            <div class="error">
                                <h3>❌ 生成失败</h3>
                                <p>${data.message}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').innerHTML = `
                        <div class="error">
                            <h3>❌ 网络错误</h3>
                            <p>请检查网络连接后重试</p>
                        </div>
                    `;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/search", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """搜索论文 API"""
    try:
        # 创建临时会话
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 在后台执行搜索
        def search_task():
            crawler = ArXivCrawler()
            papers = crawler.search_papers(request.query, request.max_papers)
            return papers
        
        # 使用线程池执行
        loop = asyncio.get_event_loop()
        papers = await loop.run_in_executor(executor, search_task)
        
        # 转换为可序列化的格式
        papers_data = [
            {
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "authors": paper.authors,
                "abstract": paper.abstract,
                "categories": paper.categories,
                "published_date": paper.published_date.isoformat(),
                "pdf_url": paper.pdf_url
            }
            for paper in papers
        ]
        
        # 存储会话数据
        session_storage[session_id] = {
            "query": request.query,
            "papers": papers_data,
            "created_at": datetime.now().isoformat()
        }
        
        return SearchResponse(
            success=True,
            message=f"成功搜索到 {len(papers)} 篇论文",
            papers=papers_data,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_innovations(request: GenerateRequest):
    """生成创新点 API"""
    try:
        # 创建临时会话
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 在后台执行完整流程
        def generate_task():
            results = {}
            
            # 1. 搜索论文
            crawler = ArXivCrawler()
            papers = crawler.search_papers(request.query, request.max_papers)
            results["papers_count"] = len(papers)
            
            # 2. 下载论文 (限制数量以避免超时)
            limited_papers = papers[:min(5, len(papers))]  # 最多5篇避免超时
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                papers_dir = temp_path / "papers"
                papers_dir.mkdir(exist_ok=True)
                
                # 设置临时目录
                crawler.papers_dir = papers_dir
                downloaded_files = crawler.download_papers(limited_papers)
                results["downloaded_count"] = len(downloaded_files)
                
                if not downloaded_files:
                    return {"error": "没有成功下载的论文"}
                
                # 3. 解析论文
                parser = PDFParser()
                extracted_dir = temp_path / "extracted"
                extracted_dir.mkdir(exist_ok=True)
                
                parsed_papers = parser.batch_parse_papers(papers_dir, extracted_dir)
                results["parsed_count"] = len(parsed_papers)
                
                if not parsed_papers:
                    return {"error": "没有成功解析的论文"}
                
                # 4. 提取创新点
                extractor = InnovationExtractor()
                innovations_list = []
                
                for paper in parsed_papers:
                    try:
                        # 获取论文标题，如果没有则使用文件名
                        paper_title = paper.title if paper.title else "未知论文"
                        # 获取论文内容
                        paper_content = paper.full_text if paper.full_text else ""
                        innovations = extractor.extract_innovations(paper_content, paper_title)
                        if innovations:
                            innovations_list.append(innovations)
                    except Exception as e:
                        print(f"提取创新点失败: {e}")
                        continue
                
                results["innovations_count"] = len(innovations_list)
                
                if not innovations_list:
                    return {"error": "没有成功提取的创新点"}
                
                # 5. 生成新想法
                generator = IdeaGenerator()
                generated_ideas = generator.generate_ideas_from_innovations(innovations_list, request.query)
                
                if generated_ideas:
                    results["generated_ideas_count"] = len(generated_ideas.generated_ideas)
                    results["success"] = True
                else:
                    results["error"] = "想法生成失败"
                
                return results
        
        # 使用线程池执行
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(executor, generate_task)
        
        if "error" in results:
            return GenerateResponse(
                success=False,
                message=results["error"],
                session_id=session_id
            )
        
        # 存储会话数据
        session_storage[session_id] = {
            "query": request.query,
            "results": results,
            "created_at": datetime.now().isoformat()
        }
        
        return GenerateResponse(
            success=True,
            message=f"成功处理 {results.get('papers_count', 0)} 篇论文，生成 {results.get('generated_ideas_count', 0)} 个创新想法",
            session_id=session_id,
            results=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

@app.get("/api/results/{session_id}")
async def get_results(session_id: str):
    """获取会话结果"""
    if session_id not in session_storage:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session_data = session_storage[session_id]
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>生成结果 - {session_data['query']}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
            .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 10px 0; text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; }}
            .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
            .back-btn {{ display: inline-block; background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">← 返回首页</a>
            <h1>📊 生成结果</h1>
            <p><strong>搜索主题:</strong> {session_data['query']}</p>
            <p><strong>创建时间:</strong> {session_data['created_at']}</p>
            
            <div class="stat-card">
                <div class="stat-number">{session_data.get('results', {}).get('papers_count', 0)}</div>
                <div class="stat-label">搜索到的论文数量</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number">{session_data.get('results', {}).get('downloaded_count', 0)}</div>
                <div class="stat-label">成功下载的论文</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number">{session_data.get('results', {}).get('parsed_count', 0)}</div>
                <div class="stat-label">成功解析的论文</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number">{session_data.get('results', {}).get('innovations_count', 0)}</div>
                <div class="stat-label">提取的创新点数量</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-number">{session_data.get('results', {}).get('generated_ideas_count', 0)}</div>
                <div class="stat-label">生成的新想法数量</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 如果直接运行此文件
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 