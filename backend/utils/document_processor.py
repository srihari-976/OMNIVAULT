"""
Document Processor Module
Handles text extraction from various file formats
"""

import os
import fitz  # PyMuPDF
from docx import Document
from PIL import Image
import pytesseract
from config import Config
import chardet

class DocumentProcessor:
    
    @staticmethod
    def detect_encoding(file_path):
        """Detect file encoding"""
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF using PyMuPDF"""
        try:
            text = ""
            doc = fitz.open(file_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
                text += f"\n\n--- Page {page_num + 1} ---\n\n"
            
            doc.close()
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + "\t"
                    text += "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_path):
        """Extract text from TXT file"""
        try:
            encoding = DocumentProcessor.detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding or 'utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error extracting text from TXT: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_image(file_path):
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return f"[Image file: {os.path.basename(file_path)} - OCR not available]"
    
    @staticmethod
    def extract_text_from_markdown(file_path):
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error extracting text from Markdown: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_code(file_path):
        """Extract text from code files"""
        try:
            encoding = DocumentProcessor.detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding or 'utf-8', errors='ignore') as f:
                code = f.read()
                # Add language identifier based on extension
                ext = os.path.splitext(file_path)[1][1:]
                return f"```{ext}\n{code}\n```"
        except Exception as e:
            print(f"Error extracting text from code file: {e}")
            return ""
    
    @staticmethod
    def process_document(file_path):
        """
        Unified document processing interface
        Returns: dict with metadata and extracted text
        """
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()[1:]
        
        print(f"Processing document: {filename} (type: {file_ext})")
        
        # Determine file type and extract text
        text = ""
        doc_type = "unknown"
        
        if file_ext == 'pdf':
            text = DocumentProcessor.extract_text_from_pdf(file_path)
            doc_type = "pdf"
        elif file_ext in ['docx', 'doc']:
            text = DocumentProcessor.extract_text_from_docx(file_path)
            doc_type = "docx"
        elif file_ext in ['txt']:
            text = DocumentProcessor.extract_text_from_txt(file_path)
            doc_type = "text"
        elif file_ext in ['md', 'markdown']:
            text = DocumentProcessor.extract_text_from_markdown(file_path)
            doc_type = "markdown"
        elif file_ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
            text = DocumentProcessor.extract_text_from_image(file_path)
            doc_type = "image"
        elif file_ext in ['py', 'js', 'java', 'cpp', 'c', 'html', 'css', 'json', 'xml']:
            text = DocumentProcessor.extract_text_from_code(file_path)
            doc_type = "code"
        else:
            # Try as text file
            text = DocumentProcessor.extract_text_from_txt(file_path)
            doc_type = "text"
        
        result = {
            "filename": filename,
            "file_path": file_path,
            "file_type": doc_type,
            "extension": file_ext,
            "text": text,
            "word_count": len(text.split()),
            "char_count": len(text),
            "success": len(text) > 0
        }
        
        print(f"  → Extracted {result['word_count']} words, {result['char_count']} characters")
        
        return result


if __name__ == "__main__":
    # Test document processing
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = DocumentProcessor.process_document(file_path)
        print(f"\nExtracted Text:\n{result['text'][:500]}...")
    else:
        print("Usage: python document_processor.py <file_path>")
