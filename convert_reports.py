#!/usr/bin/env python3
import os
import markdown
from weasyprint import HTML, CSS

def convert_md_to_pdf(md_file, pdf_file):
    """Convert a markdown file to PDF"""
    try:
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert to HTML
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        
        # Add basic HTML structure and styling
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{os.path.basename(md_file)}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    margin: 40px;
                    max-width: 800px;
                }}
                h1, h2, h3, h4, h5, h6 {{ 
                    color: #333; 
                    margin-top: 30px;
                }}
                code {{ 
                    background-color: #f4f4f4; 
                    padding: 2px 4px; 
                    border-radius: 3px;
                    font-family: monospace;
                }}
                pre {{ 
                    background-color: #f4f4f4; 
                    padding: 10px; 
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                table {{ 
                    border-collapse: collapse; 
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{ 
                    border: 1px solid #ddd; 
                    padding: 8px; 
                    text-align: left;
                }}
                th {{ 
                    background-color: #f2f2f2;
                }}
                blockquote {{
                    border-left: 4px solid #ccc;
                    margin: 0;
                    padding-left: 20px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert to PDF
        HTML(string=full_html).write_pdf(pdf_file)
        print(f"Converted: {md_file} -> {pdf_file}")
        return True
        
    except Exception as e:
        print(f"Error converting {md_file}: {e}")
        return False

def main():
    reports_dir = "/home/ivan/utra-deep-research/reports"
    pdf_dir = "/home/ivan/utra-deep-research/reports-pdf"
    
    # Ensure PDF directory exists
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Convert all markdown files
    converted = 0
    total = 0
    
    for filename in os.listdir(reports_dir):
        if filename.endswith('.md'):
            total += 1
            md_path = os.path.join(reports_dir, filename)
            pdf_filename = filename.replace('.md', '.pdf')
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            if convert_md_to_pdf(md_path, pdf_path):
                converted += 1
    
    print(f"\nConversion complete: {converted}/{total} files converted")

if __name__ == "__main__":
    main()
