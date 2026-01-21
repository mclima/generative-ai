def format_description_to_html(text: str) -> str:
    """
    Convert plain text description to HTML with paragraph tags.
    Preserves structure by wrapping text blocks in <p> tags.
    """
    if not text:
        return ""
    
    # Split by double newlines to identify paragraphs
    paragraphs = text.split('\n\n')
    
    html_parts = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check if it's a list item (starts with bullet or number)
        lines = para.split('\n')
        if len(lines) > 1 and any(line.strip().startswith(('•', '-', '*', '1.', '2.', '3.')) for line in lines):
            # Format each list item as a paragraph
            for line in lines:
                line = line.strip()
                if line:
                    # Keep bullet/dash prefix for visual consistency
                    html_parts.append(f"<p>{line}</p>")
        else:
            # Regular paragraph
            # Replace single newlines with <br> within paragraph
            para_html = para.replace('\n', '<br>')
            html_parts.append(f"<p>{para_html}</p>")
    
    return '\n'.join(html_parts)
