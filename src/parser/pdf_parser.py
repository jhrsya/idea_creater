"""
PDF论文解析模块
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pdfplumber
import PyPDF2
from loguru import logger


@dataclass
class PaperSection:
    """论文章节"""
    title: str
    content: str
    level: int
    start_page: int
    end_page: int


@dataclass
class ParsedPaper:
    """解析后的论文"""
    title: str
    abstract: str
    authors: List[str]
    sections: List[PaperSection]
    references: List[str]
    full_text: str
    metadata: Dict


class PDFParser:
    """PDF论文解析器"""
    
    def __init__(self):
        self.section_patterns = [
            r'^\d+\.\s*([A-Z][A-Z\s]+)$',  # 1. INTRODUCTION
            r'^([A-Z][A-Z\s]+)$',  # ABSTRACT, REFERENCES
            r'^\d+\.\d+\s*([A-Z][A-Z\s]+)$',  # 1.1 Background
            r'^([A-Z][a-z\s]+):$',  # Abstract:, Conclusion:
        ]
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """
        从PDF提取文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本内容
        """
        try:
            logger.info(f"开始解析PDF: {pdf_path}")
            
            # 尝试使用pdfplumber
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return text
            except Exception as e:
                logger.warning(f"pdfplumber解析失败，尝试PyPDF2: {e}")
                
                # 备用方案：使用PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
                    
        except Exception as e:
            logger.error(f"PDF解析失败 {pdf_path}: {e}")
            return None
    
    def extract_metadata(self, pdf_path: Path) -> Dict:
        """
        提取PDF元数据
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            元数据字典
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = reader.metadata
                return {
                    'title': metadata.get('/Title', ''),
                    'author': metadata.get('/Author', ''),
                    'subject': metadata.get('/Subject', ''),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', ''),
                    'pages': len(reader.pages)
                }
        except Exception as e:
            logger.error(f"提取元数据失败 {pdf_path}: {e}")
            return {}
    
    def identify_sections(self, text: str) -> List[PaperSection]:
        """
        识别论文章节
        
        Args:
            text: 论文文本
            
        Returns:
            章节列表
        """
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是章节标题
            is_section = False
            section_title = ""
            
            for pattern in self.section_patterns:
                match = re.match(pattern, line)
                if match:
                    is_section = True
                    section_title = match.group(1).strip()
                    break
            
            if is_section:
                # 保存前一个章节
                if current_section and current_content:
                    current_section.content = '\n'.join(current_content)
                    sections.append(current_section)
                
                # 开始新章节
                level = 1 if '.' in line else 2
                current_section = PaperSection(
                    title=section_title,
                    content="",
                    level=level,
                    start_page=i,
                    end_page=i
                )
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # 保存最后一个章节
        if current_section and current_content:
            current_section.content = '\n'.join(current_content)
            sections.append(current_section)
        
        return sections
    
    def extract_abstract(self, text: str) -> str:
        """
        提取摘要
        
        Args:
            text: 论文文本
            
        Returns:
            摘要内容
        """
        # 查找摘要部分
        abstract_patterns = [
            r'ABSTRACT\s*\n(.*?)(?=\n[A-Z]+\s*\n|\n\d+\.\s*[A-Z]|\n[A-Z][a-z]+:)',
            r'Abstract\s*\n(.*?)(?=\n[A-Z]+\s*\n|\n\d+\.\s*[A-Z]|\n[A-Z][a-z]+:)',
            r'摘要\s*\n(.*?)(?=\n[A-Z]+\s*\n|\n\d+\.\s*[A-Z]|\n[A-Z][a-z]+:)',
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_references(self, text: str) -> List[str]:
        """
        提取参考文献
        
        Args:
            text: 论文文本
            
        Returns:
            参考文献列表
        """
        references = []
        
        # 查找参考文献部分
        ref_patterns = [
            r'REFERENCES\s*\n(.*?)(?=\n[A-Z]+\s*\n|$)',
            r'References\s*\n(.*?)(?=\n[A-Z]+\s*\n|$)',
            r'参考文献\s*\n(.*?)(?=\n[A-Z]+\s*\n|$)',
        ]
        
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                ref_text = match.group(1)
                # 分割参考文献条目
                ref_entries = re.split(r'\n\s*\[\d+\]', ref_text)
                for entry in ref_entries:
                    entry = entry.strip()
                    if entry:
                        references.append(entry)
                break
        
        return references
    
    def parse_paper(self, pdf_path: Path) -> Optional[ParsedPaper]:
        """
        解析完整论文
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            解析后的论文对象
        """
        try:
            logger.info(f"开始解析论文: {pdf_path}")
            
            # 提取文本
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                return None
            
            # 提取元数据
            metadata = self.extract_metadata(pdf_path)
            
            # 识别章节
            sections = self.identify_sections(text)
            
            # 提取摘要
            abstract = self.extract_abstract(text)
            
            # 提取参考文献
            references = self.extract_references(text)
            
            # 构建解析结果
            parsed_paper = ParsedPaper(
                title=metadata.get('title', ''),
                abstract=abstract,
                authors=metadata.get('author', '').split(';') if metadata.get('author') else [],
                sections=sections,
                references=references,
                full_text=text,
                metadata=metadata
            )
            
            logger.info(f"论文解析完成: {pdf_path.name}")
            return parsed_paper
            
        except Exception as e:
            logger.error(f"解析论文失败 {pdf_path}: {e}")
            return None
    
    def save_parsed_paper(self, parsed_paper: ParsedPaper, output_path: Path):
        """
        保存解析结果
        
        Args:
            parsed_paper: 解析后的论文
            output_path: 输出文件路径
        """
        try:
            import json
            from datetime import datetime
            
            # 转换为可序列化的格式
            data = {
                'title': parsed_paper.title,
                'abstract': parsed_paper.abstract,
                'authors': parsed_paper.authors,
                'sections': [
                    {
                        'title': section.title,
                        'content': section.content,
                        'level': section.level,
                        'start_page': section.start_page,
                        'end_page': section.end_page
                    }
                    for section in parsed_paper.sections
                ],
                'references': parsed_paper.references,
                'metadata': parsed_paper.metadata,
                'parsed_at': datetime.now().isoformat()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"解析结果已保存: {output_path}")
            
        except Exception as e:
            logger.error(f"保存解析结果失败: {e}")
    
    def batch_parse_papers(self, pdf_dir: Path, output_dir: Path) -> List[ParsedPaper]:
        """
        批量解析论文
        
        Args:
            pdf_dir: PDF文件目录
            output_dir: 输出目录
            
        Returns:
            解析后的论文列表
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        parsed_papers = []
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        logger.info(f"开始批量解析 {len(pdf_files)} 个PDF文件")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"解析进度: {i}/{len(pdf_files)}")
            
            parsed_paper = self.parse_paper(pdf_file)
            if parsed_paper:
                # 保存解析结果
                output_file = output_dir / f"{pdf_file.stem}_parsed.json"
                self.save_parsed_paper(parsed_paper, output_file)
                parsed_papers.append(parsed_paper)
        
        logger.info(f"批量解析完成，成功解析 {len(parsed_papers)} 篇论文")
        return parsed_papers 