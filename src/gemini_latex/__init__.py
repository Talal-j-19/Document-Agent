"""
Gemini LaTeX Compiler

A Python package that uses Google's Gemini AI to generate LaTeX code and compile it to PDF.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .main import GeminiLaTeXProcessor
from .gemini_client import GeminiClient
from .latex_compiler import LaTeXCompiler
from .document_editor import DocumentEditor
from .pdf_viewer import PDFViewer
from .interactive_session import InteractiveSession

__all__ = [
    "GeminiLaTeXProcessor", 
    "GeminiClient", 
    "LaTeXCompiler",
    "DocumentEditor",
    "PDFViewer",
    "InteractiveSession"
]
