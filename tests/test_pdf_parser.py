"""
PDF解析模块测试
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.parser.pdf_parser import PDFParser, PaperSection, ParsedPaper


class TestPDFParser:
    """PDF解析器测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.parser = PDFParser()
        self.test_pdf_path = Path("test_paper.pdf")
    
    def test_init(self):
        """测试初始化"""
        assert self.parser is not None
        assert len(self.parser.section_patterns) > 0
    
    @patch('src.parser.pdf_parser.pdfplumber')
    def test_extract_text_from_pdf_pdfplumber_success(self, mock_pdfplumber):
        """测试pdfplumber成功提取文本"""
        # 模拟pdfplumber成功
        mock_pdf = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test page content"
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        result = self.parser.extract_text_from_pdf(self.test_pdf_path)
        
        assert result == "Test page content\n"
        mock_pdfplumber.open.assert_called_once_with(self.test_pdf_path)
    
    @patch('src.parser.pdf_parser.pdfplumber')
    @patch('src.parser.pdf_parser.PyPDF2')
    def test_extract_text_from_pdf_fallback_to_pypdf2(self, mock_pypdf2, mock_pdfplumber):
        """测试pdfplumber失败时回退到PyPDF2"""
        # 模拟pdfplumber失败
        mock_pdfplumber.open.side_effect = Exception("pdfplumber error")
        
        # 模拟PyPDF2成功
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test page content"
        mock_reader.pages = [mock_page]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        with patch('builtins.open', mock_open()):
            result = self.parser.extract_text_from_pdf(self.test_pdf_path)
        
        assert result == "Test page content\n"
        mock_pypdf2.PdfReader.assert_called_once()
    
    @patch('src.parser.pdf_parser.pdfplumber')
    def test_extract_text_from_pdf_failure(self, mock_pdfplumber):
        """测试PDF提取失败"""
        mock_pdfplumber.open.side_effect = Exception("PDF error")
        
        result = self.parser.extract_text_from_pdf(self.test_pdf_path)
        
        assert result is None
    
    @patch('src.parser.pdf_parser.PyPDF2')
    def test_extract_metadata_success(self, mock_pypdf2):
        """测试成功提取元数据"""
        mock_reader = Mock()
        mock_reader.metadata = {
            '/Title': 'Test Paper',
            '/Author': 'Test Author',
            '/Subject': 'Test Subject',
            '/Creator': 'Test Creator',
            '/Producer': 'Test Producer'
        }
        mock_reader.pages = [Mock(), Mock()]  # 2页
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        with patch('builtins.open', mock_open()):
            result = self.parser.extract_metadata(self.test_pdf_path)
        
        expected = {
            'title': 'Test Paper',
            'author': 'Test Author',
            'subject': 'Test Subject',
            'creator': 'Test Creator',
            'producer': 'Test Producer',
            'pages': 2
        }
        assert result == expected
    
    @patch('src.parser.pdf_parser.PyPDF2')
    def test_extract_metadata_failure(self, mock_pypdf2):
        """测试元数据提取失败"""
        mock_pypdf2.PdfReader.side_effect = Exception("Metadata error")
        
        with patch('builtins.open', mock_open()):
            result = self.parser.extract_metadata(self.test_pdf_path)
        
        assert result == {}
    
    def test_identify_sections(self):
        """测试章节识别"""
        text = """
        ABSTRACT
        This is the abstract content.
        
        1. INTRODUCTION
        This is the introduction.
        
        2. METHODOLOGY
        This is the methodology.
        
        REFERENCES
        [1] Test reference
        """
        
        sections = self.parser.identify_sections(text)
        
        assert len(sections) == 3
        assert sections[0].title == "ABSTRACT"
        assert sections[1].title == "INTRODUCTION"
        assert sections[2].title == "METHODOLOGY"
    
    def test_extract_abstract(self):
        """测试摘要提取"""
        text = """
        ABSTRACT
        This is a test abstract that contains important information about the paper.
        
        1. INTRODUCTION
        This is the introduction section.
        """
        
        abstract = self.parser.extract_abstract(text)
        
        assert "test abstract" in abstract.lower()
    
    def test_extract_abstract_not_found(self):
        """测试未找到摘要"""
        text = """
        1. INTRODUCTION
        This is the introduction section.
        
        2. METHODOLOGY
        This is the methodology section.
        """
        
        abstract = self.parser.extract_abstract(text)
        
        assert abstract == ""
    
    def test_extract_references(self):
        """测试参考文献提取"""
        text = """
        2. METHODOLOGY
        This is the methodology.
        
        REFERENCES
        [1] Author A. Title A. Journal A, 2020.
        [2] Author B. Title B. Journal B, 2021.
        
        APPENDIX
        Additional information.
        """
        
        references = self.parser.extract_references(text)
        
        assert len(references) == 2
        assert "Author A" in references[0]
        assert "Author B" in references[1]
    
    def test_extract_references_not_found(self):
        """测试未找到参考文献"""
        text = """
        1. INTRODUCTION
        This is the introduction.
        
        2. CONCLUSION
        This is the conclusion.
        """
        
        references = self.parser.extract_references(text)
        
        assert references == []
    
    @patch.object(PDFParser, 'extract_text_from_pdf')
    @patch.object(PDFParser, 'extract_metadata')
    @patch.object(PDFParser, 'identify_sections')
    @patch.object(PDFParser, 'extract_abstract')
    @patch.object(PDFParser, 'extract_references')
    def test_parse_paper_success(self, mock_extract_refs, mock_extract_abstract, 
                                mock_identify_sections, mock_extract_metadata, 
                                mock_extract_text):
        """测试成功解析论文"""
        # 模拟各个方法返回结果
        mock_extract_text.return_value = "Full text content"
        mock_extract_metadata.return_value = {
            'title': 'Test Paper',
            'author': 'Test Author'
        }
        mock_identify_sections.return_value = [
            PaperSection("ABSTRACT", "Abstract content", 1, 0, 0),
            PaperSection("INTRODUCTION", "Intro content", 1, 0, 0)
        ]
        mock_extract_abstract.return_value = "Abstract content"
        mock_extract_refs.return_value = ["Ref 1", "Ref 2"]
        
        result = self.parser.parse_paper(self.test_pdf_path)
        
        assert result is not None
        assert result.title == "Test Paper"
        assert result.abstract == "Abstract content"
        assert len(result.sections) == 2
        assert len(result.references) == 2
        assert result.full_text == "Full text content"
    
    @patch.object(PDFParser, 'extract_text_from_pdf')
    def test_parse_paper_no_text(self, mock_extract_text):
        """测试解析论文时没有提取到文本"""
        mock_extract_text.return_value = None
        
        result = self.parser.parse_paper(self.test_pdf_path)
        
        assert result is None
    
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_parsed_paper(self, mock_file, mock_json_dump):
        """测试保存解析结果"""
        parsed_paper = ParsedPaper(
            title="Test Paper",
            abstract="Test abstract",
            authors=["Author 1", "Author 2"],
            sections=[],
            references=[],
            full_text="Test content",
            metadata={}
        )
        
        output_path = Path("test_output.json")
        self.parser.save_parsed_paper(parsed_paper, output_path)
        
        mock_file.assert_called_once_with(output_path, 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
    
    @patch.object(PDFParser, 'parse_paper')
    def test_batch_parse_papers(self, mock_parse_paper):
        """测试批量解析论文"""
        # 模拟解析结果
        mock_paper = Mock()
        mock_parse_paper.return_value = mock_paper
        
        # 模拟PDF文件
        pdf_dir = Path("test_pdfs")
        output_dir = Path("test_output")
        
        with patch.object(Path, 'glob') as mock_glob:
            mock_glob.return_value = [
                Path("test1.pdf"),
                Path("test2.pdf")
            ]
            
            with patch.object(Path, 'mkdir') as mock_mkdir:
                result = self.parser.batch_parse_papers(pdf_dir, output_dir)
        
        assert len(result) == 2
        assert mock_parse_paper.call_count == 2
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestPaperSection:
    """论文章节测试类"""
    
    def test_paper_section_creation(self):
        """测试章节创建"""
        section = PaperSection(
            title="Test Section",
            content="Test content",
            level=1,
            start_page=0,
            end_page=10
        )
        
        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert section.level == 1
        assert section.start_page == 0
        assert section.end_page == 10


class TestParsedPaper:
    """解析后论文测试类"""
    
    def test_parsed_paper_creation(self):
        """测试解析后论文创建"""
        paper = ParsedPaper(
            title="Test Paper",
            abstract="Test abstract",
            authors=["Author 1", "Author 2"],
            sections=[],
            references=[],
            full_text="Test content",
            metadata={"key": "value"}
        )
        
        assert paper.title == "Test Paper"
        assert paper.abstract == "Test abstract"
        assert len(paper.authors) == 2
        assert paper.full_text == "Test content"
        assert paper.metadata["key"] == "value" 