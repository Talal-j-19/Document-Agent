# Gemini LaTeX Compiler

A Python project that uses Google's Gemini AI to generate LaTeX code and automatically compile it to PDF documents.

## Features

- 🤖 **AI-Powered LaTeX Generation**: Use Google's Gemini AI to create LaTeX documents from natural language prompts
- 📄 **Automatic PDF Compilation**: Compile generated LaTeX code to PDF using various LaTeX engines
- 🛠️ **Flexible Configuration**: Support for custom document classes, packages, and settings
- 💻 **Command-Line Interface**: Easy-to-use CLI for quick document generation
- 🐍 **Python API**: Programmatic access for integration into other applications

## Prerequisites

1. **Python 3.8+**
2. **LaTeX Distribution**: Install one of the following:
   - Windows: [MiKTeX](https://miktex.org/)
   - macOS: [MacTeX](https://tug.org/mactex/)
   - Linux: TeX Live (`sudo apt-get install texlive-full`)
3. **Gemini API Key**: Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/gemini-latex-compiler.git
cd gemini-latex-compiler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. Install the package:
```bash
pip install -e .
```

## Quick Start

### Command Line Usage

1. **Check your setup**:
```bash
gemini-latex check
```

2. **Generate a simple document**:
```bash
gemini-latex generate "Create a research paper about machine learning"
```

3. **Generate with custom options**:
```bash
gemini-latex custom "Create a mathematical proof" --doc-class article --packages "amsmath,amssymb,theorem"
```

4. **Generate only LaTeX code** (no compilation):
```bash
gemini-latex latex-only "Create a resume template"
```

5. **Compile an existing LaTeX file**:
```bash
gemini-latex compile document.tex
```

### Python API Usage

```python
from gemini_latex import GeminiLaTeXProcessor

# Initialize the processor
processor = GeminiLaTeXProcessor()

# Generate and compile a document
result = processor.generate_and_compile(
    prompt="Create a technical report about renewable energy",
    output_filename="energy_report"
)

if result["success"]:
    print(f"PDF generated: {result['pdf_file']}")
    print(f"LaTeX source: {result['tex_file']}")
else:
    print(f"Error: {result['error']}")
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Required: Your Gemini API key
GEMINI_API_KEY=your_api_key_here

# Optional: Default LaTeX engine
LATEX_ENGINE=pdflatex

# Optional: Default output directory
DEFAULT_OUTPUT_DIR=output
```

### LaTeX Engines

The project supports multiple LaTeX engines:
- `pdflatex` (default) - Good for most documents
- `xelatex` - Better Unicode and font support
- `lualatex` - Modern LaTeX engine with Lua scripting

## Examples

Check the `examples/` directory for sample scripts:

- `basic_usage.py` - Simple document generation
- `custom_document.py` - Advanced customization
- `batch_processing.py` - Processing multiple documents

## API Reference

### GeminiLaTeXProcessor

The main class for document generation and compilation.

#### Methods

- `generate_and_compile(prompt, output_filename=None, context=None, save_tex=True)`
- `generate_latex_only(prompt, context=None)`
- `compile_existing_latex(tex_file_path)`
- `generate_with_custom_options(prompt, document_class="article", packages=None, ...)`

### GeminiClient

Handles interaction with the Gemini API.

#### Methods

- `generate_latex(prompt, context=None)`
- `generate_latex_with_options(prompt, document_class="article", packages=None, ...)`

### LaTeXCompiler

Manages LaTeX compilation to PDF.

#### Methods

- `compile_latex_to_pdf(latex_code, output_path=None, working_dir=None)`
- `compile_from_file(tex_file_path, output_dir=None)`
- `get_available_engines()`

## Error Handling

The library provides detailed error information:

```python
result = processor.generate_and_compile("Create a document")

if not result["success"]:
    print(f"Error: {result['error']}")
    if result["compilation_log"]:
        print("Compilation log:", result["compilation_log"])
```

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY must be provided"**
   - Make sure you've set up your `.env` file with a valid API key

2. **"LaTeX engine 'pdflatex' not found"**
   - Install a LaTeX distribution (MiKTeX, TeX Live, etc.)
   - Ensure the LaTeX binaries are in your system PATH

3. **"LaTeX compilation failed"**
   - Check the compilation log in the result for specific LaTeX errors
   - Ensure required LaTeX packages are installed

### Getting Help

- Check the compilation log for LaTeX-specific errors
- Use the `check` command to verify your setup
- Review the examples for proper usage patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google's Gemini AI for document generation
- The LaTeX community for the typesetting system
- Python packaging community for the tools and libraries
