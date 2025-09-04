"""
LaTeX compiler for converting LaTeX code to PDF.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, List


class LaTeXCompiler:
    """Handles compilation of LaTeX code to PDF."""
    
    def __init__(self, latex_engine: str = "pdflatex"):
        """
        Initialize the LaTeX compiler.
        
        Args:
            latex_engine: LaTeX engine to use (pdflatex, xelatex, lualatex)
        """
        self.latex_engine = latex_engine
        self.validate_latex_installation()
    
    def validate_latex_installation(self) -> bool:
        """
        Check if LaTeX is installed and accessible.
        
        Returns:
            True if LaTeX is available, raises RuntimeError otherwise
        """
        try:
            result = subprocess.run(
                [self.latex_engine, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True
            else:
                raise RuntimeError(f"LaTeX engine '{self.latex_engine}' is not working properly")
        except FileNotFoundError:
            raise RuntimeError(
                f"LaTeX engine '{self.latex_engine}' not found. "
                "Please install a LaTeX distribution like MiKTeX or TeX Live."
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("LaTeX installation check timed out")
    
    def compile_latex_to_pdf(
        self, 
        latex_code: str, 
        output_path: Optional[str] = None,
        working_dir: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Compile LaTeX code to PDF.
        
        Args:
            latex_code: The LaTeX code to compile
            output_path: Path where to save the PDF (optional)
            working_dir: Working directory for compilation (optional)
            
        Returns:
            Tuple of (pdf_path, compilation_log)
        """
        if working_dir is None:
            working_dir = tempfile.mkdtemp()
            cleanup_temp = True
        else:
            cleanup_temp = False
        
        try:
            # Create temporary LaTeX file
            tex_file = os.path.join(working_dir, "document.tex")
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_code)
            
            # Compile LaTeX
            pdf_path, log = self._run_latex_compilation(tex_file, working_dir)
            
            # Move PDF to desired location if specified
            if output_path:
                final_pdf_path = Path(output_path)
                final_pdf_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(pdf_path, final_pdf_path)
                pdf_path = str(final_pdf_path)
            
            return pdf_path, log
            
        finally:
            if cleanup_temp and os.path.exists(working_dir):
                shutil.rmtree(working_dir, ignore_errors=True)
    
    def _run_latex_compilation(self, tex_file: str, working_dir: str) -> Tuple[str, str]:
        """
        Run the actual LaTeX compilation process.
        
        Args:
            tex_file: Path to the .tex file
            working_dir: Working directory for compilation
            
        Returns:
            Tuple of (pdf_path, compilation_log)
        """
        compilation_log = []
        pdf_path = tex_file.replace('.tex', '.pdf')
        
        # Run compilation (usually twice for proper references)
        for run_number in range(2):
            try:
                result = subprocess.run([
                    self.latex_engine,
                    "-interaction=nonstopmode",
                    "-output-directory", working_dir,
                    tex_file
                ], capture_output=True, text=True, cwd=working_dir, timeout=60)
                
                compilation_log.append(f"Run {run_number + 1}:")
                compilation_log.append(result.stdout)
                if result.stderr:
                    compilation_log.append("STDERR:")
                    compilation_log.append(result.stderr)
                
                if result.returncode != 0:
                    error_msg = f"LaTeX compilation failed on run {run_number + 1}"
                    compilation_log.append(f"ERROR: {error_msg}")
                    if not os.path.exists(pdf_path):
                        raise RuntimeError(f"{error_msg}. See compilation log for details.")
                
            except subprocess.TimeoutExpired:
                raise RuntimeError("LaTeX compilation timed out after 60 seconds")
        
        if not os.path.exists(pdf_path):
            raise RuntimeError("PDF was not generated despite successful compilation")
        
        return pdf_path, "\n".join(compilation_log)
    
    def compile_from_file(self, tex_file_path: str, output_dir: Optional[str] = None) -> Tuple[str, str]:
        """
        Compile a LaTeX file to PDF.
        
        Args:
            tex_file_path: Path to the .tex file
            output_dir: Directory where to save the PDF
            
        Returns:
            Tuple of (pdf_path, compilation_log)
        """
        with open(tex_file_path, 'r', encoding='utf-8') as f:
            latex_code = f.read()
        
        if output_dir is None:
            output_dir = os.path.dirname(tex_file_path)
        
        base_name = os.path.splitext(os.path.basename(tex_file_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.pdf")
        
        return self.compile_latex_to_pdf(latex_code, output_path, os.path.dirname(tex_file_path))
    
    def get_available_engines(self) -> List[str]:
        """
        Get list of available LaTeX engines on the system.
        
        Returns:
            List of available LaTeX engine names
        """
        engines = ["pdflatex", "xelatex", "lualatex"]
        available = []
        
        for engine in engines:
            try:
                subprocess.run([engine, "--version"], 
                             capture_output=True, timeout=5)
                available.append(engine)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        return available
