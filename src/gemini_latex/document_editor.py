"""
Document editor module for handling LaTeX document modifications and iterative editing.
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime

from .gemini_client import GeminiClient
from .latex_compiler import LaTeXCompiler


class DocumentEditor:
    """Handles document editing operations and version management."""
    
    def __init__(
        self,
        gemini_client: GeminiClient,
        latex_compiler: LaTeXCompiler,
        session_dir: str = "sessions"
    ):
        """
        Initialize the document editor.
        
        Args:
            gemini_client: Gemini AI client for generating modifications
            latex_compiler: LaTeX compiler for generating PDFs
            session_dir: Directory to store editing sessions
        """
        self.gemini_client = gemini_client
        self.latex_compiler = latex_compiler
        self.session_dir = session_dir
        
        # Ensure session directory exists
        Path(self.session_dir).mkdir(parents=True, exist_ok=True)
    
    def create_editing_session(
        self, 
        initial_latex_code: str,
        document_name: str,
        original_prompt: str
    ) -> str:
        """
        Create a new editing session.
        
        Args:
            initial_latex_code: The initial LaTeX code to edit
            document_name: Name of the document being edited
            original_prompt: The original prompt used to generate the document
            
        Returns:
            Session ID for the new editing session
        """
        session_id = f"{document_name}_{int(time.time())}"
        session_path = os.path.join(self.session_dir, session_id)
        os.makedirs(session_path, exist_ok=True)
        
        # Initialize session metadata
        session_data = {
            "session_id": session_id,
            "document_name": document_name,
            "original_prompt": original_prompt,
            "created_at": datetime.now().isoformat(),
            "versions": [
                {
                    "version": 1,
                    "latex_code": initial_latex_code,
                    "change_description": "Initial version",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "current_version": 1
        }
        
        # Save session metadata
        with open(os.path.join(session_path, "session.json"), 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        # Save initial LaTeX file
        with open(os.path.join(session_path, "v1.tex"), 'w', encoding='utf-8') as f:
            f.write(initial_latex_code)
        
        return session_id
    
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """
        Load an existing editing session.
        
        Args:
            session_id: The session ID to load
            
        Returns:
            Session data dictionary
        """
        session_path = os.path.join(self.session_dir, session_id)
        session_file = os.path.join(session_path, "session.json")
        
        if not os.path.exists(session_file):
            raise FileNotFoundError(f"Session {session_id} not found")
        
        with open(session_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def apply_modification(
        self,
        session_id: str,
        modification_request: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply a modification to the document.
        
        Args:
            session_id: The session ID
            modification_request: Description of the changes to make
            context: Additional context for the modification
            
        Returns:
            Dictionary containing the result of the modification
        """
        # Load current session
        session_data = self.load_session(session_id)
        current_version = session_data["current_version"]
        current_latex_code = session_data["versions"][-1]["latex_code"]
        
        # Create modification prompt
        modification_prompt = self._create_modification_prompt(
            current_latex_code,
            modification_request,
            session_data["original_prompt"],
            context
        )
        
        try:
            # Generate modified LaTeX code
            modified_latex_code = self.gemini_client.generate_latex(
                modification_prompt,
                context=f"This is a modification to an existing document. Original prompt: {session_data['original_prompt']}"
            )
            
            # Create new version
            new_version = current_version + 1
            new_version_data = {
                "version": new_version,
                "latex_code": modified_latex_code,
                "change_description": modification_request,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update session data
            session_data["versions"].append(new_version_data)
            session_data["current_version"] = new_version
            
            # Save updated session
            session_path = os.path.join(self.session_dir, session_id)
            with open(os.path.join(session_path, "session.json"), 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            # Save new LaTeX version
            with open(os.path.join(session_path, f"v{new_version}.tex"), 'w', encoding='utf-8') as f:
                f.write(modified_latex_code)
            
            return {
                "success": True,
                "new_version": new_version,
                "latex_code": modified_latex_code,
                "session_data": session_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to apply modification: {str(e)}",
                "latex_code": current_latex_code,
                "session_data": session_data
            }
    
    def compile_current_version(self, session_id: str) -> Dict[str, Any]:
        """
        Compile the current version of the document to PDF.
        
        Args:
            session_id: The session ID
            
        Returns:
            Dictionary containing compilation results
        """
        session_data = self.load_session(session_id)
        current_version = session_data["current_version"]
        current_latex_code = session_data["versions"][-1]["latex_code"]
        
        # Set up paths
        session_path = os.path.join(self.session_dir, session_id)
        pdf_file = os.path.join(session_path, f"v{current_version}.pdf")
        
        try:
            # Compile to PDF
            compiled_pdf_path, compilation_log = self.latex_compiler.compile_latex_to_pdf(
                current_latex_code, pdf_file
            )
            
            return {
                "success": True,
                "pdf_file": compiled_pdf_path,
                "latex_code": current_latex_code,
                "compilation_log": compilation_log,
                "version": current_version
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Compilation failed: {str(e)}",
                "latex_code": current_latex_code,
                "version": current_version
            }
    
    def get_version_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the version history for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            List of version information
        """
        session_data = self.load_session(session_id)
        return [
            {
                "version": v["version"],
                "change_description": v["change_description"],
                "timestamp": v["timestamp"]
            }
            for v in session_data["versions"]
        ]
    
    def revert_to_version(self, session_id: str, version_number: int) -> Dict[str, Any]:
        """
        Revert to a specific version.
        
        Args:
            session_id: The session ID
            version_number: The version number to revert to
            
        Returns:
            Dictionary containing revert results
        """
        session_data = self.load_session(session_id)
        
        # Find the target version
        target_version = None
        for version in session_data["versions"]:
            if version["version"] == version_number:
                target_version = version
                break
        
        if not target_version:
            return {
                "success": False,
                "error": f"Version {version_number} not found"
            }
        
        # Create a new version based on the target version
        new_version = session_data["current_version"] + 1
        new_version_data = {
            "version": new_version,
            "latex_code": target_version["latex_code"],
            "change_description": f"Reverted to version {version_number}",
            "timestamp": datetime.now().isoformat()
        }
        
        # Update session data
        session_data["versions"].append(new_version_data)
        session_data["current_version"] = new_version
        
        # Save updated session
        session_path = os.path.join(self.session_dir, session_id)
        with open(os.path.join(session_path, "session.json"), 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        # Save reverted LaTeX version
        with open(os.path.join(session_path, f"v{new_version}.tex"), 'w', encoding='utf-8') as f:
            f.write(target_version["latex_code"])
        
        return {
            "success": True,
            "new_version": new_version,
            "latex_code": target_version["latex_code"],
            "reverted_from": version_number
        }
    
    def _create_modification_prompt(
        self,
        current_latex_code: str,
        modification_request: str,
        original_prompt: str,
        context: Optional[str] = None
    ) -> str:
        """
        Create a prompt for modifying the LaTeX document.
        
        Args:
            current_latex_code: Current LaTeX code
            modification_request: Description of changes to make
            original_prompt: The original document generation prompt
            context: Additional context
            
        Returns:
            Formatted prompt for the AI
        """
        prompt = f"""
You are an expert LaTeX document editor. You need to modify an existing LaTeX document based on user requirements.

ORIGINAL DOCUMENT PURPOSE: {original_prompt}

CURRENT LATEX CODE:
{current_latex_code}

MODIFICATION REQUEST: {modification_request}

Instructions:
1. Carefully analyze the current LaTeX code and understand its structure
2. Apply ONLY the requested modifications while preserving the existing document structure and formatting
3. Maintain compatibility with pdflatex, xelatex, and lualatex engines
4. Ensure all packages and commands are properly defined
5. Return the complete modified LaTeX document
6. Do not add explanations - return only the LaTeX code
7. Start with \\documentclass and end with \\end{{document}}

IMPORTANT: Make minimal changes - only what is specifically requested. Preserve the existing style, structure, and content unless explicitly asked to change them.
"""
        
        if context:
            prompt += f"\n\nADDITIONAL CONTEXT: {context}"
        
        return prompt.strip()
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available editing sessions.
        
        Returns:
            List of session information
        """
        sessions = []
        
        if not os.path.exists(self.session_dir):
            return sessions
        
        for session_folder in os.listdir(self.session_dir):
            session_path = os.path.join(self.session_dir, session_folder)
            session_file = os.path.join(session_path, "session.json")
            
            if os.path.exists(session_file):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    sessions.append({
                        "session_id": session_data["session_id"],
                        "document_name": session_data["document_name"],
                        "created_at": session_data["created_at"],
                        "current_version": session_data["current_version"],
                        "total_versions": len(session_data["versions"])
                    })
                except Exception:
                    continue  # Skip corrupted session files
        
        return sessions
