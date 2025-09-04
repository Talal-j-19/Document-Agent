"""
Main application module that integrates Gemini API and LaTeX compilation.
"""

import os
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from .gemini_client import GeminiClient
from .latex_compiler import LaTeXCompiler


class GeminiLaTeXProcessor:
    """Main class that handles the complete pipeline from prompt to PDF."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        latex_engine: str = "pdflatex",
        default_output_dir: Optional[str] = None
    ):
        """
        Initialize the Gemini LaTeX processor.
        
        Args:
            api_key: Gemini API key
            latex_engine: LaTeX engine to use for compilation
            default_output_dir: Default directory for output files
        """
        self.gemini_client = GeminiClient(api_key)
        self.latex_compiler = LaTeXCompiler(latex_engine)
        self.default_output_dir = default_output_dir or "output"
        
        # Ensure output directory exists
        Path(self.default_output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_and_compile(
        self, 
        prompt: str,
        output_filename: Optional[str] = None,
        context: Optional[str] = None,
        save_tex: bool = True
    ) -> Dict[str, Any]:
        """
        Complete pipeline: generate LaTeX from prompt and compile to PDF.
        
        Args:
            prompt: Description of the document to generate
            output_filename: Name for the output files (without extension)
            context: Additional context for LaTeX generation
            save_tex: Whether to save the generated .tex file
            
        Returns:
            Dictionary containing paths and compilation information
        """
        if output_filename is None:
            # Generate filename from prompt (simplified)
            output_filename = "document_" + str(hash(prompt))[:8]
        
        # Generate LaTeX code
        try:
            latex_code = self.gemini_client.generate_latex(prompt, context)
        except Exception as e:
            return {
                "success": False,
                "error": f"LaTeX generation failed: {str(e)}",
                "latex_code": None,
                "tex_file": None,
                "pdf_file": None,
                "compilation_log": None
            }
        
        # Set up output paths
        tex_file = os.path.join(self.default_output_dir, f"{output_filename}.tex")
        pdf_file = os.path.join(self.default_output_dir, f"{output_filename}.pdf")
        
        # Save LaTeX code if requested
        if save_tex:
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_code)
        
        # Compile to PDF
        try:
            compiled_pdf_path, compilation_log = self.latex_compiler.compile_latex_to_pdf(
                latex_code, pdf_file
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"LaTeX compilation failed: {str(e)}",
                "latex_code": latex_code,
                "tex_file": tex_file if save_tex else None,
                "pdf_file": None,
                "compilation_log": None
            }
        
        return {
            "success": True,
            "error": None,
            "latex_code": latex_code,
            "tex_file": tex_file if save_tex else None,
            "pdf_file": compiled_pdf_path,
            "compilation_log": compilation_log
        }
    
    def generate_latex_only(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate only LaTeX code without compilation.
        
        Args:
            prompt: Description of the document to generate
            context: Additional context for LaTeX generation
            
        Returns:
            Generated LaTeX code
        """
        return self.gemini_client.generate_latex(prompt, context)
    
    def compile_existing_latex(self, tex_file_path: str) -> Dict[str, Any]:
        """
        Compile an existing LaTeX file to PDF.
        
        Args:
            tex_file_path: Path to the existing .tex file
            
        Returns:
            Dictionary containing compilation information
        """
        try:
            pdf_path, compilation_log = self.latex_compiler.compile_from_file(tex_file_path)
            return {
                "success": True,
                "error": None,
                "pdf_file": pdf_path,
                "compilation_log": compilation_log
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Compilation failed: {str(e)}",
                "pdf_file": None,
                "compilation_log": None
            }
    
    def generate_with_custom_options(
        self,
        prompt: str,
        document_class: str = "article",
        packages: Optional[list] = None,
        custom_settings: Optional[Dict[str, Any]] = None,
        output_filename: Optional[str] = None,
        save_tex: bool = True
    ) -> Dict[str, Any]:
        """
        Generate LaTeX with custom options and compile to PDF.
        
        Args:
            prompt: Description of the document to generate
            document_class: LaTeX document class
            packages: List of LaTeX packages to include
            custom_settings: Custom LaTeX settings
            output_filename: Name for output files
            save_tex: Whether to save the .tex file
            
        Returns:
            Dictionary containing paths and compilation information
        """
        if output_filename is None:
            output_filename = "custom_document_" + str(hash(prompt))[:8]
        
        try:
            latex_code = self.gemini_client.generate_latex_with_options(
                prompt, document_class, packages, custom_settings
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"LaTeX generation failed: {str(e)}",
                "latex_code": None,
                "tex_file": None,
                "pdf_file": None,
                "compilation_log": None
            }
        
        # Set up output paths
        tex_file = os.path.join(self.default_output_dir, f"{output_filename}.tex")
        pdf_file = os.path.join(self.default_output_dir, f"{output_filename}.pdf")
        
        # Save LaTeX code if requested
        if save_tex:
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_code)
        
        # Compile to PDF
        try:
            compiled_pdf_path, compilation_log = self.latex_compiler.compile_latex_to_pdf(
                latex_code, pdf_file
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"LaTeX compilation failed: {str(e)}",
                "latex_code": latex_code,
                "tex_file": tex_file if save_tex else None,
                "pdf_file": None,
                "compilation_log": compilation_log if 'compilation_log' in locals() else None
            }
        
        return {
            "success": True,
            "error": None,
            "latex_code": latex_code,
            "tex_file": tex_file if save_tex else None,
            "pdf_file": compiled_pdf_path,
            "compilation_log": compilation_log
        }
