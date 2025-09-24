"""
Interactive session manager that orchestrates the complete editing workflow.
"""

import os
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .main import GeminiLaTeXProcessor
from .document_editor import DocumentEditor
from .pdf_viewer import PDFViewer


class InteractiveSession:
    """Manages interactive document editing sessions."""
    
    def __init__(
        self,
        processor: GeminiLaTeXProcessor,
        session_dir: str = "sessions"
    ):
        """
        Initialize the interactive session manager.
        
        Args:
            processor: GeminiLaTeXProcessor instance
            session_dir: Directory to store editing sessions
        """
        self.processor = processor
        self.editor = DocumentEditor(
            processor.gemini_client,
            processor.latex_compiler,
            session_dir
        )
        self.viewer = PDFViewer()
        self.console = Console()
        
    def start_interactive_editing(
        self,
        prompt: str,
        document_name: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start an interactive editing session.
        
        Args:
            prompt: Initial prompt for document generation
            document_name: Name for the document (optional)
            context: Additional context for generation (optional)
            
        Returns:
            Dictionary containing session results
        """
        if not document_name:
            document_name = "document"
        
        self.console.print(Panel.fit("🚀 Starting Interactive Document Editing", style="bold blue"))
        self.console.print(f"Document: {document_name}")
        self.console.print(f"Prompt: {prompt}")
        if context:
            self.console.print(f"Context: {context}")
        
        # Step 1: Generate initial document
        self.console.print("\n🔄 Generating initial document...")
        
        initial_result = self.processor.generate_and_compile(
            prompt=prompt,
            output_filename=document_name,
            context=context,
            save_tex=True
        )
        
        if not initial_result["success"]:
            return {
                "success": False,
                "error": f"Failed to generate initial document: {initial_result['error']}",
                "session_id": None
            }
        
        # Step 2: Create editing session
        session_id = self.editor.create_editing_session(
            initial_latex_code=initial_result["latex_code"],
            document_name=document_name,
            original_prompt=prompt
        )
        
        self.console.print(f"✅ Session created: {session_id}")
        
        # Step 3: Compile and display initial version
        compile_result = self.editor.compile_current_version(session_id)
        if not compile_result["success"]:
            return {
                "success": False,
                "error": f"Failed to compile initial version: {compile_result['error']}",
                "session_id": session_id
            }
        
        # Step 4: Start interactive editing loop
        return self._run_editing_loop(session_id, compile_result["pdf_file"])
    
    def resume_session(self, session_id: str) -> Dict[str, Any]:
        """
        Resume an existing editing session.
        
        Args:
            session_id: The session ID to resume
            
        Returns:
            Dictionary containing session results
        """
        try:
            session_data = self.editor.load_session(session_id)
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Session {session_id} not found",
                "session_id": session_id
            }
        
        self.console.print(Panel.fit("🔄 Resuming Interactive Editing Session", style="bold green"))
        self.console.print(f"Session ID: {session_id}")
        self.console.print(f"Document: {session_data['document_name']}")
        self.console.print(f"Current Version: {session_data['current_version']}")
        
        # Compile current version
        compile_result = self.editor.compile_current_version(session_id)
        if not compile_result["success"]:
            return {
                "success": False,
                "error": f"Failed to compile current version: {compile_result['error']}",
                "session_id": session_id
            }
        
        # Start interactive editing loop
        return self._run_editing_loop(session_id, compile_result["pdf_file"])
    
    def _run_editing_loop(self, session_id: str, initial_pdf_path: str) -> Dict[str, Any]:
        """
        Run the main interactive editing loop.
        
        Args:
            session_id: The session ID
            initial_pdf_path: Path to the initial PDF
            
        Returns:
            Dictionary containing session results
        """
        current_pdf_path = initial_pdf_path
        session_data = self.editor.load_session(session_id)
        current_version = session_data["current_version"]
        
        while True:
            # Display current PDF info and open it
            self.viewer.display_pdf_info(current_pdf_path, current_version)
            
            # Open PDF
            if not self.viewer.open_pdf(current_pdf_path):
                self.viewer.show_error_message("Failed to open PDF. Please check the file manually.")
            
            # Get user feedback
            feedback = self.viewer.prompt_for_feedback()
            
            if feedback["action"] == "cancel":
                self.console.print("❌ Session cancelled by user.")
                return {
                    "success": False,
                    "error": "Session cancelled by user",
                    "session_id": session_id
                }
            
            elif feedback["action"] == "satisfied":
                if self.viewer.confirm_satisfaction():
                    # User is satisfied, end session
                    final_result = self._finalize_session(session_id, current_pdf_path, current_version)
                    return final_result
                else:
                    # User changed mind, continue editing
                    continue
            
            elif feedback["action"] == "save_exit":
                # Save and exit without confirmation
                final_result = self._finalize_session(session_id, current_pdf_path, current_version)
                return final_result
            
            elif feedback["action"] == "modify":
                # Apply modifications
                modify_result = self._handle_modification(session_id, feedback["data"])
                if modify_result["success"]:
                    current_pdf_path = modify_result["pdf_file"]
                    current_version = modify_result["version"]
                    self.viewer.show_success_message(f"Document updated to version {current_version}!")
                else:
                    self.viewer.show_error_message(f"Failed to apply modifications: {modify_result['error']}")
                    # Continue with current version
            
            elif feedback["action"] == "view_history":
                # Show version history
                self._show_version_history(session_id)
                # Continue loop to show menu again
            
            elif feedback["action"] == "revert":
                # Handle version revert
                revert_result = self._handle_revert(session_id)
                if revert_result["success"]:
                    current_pdf_path = revert_result["pdf_file"]
                    current_version = revert_result["version"]
                    self.viewer.show_success_message(f"Reverted to version {current_version}!")
                else:
                    self.viewer.show_error_message(f"Failed to revert: {revert_result['error']}")
    
    def _handle_modification(self, session_id: str, modification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle document modification request.
        
        Args:
            session_id: The session ID
            modification_data: Modification request data
            
        Returns:
            Dictionary containing modification results
        """
        self.viewer.show_progress_message("Applying modifications...")
        
        # Apply modification
        modify_result = self.editor.apply_modification(
            session_id=session_id,
            modification_request=modification_data["modification_request"],
            context=modification_data.get("context")
        )
        
        if not modify_result["success"]:
            return {
                "success": False,
                "error": modify_result["error"]
            }
        
        # Compile new version
        self.viewer.show_progress_message("Compiling updated document...")
        compile_result = self.editor.compile_current_version(session_id)
        
        if not compile_result["success"]:
            return {
                "success": False,
                "error": f"Compilation failed: {compile_result['error']}"
            }
        
        return {
            "success": True,
            "pdf_file": compile_result["pdf_file"],
            "version": compile_result["version"]
        }
    
    def _handle_revert(self, session_id: str) -> Dict[str, Any]:
        """
        Handle version revert request.
        
        Args:
            session_id: The session ID
            
        Returns:
            Dictionary containing revert results
        """
        # Show version history
        versions = self.editor.get_version_history(session_id)
        self.viewer.display_version_history(versions)
        
        # Get user's version choice
        version_choice = self.viewer.get_version_choice(versions)
        
        if version_choice is None:
            # User cancelled
            return {
                "success": False,
                "error": "Revert cancelled by user"
            }
        
        self.viewer.show_progress_message(f"Reverting to version {version_choice}...")
        
        # Revert to chosen version
        revert_result = self.editor.revert_to_version(session_id, version_choice)
        
        if not revert_result["success"]:
            return {
                "success": False,
                "error": revert_result["error"]
            }
        
        # Compile reverted version
        self.viewer.show_progress_message("Compiling reverted document...")
        compile_result = self.editor.compile_current_version(session_id)
        
        if not compile_result["success"]:
            return {
                "success": False,
                "error": f"Compilation failed: {compile_result['error']}"
            }
        
        return {
            "success": True,
            "pdf_file": compile_result["pdf_file"],
            "version": compile_result["version"]
        }
    
    def _show_version_history(self, session_id: str) -> None:
        """
        Show version history for the session.
        
        Args:
            session_id: The session ID
        """
        versions = self.editor.get_version_history(session_id)
        self.viewer.display_version_history(versions)
        
        # Wait for user acknowledgment
        input("\\nPress Enter to continue...")
    
    def _finalize_session(self, session_id: str, final_pdf_path: str, final_version: int) -> Dict[str, Any]:
        """
        Finalize the editing session.
        
        Args:
            session_id: The session ID
            final_pdf_path: Path to the final PDF
            final_version: Final version number
            
        Returns:
            Dictionary containing finalization results
        """
        self.viewer.show_final_summary(session_id, final_version, final_pdf_path)
        
        return {
            "success": True,
            "session_id": session_id,
            "final_version": final_version,
            "final_pdf": final_pdf_path,
            "message": "Interactive editing session completed successfully"
        }
    
    def list_sessions(self) -> None:
        """List all available editing sessions."""
        sessions = self.editor.list_sessions()
        
        if not sessions:
            self.console.print("📝 No editing sessions found.")
            return
        
        self.console.print("\\n📝 Available Editing Sessions:")
        self.console.print("=" * 60)
        
        for session in sessions:
            # Format timestamp
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(session["created_at"].replace('Z', '+00:00'))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = session["created_at"]
            
            self.console.print(f"Session ID: {session['session_id']}")
            self.console.print(f"  Document: {session['document_name']}")
            self.console.print(f"  Created: {formatted_time}")
            self.console.print(f"  Versions: {session['total_versions']} (current: v{session['current_version']})")
            self.console.print()
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Dictionary containing session information
        """
        try:
            session_data = self.editor.load_session(session_id)
            versions = self.editor.get_version_history(session_id)
            
            return {
                "success": True,
                "session_data": session_data,
                "version_history": versions
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
