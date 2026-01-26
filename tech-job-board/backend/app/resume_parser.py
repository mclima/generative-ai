import PyPDF2
import docx
from typing import Optional
import io

class ResumeParser:
    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
    
    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        try:
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")
    
    @staticmethod
    def parse_txt(file_content: bytes) -> str:
        try:
            return file_content.decode('utf-8').strip()
        except Exception as e:
            raise ValueError(f"Error parsing TXT: {str(e)}")
    
    @classmethod
    def parse_resume(cls, file_content: bytes, filename: str) -> str:
        if filename.lower().endswith('.pdf'):
            return cls.parse_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            return cls.parse_docx(file_content)
        elif filename.lower().endswith('.txt'):
            return cls.parse_txt(file_content)
        else:
            raise ValueError("Unsupported file format. Please upload PDF, DOCX, or TXT file.")
