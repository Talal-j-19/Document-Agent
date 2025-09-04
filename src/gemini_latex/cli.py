"""
Command-line interface for the Gemini LaTeX Compiler.
"""

import click
import os
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from typing import Optional

from .main import GeminiLaTeXProcessor


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Gemini LaTeX Compiler - Generate LaTeX documents using AI and compile them to PDF."""
    pass


@cli.command()
@click.argument('prompt', type=str)
@click.option('--output', '-o', type=str, help='Output filename (without extension)')
@click.option('--context', '-c', type=str, help='Additional context for generation')
@click.option('--no-tex', is_flag=True, help='Don\'t save the .tex file')
@click.option('--engine', '-e', default='pdflatex', help='LaTeX engine to use')
@click.option('--output-dir', type=str, help='Output directory')
@click.option('--api-key', type=str, help='Gemini API key (overrides environment variable)')
def generate(prompt: str, output: Optional[str], context: Optional[str], 
             no_tex: bool, engine: str, output_dir: Optional[str], api_key: Optional[str]):
    """Generate LaTeX from prompt and compile to PDF."""
    
    try:
        processor = GeminiLaTeXProcessor(
            api_key=api_key,
            latex_engine=engine,
            default_output_dir=output_dir or "output"
        )
        
        with console.status("[bold blue]Generating LaTeX code..."):
            result = processor.generate_and_compile(
                prompt=prompt,
                output_filename=output,
                context=context,
                save_tex=not no_tex
            )
        
        if result["success"]:
            console.print(Panel.fit("✅ Generation and compilation successful!", style="bold green"))
            
            if result["tex_file"]:
                console.print(f"📄 LaTeX file: {result['tex_file']}")
            console.print(f"📋 PDF file: {result['pdf_file']}")
            
            # Show LaTeX code preview
            if result["latex_code"]:
                console.print("\n[bold]Generated LaTeX code:[/bold]")
                syntax = Syntax(result["latex_code"][:500] + "...", "latex", theme="monokai")
                console.print(syntax)
        else:
            console.print(Panel.fit(f"❌ Error: {result['error']}", style="bold red"))
            if result["latex_code"]:
                console.print("\n[bold]Generated LaTeX code (for debugging):[/bold]")
                syntax = Syntax(result["latex_code"], "latex", theme="monokai")
                console.print(syntax)
            
    except Exception as e:
        console.print(Panel.fit(f"❌ Unexpected error: {str(e)}", style="bold red"))


@cli.command()
@click.argument('prompt', type=str)
@click.option('--context', '-c', type=str, help='Additional context for generation')
@click.option('--output', '-o', type=str, help='Output file for LaTeX code')
@click.option('--api-key', type=str, help='Gemini API key (overrides environment variable)')
def latex_only(prompt: str, context: Optional[str], output: Optional[str], api_key: Optional[str]):
    """Generate only LaTeX code without compilation."""
    
    try:
        processor = GeminiLaTeXProcessor(api_key=api_key)
        
        with console.status("[bold blue]Generating LaTeX code..."):
            latex_code = processor.generate_latex_only(prompt, context)
        
        console.print(Panel.fit("✅ LaTeX generation successful!", style="bold green"))
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(latex_code)
            console.print(f"📄 LaTeX code saved to: {output}")
        
        console.print("\n[bold]Generated LaTeX code:[/bold]")
        syntax = Syntax(latex_code, "latex", theme="monokai")
        console.print(syntax)
        
    except Exception as e:
        console.print(Panel.fit(f"❌ Error: {str(e)}", style="bold red"))


@cli.command()
@click.argument('tex_file', type=click.Path(exists=True))
@click.option('--engine', '-e', default='pdflatex', help='LaTeX engine to use')
def compile(tex_file: str, engine: str):
    """Compile an existing LaTeX file to PDF."""
    
    try:
        processor = GeminiLaTeXProcessor(latex_engine=engine)
        
        with console.status("[bold blue]Compiling LaTeX file..."):
            result = processor.compile_existing_latex(tex_file)
        
        if result["success"]:
            console.print(Panel.fit("✅ Compilation successful!", style="bold green"))
            console.print(f"📋 PDF file: {result['pdf_file']}")
        else:
            console.print(Panel.fit(f"❌ Compilation failed: {result['error']}", style="bold red"))
            if result["compilation_log"]:
                console.print("\n[bold]Compilation log:[/bold]")
                console.print(result["compilation_log"])
                
    except Exception as e:
        console.print(Panel.fit(f"❌ Error: {str(e)}", style="bold red"))


@cli.command()
@click.argument('prompt', type=str)
@click.option('--doc-class', default='article', help='Document class (article, report, book, etc.)')
@click.option('--packages', help='Comma-separated list of LaTeX packages')
@click.option('--output', '-o', type=str, help='Output filename (without extension)')
@click.option('--engine', '-e', default='pdflatex', help='LaTeX engine to use')
@click.option('--output-dir', type=str, help='Output directory')
@click.option('--api-key', type=str, help='Gemini API key (overrides environment variable)')
def custom(prompt: str, doc_class: str, packages: Optional[str], output: Optional[str],
           engine: str, output_dir: Optional[str], api_key: Optional[str]):
    """Generate LaTeX with custom document class and packages."""
    
    try:
        package_list = packages.split(',') if packages else None
        if package_list:
            package_list = [pkg.strip() for pkg in package_list]
        
        processor = GeminiLaTeXProcessor(
            api_key=api_key,
            latex_engine=engine,
            default_output_dir=output_dir or "output"
        )
        
        with console.status("[bold blue]Generating custom LaTeX document..."):
            result = processor.generate_with_custom_options(
                prompt=prompt,
                document_class=doc_class,
                packages=package_list,
                output_filename=output
            )
        
        if result["success"]:
            console.print(Panel.fit("✅ Custom document generation successful!", style="bold green"))
            console.print(f"📄 LaTeX file: {result['tex_file']}")
            console.print(f"📋 PDF file: {result['pdf_file']}")
        else:
            console.print(Panel.fit(f"❌ Error: {result['error']}", style="bold red"))
            
    except Exception as e:
        console.print(Panel.fit(f"❌ Error: {str(e)}", style="bold red"))


@cli.command()
def check():
    """Check system requirements and LaTeX installation."""
    
    console.print("[bold]Checking system requirements...[/bold]\n")
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        console.print("✅ GEMINI_API_KEY environment variable is set")
    else:
        console.print("❌ GEMINI_API_KEY environment variable is not set")
    
    # Check LaTeX installation
    try:
        from .latex_compiler import LaTeXCompiler
        compiler = LaTeXCompiler()
        available_engines = compiler.get_available_engines()
        
        if available_engines:
            console.print("✅ LaTeX installation found")
            console.print(f"   Available engines: {', '.join(available_engines)}")
        else:
            console.print("❌ No LaTeX engines found")
    except Exception as e:
        console.print(f"❌ LaTeX check failed: {str(e)}")


def main():
    """Entry point for the CLI."""
    cli()
