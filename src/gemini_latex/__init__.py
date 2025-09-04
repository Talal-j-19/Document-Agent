"""
Gemini LaTeX Compiler

A Python package that uses Google's Gemini AI to generate LaTeX code and compile it to PDF.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .gemini_client import GeminiClient
from .latex_compiler import LaTeXCompiler
from .main import GeminiLaTeXProcessor

__all__ = ["GeminiClient", "LaTeXCompiler", "GeminiLaTeXProcessor"]
