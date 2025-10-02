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
        save_tex: bool = True,
        retry_on_error: bool = True
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
        
        # --- ENGINE AUTO-SELECTION FOR ALTACV ---
        engine_to_use = self.latex_compiler.latex_engine
        if "\\documentclass" in latex_code and "altacv" in latex_code:
            if engine_to_use != "xelatex":
                # Switch to xelatex for altacv
                from .latex_compiler import LaTeXCompiler
                self.latex_compiler = LaTeXCompiler("xelatex")
                engine_to_use = "xelatex"
        # Compile to PDF with intelligent retry
        compilation_attempt = 1
        max_attempts = 2 if retry_on_error else 1
        
        while compilation_attempt <= max_attempts:
            try:
                compiled_pdf_path, compilation_log = self.latex_compiler.compile_latex_to_pdf(
                    latex_code, pdf_file
                )
                break  # Success, exit retry loop
                
            except Exception as e:
                error_msg = str(e)
                
                # If this is the last attempt or retry is disabled, return error
                if compilation_attempt >= max_attempts or not retry_on_error:
                    return {
                        "success": False,
                        "error": f"LaTeX compilation failed: {error_msg}",
                        "latex_code": latex_code,
                        "tex_file": tex_file if save_tex else None,
                        "pdf_file": None,
                        "compilation_log": compilation_log if 'compilation_log' in locals() else None
                    }
                
                # Try to fix common issues and regenerate LaTeX code
                if compilation_attempt < max_attempts:
                    print(f"Compilation attempt {compilation_attempt} failed. Trying to fix issues...")
                    
                    # Analyze error and create enhanced context  
                    current_log = compilation_log if 'compilation_log' in locals() and compilation_log else None
                    error_context = self._create_error_fix_context(error_msg, current_log)
                    enhanced_context = f"{context}\n\nIMPORTANT: Previous compilation failed with error: {error_msg}\n{error_context}" if context else error_context
                    
                    # Regenerate LaTeX code with error context
                    try:
                        latex_code = self.gemini_client.generate_latex(prompt, enhanced_context)
                        # Save the updated LaTeX code if requested
                        if save_tex:
                            with open(tex_file, 'w', encoding='utf-8') as f:
                                f.write(latex_code)
                    except Exception as regeneration_error:
                        return {
                            "success": False,
                            "error": f"LaTeX regeneration failed: {str(regeneration_error)}",
                            "latex_code": latex_code,
                            "tex_file": tex_file if save_tex else None,
                            "pdf_file": None,
                            "compilation_log": None
                        }
                
                compilation_attempt += 1
        
        return {
            "success": True,
            "error": None,
            "latex_code": latex_code,
            "tex_file": tex_file if save_tex else None,
            "pdf_file": compiled_pdf_path,
            "compilation_log": compilation_log
        }
    
    def _create_error_fix_context(self, error_msg: str, compilation_log: Optional[str] = None) -> str:
        """
        Create context for fixing LaTeX compilation errors.
        
        Args:
            error_msg: The error message from compilation
            compilation_log: The full compilation log
            
        Returns:
            Enhanced context string to help fix the error
        """
        fix_context = ["\nPlease fix the following LaTeX compilation issues:"]
        
        # Analyze common error patterns
        if "auto expansion is only possible with scalable fonts" in error_msg or (compilation_log and "auto expansion" in compilation_log):
            fix_context.extend([
                "- FONT EXPANSION ERROR: Remove or comment out \\usepackage{microtype} or switch to XeLaTeX/LuaLaTeX",
                "- Alternative: Use \\usepackage[activate={true,nocompatibility},final,tracking=true,kerning=true,spacing=true,factor=1100,stretch=10,shrink=10]{microtype}",
                "- Or switch to standard fonts without expansion features"
            ])
        
        if "Undefined control sequence" in error_msg or (compilation_log and "Undefined control sequence" in compilation_log):
            fix_context.extend([
                "- UNDEFINED COMMAND ERROR: Remove undefined commands or include the required packages",
                "- Check that all \\usepackage{} declarations are correct and packages exist",
                "- Avoid custom commands that are not defined"
            ])
        
        if "moderncv" in error_msg or (compilation_log and "moderncv" in compilation_log):
            fix_context.extend([
                "- MODERNCV ISSUES: Consider using standard article class instead for better compatibility",
                "- If using moderncv, avoid custom spacing commands like \\makecvfootertopskip",
                "- Use only standard moderncv commands and styles"
            ])
        
        if "Emergency stop" in error_msg or (compilation_log and "Emergency stop" in compilation_log):
            fix_context.extend([
                "- CRITICAL ERROR: Check for missing \\begin{document}, unmatched braces, or syntax errors",
                "- Ensure document structure is complete and valid"
            ])
        
        # Add general recovery suggestions
        fix_context.extend([
            "\nGeneral fixes:",
            "- Use standard document classes (article, report, book) for maximum compatibility",
            "- Include proper encoding: \\usepackage[T1]{fontenc} and \\usepackage[utf8]{inputenc}",
            "- Use widely supported packages: geometry, xcolor, hyperref, enumitem",
            "- Avoid specialized packages that might not be available",
            "- Generate clean, simple LaTeX code that works across different engines"
        ])
        
        return "\n".join(fix_context)
    
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
