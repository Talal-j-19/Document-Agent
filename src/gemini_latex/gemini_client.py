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

    # Modern, professional LaTeX CV system prompt
    system_prompt = (
        """
You are an expert LaTeX document generator. Generate clean, professional, and modern LaTeX code based on the user's requirements.

Rules:
1. Always include the appropriate document class and all necessary packages for the requested style (including moderncv, altacv, or other modern CV templates if specified or implied).
2. Use correct LaTeX commands and environments for the chosen template.
3. Ensure the code is compilable with pdflatex, xelatex, or lualatex, and includes all required packages and class files.
4. Include proper formatting, structure, and styling as expected for a professional, modern CV.
5. Only return the LaTeX code, no explanations or markdown formatting.
6. Start with \\documentclass and end with \\end{document}.

Guidelines for Modern CVs:
- If the user requests a modern or professional CV, use a modern LaTeX class such as moderncv or altacv, and select a suitable style (e.g., 'banking', 'classic', 'casual', etc. for moderncv).
- Always include all required \\usepackage and \\moderncvstyle or \\moderncvcolor commands, and ensure the document compiles without missing dependencies.
- For altacv, include the altacv class and all required packages, and use the sidebar and color features as appropriate.
- Add sections for profile, skills, experience, education, projects, and contact info, using icons and color if supported by the template.
- If a profile photo or other external object is requested, DO NOT include an explicit LaTeX command (such as \\photo or \\includegraphics) in the code by default. Instead, add a clear placeholder comment in the code (e.g., '% Photo placeholder: add \\photo[80pt]{photo.jpg} here if available'). This prevents compilation errors if the file is missing. The actual reference can be added later in editing mode when the user provides the file.
- Use color, icons, and modern layout features as supported by the chosen template.
- If the user does not specify a template, prefer moderncv for CVs, but fall back to article with custom formatting if moderncv is not available.
- Always use standard, well-documented commands for the chosen template, and avoid custom commands that may not be defined.
- Include proper font encoding: \\usepackage[T1]{fontenc} and \\usepackage[utf8]{inputenc} if not already included by the template.
- For best compatibility, avoid microtype unless required, and use standard fonts.
"""
    )
    
    def generate_latex(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate LaTeX code based on the given prompt.
        
        Args:
            prompt: The description of what LaTeX document to generate
            context: Additional context or requirements for the LaTeX generation
        Returns:
            Generated LaTeX code as a string
        """
        full_prompt = self.system_prompt
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
