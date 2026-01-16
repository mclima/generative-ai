from bs4 import BeautifulSoup

def format_html_description(html_content: str) -> str:
    """
    Convert HTML job description to well-formatted plain text.
    Preserves structure with line breaks, bullet points, and proper spacing.
    """
    if not html_content:
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Add line breaks after block elements for better readability
        for br in soup.find_all('br'):
            br.replace_with('\n')
        
        for p in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            p.insert_after('\n\n')
        
        for li in soup.find_all('li'):
            li.insert_before('• ')
            li.insert_after('\n')
        
        # Get text with preserved line breaks
        description_text = soup.get_text(separator=' ')
        
        # Clean up excessive whitespace while preserving line breaks
        lines = [line.strip() for line in description_text.split('\n')]
        description_text = '\n'.join(line for line in lines if line)
        
        return description_text
    except Exception as e:
        print(f"Error formatting HTML description: {e}")
        return html_content
