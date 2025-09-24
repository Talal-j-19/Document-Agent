"""
Gemini API client for generating LaTeX code.
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class GeminiClient:
    """Client for interacting with Google's Gemini AI to generate LaTeX code."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Google AI API key. If not provided, will look for GEMINI_API_KEY env var.
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided either as parameter or environment variable")
        
        genai.configure(api_key=self.api_key)

        # Choose model name: prefer env var GEMINI_MODEL, default to a current stable model
        model_name = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize model '{model_name}': {e}")
        
        # Configure request timeout (seconds), default 120; override with GEMINI_REQUEST_TIMEOUT
        try:
            self.request_timeout = int(os.getenv("GEMINI_REQUEST_TIMEOUT", "120"))
        except ValueError:
            self.request_timeout = 120
    
    def generate_latex(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate LaTeX code based on the given prompt.
        
        Args:
            prompt: The description of what LaTeX document to generate
            context: Additional context or requirements for the LaTeX generation
            
        Returns:
            Generated LaTeX code as a string
        """
        system_prompt = """
You are an expert LaTeX document generator. Generate clean, well-structured LaTeX code based on the user's requirements.

Rules:
1. Always include proper document class and necessary packages
2. Use appropriate LaTeX commands and environments
3. Ensure the code is compilable with pdflatex, xelatex, or lualatex
4. Include proper formatting and structure
5. Only return the LaTeX code, no explanations or markdown formatting
6. Start with \\documentclass and end with \\end{document}

Compatibility Guidelines:
- For CV/Resume documents: Use standard document classes (article, report) instead of moderncv if there might be compatibility issues
- Avoid undefined control sequences - only use commands from included packages
- For font issues: Include appropriate font packages and avoid microtype with problematic fonts
- Use standard packages: geometry, hyperref, xcolor, enumitem, graphicx
- When using moderncv: Avoid custom commands like \\makecvfootertopskip, use standard spacing commands
- For modern styling: Use xcolor for colors, geometry for margins, custom commands for formatting
- Test compatibility: Prefer widely supported packages over specialized ones

For CV documents specifically:
- If using moderncv, use only well-established commands
- Alternative: Use article class with custom formatting for better compatibility
- Include proper font encoding: \\usepackage[T1]{fontenc} and \\usepackage[utf8]{inputenc}
- Avoid problematic font expansion by using standard fonts
"""
        
        full_prompt = system_prompt
        if context:
            full_prompt += f"\n\nAdditional context: {context}"
        full_prompt += f"\n\nUser request: {prompt}"
        
        try:
            response = self.model.generate_content(
                full_prompt,
                request_options={"timeout": self.request_timeout}
            )
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate LaTeX code: {str(e)}")
    
    def generate_latex_with_options(
        self, 
        prompt: str, 
        document_class: str = "article",
        packages: Optional[list] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate LaTeX code with specific options and customizations.
        
        Args:
            prompt: The description of what LaTeX document to generate
            document_class: LaTeX document class (article, report, book, etc.)
            packages: List of LaTeX packages to include
            custom_settings: Dictionary of custom LaTeX settings
            
        Returns:
            Generated LaTeX code as a string
        """
        context_parts = []
        context_parts.append(f"Use document class: {document_class}")
        
        if packages:
            context_parts.append(f"Include these packages: {', '.join(packages)}")
        
        if custom_settings:
            settings_str = ", ".join([f"{k}: {v}" for k, v in custom_settings.items()])
            context_parts.append(f"Apply these settings: {settings_str}")
        
        context = "\n".join(context_parts) if context_parts else None
        
        return self.generate_latex(prompt, context)
