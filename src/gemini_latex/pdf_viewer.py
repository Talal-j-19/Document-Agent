"""
PDF viewer interface for displaying PDFs to users and collecting feedback.
"""

import os
import sys
import subprocess
import platform
from typing import Optional, Dict, Any
from pathlib import Path

class PDFViewer:
    """Handles PDF display and user interaction."""
    
    def __init__(self):
        """Initialize the PDF viewer."""
        self.system = platform.system().lower()
    
    def open_pdf(self, pdf_path: str) -> bool:
        """
        Open a PDF file using the system's default PDF viewer.
        
        Args:
            pdf_path: Path to the PDF file to open
            
        Returns:
            True if PDF was opened successfully, False otherwise
        """
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return False
        
        try:
            if self.system == "windows":
                # Windows
                os.startfile(pdf_path)
            elif self.system == "darwin":
                # macOS
                subprocess.run(["open", pdf_path], check=True)
            else:
                # Linux and others
                subprocess.run(["xdg-open", pdf_path], check=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to open PDF: {str(e)}")
            return False
    
    def display_pdf_info(self, pdf_path: str, version: int = None) -> None:
        """
        Display information about the PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            version: Version number (optional)
        """
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return
        
        file_size = os.path.getsize(pdf_path) / 1024  # Size in KB
        
        print(f"📋 PDF Information:")
        print(f"   File: {os.path.basename(pdf_path)}")
        if version:
            print(f"   Version: {version}")
        print(f"   Size: {file_size:.1f} KB")
        print(f"   Location: {pdf_path}")
    
    def prompt_for_feedback(self) -> Dict[str, Any]:
        """
        Prompt the user for feedback on the current document.
        
        Returns:
            Dictionary containing user feedback and action
        """
        print("\n" + "="*60)
        print("📋 DOCUMENT REVIEW")
        print("="*60)
        print("Please review the PDF that just opened.")
        print()
        print("What would you like to do?")
        print("1. Make changes to the document")
        print("2. I'm satisfied with the current version")
        print("3. View version history")
        print("4. Revert to a previous version")
        print("5. Save and exit")
        print("6. Cancel without saving")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == "1":
                    return self._get_modification_request()
                elif choice == "2":
                    return {"action": "satisfied", "data": None}
                elif choice == "3":
                    return {"action": "view_history", "data": None}
                elif choice == "4":
                    return self._get_revert_request()
                elif choice == "5":
                    return {"action": "save_exit", "data": None}
                elif choice == "6":
                    return {"action": "cancel", "data": None}
                else:
                    print("❌ Invalid choice. Please enter a number between 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\n❌ Operation cancelled by user.")
                return {"action": "cancel", "data": None}
            except Exception as e:
                print(f"❌ Error getting input: {str(e)}")
                continue
    
    def _get_modification_request(self) -> Dict[str, Any]:
        """
        Get modification request from user.
        
        Returns:
            Dictionary containing modification request
        """
        print("\n📝 Describe the changes you want to make:")
        print("Be specific about what you want to add, remove, or modify.")
        print("Examples:")
        print("- 'Add a skills section with Python, Java, and SQL'")
        print("- 'Change the color scheme to blue and grey'")
        print("- 'Remove the summary section and make the contact info smaller'")
        print("- 'Add more work experience entries'")
        print()
        
        while True:
            try:
                modification = input("Your changes: ").strip()
                
                if not modification:
                    print("❌ Please describe the changes you want to make.")
                    continue
                
                # Ask for additional context
                print("\n💡 Any additional context or preferences? (optional)")
                context = input("Additional context: ").strip()
                context = context if context else None
                
                return {
                    "action": "modify",
                    "data": {
                        "modification_request": modification,
                        "context": context
                    }
                }
                
            except KeyboardInterrupt:
                print("\n\n❌ Operation cancelled by user.")
                return {"action": "cancel", "data": None}
            except Exception as e:
                print(f"❌ Error getting input: {str(e)}")
                continue
    
    def _get_revert_request(self) -> Dict[str, Any]:
        """
        Get version to revert to from user.
        
        Returns:
            Dictionary containing revert request
        """
        print("\n🔄 Revert to Previous Version")
        print("You'll see the version history, then choose which version to revert to.")
        
        return {"action": "revert", "data": None}
    
    def display_version_history(self, versions: list) -> None:
        """
        Display version history to the user.
        
        Args:
            versions: List of version information
        """
        print("\n📊 VERSION HISTORY")
        print("="*60)
        
        for version_info in versions:
            timestamp = version_info.get("timestamp", "Unknown")
            # Format timestamp for better readability
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = timestamp
            
            print(f"Version {version_info['version']}: {version_info['change_description']}")
            print(f"   Created: {formatted_time}")
            print()
    
    def get_version_choice(self, versions: list) -> Optional[int]:
        """
        Get user's choice of version to revert to.
        
        Args:
            versions: List of version information
            
        Returns:
            Version number to revert to, or None if cancelled
        """
        while True:
            try:
                print("Enter the version number to revert to (or 'cancel' to go back):")
                choice = input("Version number: ").strip().lower()
                
                if choice == "cancel":
                    return None
                
                version_num = int(choice)
                
                # Validate version exists
                valid_versions = [v["version"] for v in versions]
                if version_num not in valid_versions:
                    print(f"❌ Invalid version number. Available versions: {valid_versions}")
                    continue
                
                # Confirm the choice
                target_version = next(v for v in versions if v["version"] == version_num)
                print(f"\n⚠️  You're about to revert to Version {version_num}:")
                print(f"   Description: {target_version['change_description']}")
                
                confirm = input("Are you sure? (yes/no): ").strip().lower()
                if confirm in ['yes', 'y']:
                    return version_num
                elif confirm in ['no', 'n']:
                    continue
                else:
                    print("❌ Please enter 'yes' or 'no'.")
                    continue
                    
            except ValueError:
                print("❌ Please enter a valid version number.")
                continue
            except KeyboardInterrupt:
                print("\n\n❌ Operation cancelled by user.")
                return None
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
    
    def show_success_message(self, message: str) -> None:
        """
        Display a success message.
        
        Args:
            message: Success message to display
        """
        print(f"\n✅ {message}")
    
    def show_error_message(self, message: str) -> None:
        """
        Display an error message.
        
        Args:
            message: Error message to display
        """
        print(f"\n❌ {message}")
    
    def show_progress_message(self, message: str) -> None:
        """
        Display a progress message.
        
        Args:
            message: Progress message to display
        """
        print(f"\n🔄 {message}")
    
    def confirm_satisfaction(self) -> bool:
        """
        Confirm that the user is satisfied with the current document.
        
        Returns:
            True if user is satisfied, False otherwise
        """
        print("\n✅ Great! Are you completely satisfied with the current document?")
        
        while True:
            try:
                choice = input("Confirm (yes/no): ").strip().lower()
                
                if choice in ['yes', 'y']:
                    return True
                elif choice in ['no', 'n']:
                    return False
                else:
                    print("❌ Please enter 'yes' or 'no'.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n\n❌ Operation cancelled by user.")
                return False
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
    
    def show_final_summary(self, session_id: str, final_version: int, pdf_path: str) -> None:
        """
        Show final summary of the editing session.
        
        Args:
            session_id: The session ID
            final_version: Final version number
            pdf_path: Path to the final PDF
        """
        print("\n" + "="*60)
        print("🎉 EDITING SESSION COMPLETED")
        print("="*60)
        print(f"Session ID: {session_id}")
        print(f"Final Version: {final_version}")
        print(f"Final PDF: {pdf_path}")
        print("="*60)
        print("\n✅ Your document is ready!")
        
        # Offer to open the final PDF
        while True:
            try:
                choice = input("\nWould you like to open the final PDF? (yes/no): ").strip().lower()
                
                if choice in ['yes', 'y']:
                    self.open_pdf(pdf_path)
                    break
                elif choice in ['no', 'n']:
                    break
                else:
                    print("❌ Please enter 'yes' or 'no'.")
                    continue
                    
            except KeyboardInterrupt:
                break
            except Exception:
                break
