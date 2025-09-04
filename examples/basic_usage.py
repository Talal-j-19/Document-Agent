"""
Basic usage example for the Gemini LaTeX Compiler.

This script demonstrates simple document generation from natural language prompts.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gemini_latex import GeminiLaTeXProcessor


def main():
    """Run basic usage examples."""
    print("Gemini LaTeX Compiler - Basic Usage Examples")
    print("=" * 50)
    
    # Initialize the processor
    try:
        processor = GeminiLaTeXProcessor(default_output_dir="examples/output")
        print("✅ Processor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize processor: {e}")
        print("Make sure you have set your GEMINI_API_KEY in the .env file")
        return
    
    # Example 1: Simple document generation
    print("\n1. Generating a simple document...")
    result = processor.generate_and_compile(
        prompt="Create a simple letter thanking someone for their help",
        output_filename="thank_you_letter"
    )
    
    if result["success"]:
        print(f"   ✅ Document generated: {result['pdf_file']}")
    else:
        print(f"   ❌ Failed: {result['error']}")
    
    # Example 2: Technical document
    print("\n2. Generating a technical document...")
    result = processor.generate_and_compile(
        prompt="Create a brief technical report about the benefits of renewable energy",
        output_filename="renewable_energy_report",
        context="Include sections for introduction, benefits, and conclusion. Use professional formatting."
    )
    
    if result["success"]:
        print(f"   ✅ Document generated: {result['pdf_file']}")
    else:
        print(f"   ❌ Failed: {result['error']}")
    
    # Example 3: Only generate LaTeX (no compilation)
    print("\n3. Generating LaTeX code only...")
    try:
        latex_code = processor.generate_latex_only(
            prompt="Create a mathematical formula sheet for calculus",
            context="Include derivative and integral formulas with examples"
        )
        print(f"   ✅ LaTeX code generated ({len(latex_code)} characters)")
        print("   Preview:")
        print("   " + latex_code[:200] + "...")
        
        # Save the LaTeX code
        latex_file = "examples/output/calculus_formulas.tex"
        os.makedirs(os.path.dirname(latex_file), exist_ok=True)
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(latex_code)
        print(f"   📄 LaTeX saved to: {latex_file}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print("Basic usage examples completed!")
    print("Check the 'examples/output' directory for generated files.")


if __name__ == "__main__":
    main()
