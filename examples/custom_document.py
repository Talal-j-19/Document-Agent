"""
Custom document example for the Gemini LaTeX Compiler.

This script demonstrates advanced customization options including
custom document classes, packages, and settings.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gemini_latex import GeminiLaTeXProcessor


def main():
    """Run custom document examples."""
    print("Gemini LaTeX Compiler - Custom Document Examples")
    print("=" * 55)
    
    # Initialize the processor
    try:
        processor = GeminiLaTeXProcessor(default_output_dir="examples/output")
        print("✅ Processor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize processor: {e}")
        return
    
    # Example 1: Academic paper with custom packages
    print("\n1. Generating academic paper with math packages...")
    result = processor.generate_with_custom_options(
        prompt="Create an academic paper about machine learning algorithms",
        document_class="article",
        packages=["amsmath", "amssymb", "amsthm", "graphicx", "hyperref"],
        custom_settings={
            "font_size": "12pt",
            "paper": "a4paper",
            "margin": "1in"
        },
        output_filename="ml_academic_paper"
    )
    
    if result["success"]:
        print(f"   ✅ Academic paper generated: {result['pdf_file']}")
    else:
        print(f"   ❌ Failed: {result['error']}")
    
    # Example 2: Presentation slides
    print("\n2. Generating presentation slides...")
    result = processor.generate_with_custom_options(
        prompt="Create a presentation about climate change with multiple slides",
        document_class="beamer",
        packages=["graphicx", "tikz", "hyperref"],
        output_filename="climate_presentation"
    )
    
    if result["success"]:
        print(f"   ✅ Presentation generated: {result['pdf_file']}")
    else:
        print(f"   ❌ Failed: {result['error']}")
    
    # Example 3: Book chapter
    print("\n3. Generating book chapter...")
    result = processor.generate_with_custom_options(
        prompt="Create a chapter about data structures for a computer science textbook",
        document_class="book",
        packages=["listings", "xcolor", "graphicx", "hyperref"],
        custom_settings={
            "chapter_title": "Data Structures and Algorithms"
        },
        output_filename="data_structures_chapter"
    )
    
    if result["success"]:
        print(f"   ✅ Book chapter generated: {result['pdf_file']}")
    else:
        print(f"   ❌ Failed: {result['error']}")
    
    # Example 4: Resume/CV
    print("\n4. Generating professional resume...")
    result = processor.generate_with_custom_options(
        prompt="Create a professional resume for a software engineer with 5 years experience",
        document_class="article",
        packages=["geometry", "enumitem", "hyperref", "xcolor"],
        custom_settings={
            "margins": "0.75in",
            "font": "sans-serif"
        },
        output_filename="software_engineer_resume"
    )
    
    if result["success"]:
        print(f"   ✅ Resume generated: {result['pdf_file']}")
    else:
        print(f"   ❌ Failed: {result['error']}")
    
    # Example 5: Mathematical document
    print("\n5. Generating mathematical document...")
    result = processor.generate_with_custom_options(
        prompt="Create a mathematical proof document with theorems and lemmas",
        document_class="amsart",
        packages=["amsmath", "amssymb", "amsthm", "mathtools", "tikz"],
        output_filename="mathematical_proofs"
    )
    
    if result["success"]:
        print(f"   ✅ Mathematical document generated: {result['pdf_file']}")
    else:
        print(f"   ❌ Failed: {result['error']}")
    
    print("\n" + "=" * 55)
    print("Custom document examples completed!")
    print("Check the 'examples/output' directory for generated files.")
    print("\\nTip: Try experimenting with different document classes:")
    print("- article: General documents, papers")
    print("- report: Longer documents with chapters")
    print("- book: Books with parts, chapters, sections")
    print("- beamer: Presentation slides")
    print("- letter: Formal letters")


if __name__ == "__main__":
    main()
