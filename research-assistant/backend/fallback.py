from typing import Dict

def is_valid_topic(topic: str) -> bool:
    """Check if topic appears to be a valid research query."""
    if not topic or len(topic.strip()) < 3:
        return False
    
    topic_lower = topic.lower()
    
    # Check for obvious random patterns
    if any(pattern in topic_lower for pattern in ['xyz', '123', '999', 'abc123', 'test123', 'nonexistent']):
        return False
    
    # Check for excessive numbers
    digit_count = sum(1 for c in topic_lower if c.isdigit())
    if digit_count > len(topic_lower) * 0.3:  # More than 30% digits
        return False
    
    # Check for reasonable word structure
    words = topic_lower.split()
    valid_words = 0
    for word in words:
        clean_word = word.strip('.,!?;:')
        if len(clean_word) > 15:  # Unusually long single word
            continue
        if len(clean_word) > 2:
            vowels = sum(1 for c in clean_word if c in 'aeiou')
            consonants = sum(1 for c in clean_word if c.isalpha() and c not in 'aeiou')
            # Reasonable vowel/consonant ratio
            if vowels > 0 and consonants > 0:
                valid_words += 1
    
    return valid_words >= len(words) / 2

def generate_fallback_response(topic: str, errors: Dict[str, str]) -> str:
    """
    Generate a helpful fallback response when the research pipeline fails.
    Provides informative message and suggested resources.
    """
    
    error_summary = []
    if errors.get("search_error"):
        error_summary.append("• Search service unavailable")
    if errors.get("scraper_error"):
        error_summary.append("• Content extraction failed")
    if errors.get("writer_error"):
        error_summary.append("• Outline generation failed")
    if errors.get("editor_error"):
        error_summary.append("• Editing service failed")
    
    # Check if topic is valid
    if not is_valid_topic(topic):
        suggested_resources = """
**Please provide a valid research topic.** Your query appears to be incomplete or contains random characters.

**Examples of valid topics:**
- "climate change effects on polar bears"
- "latest developments in quantum computing"
- "history of the Roman Empire"
- "benefits of Mediterranean diet"
"""
    else:
        suggested_resources = generate_suggested_links(topic)
    
    fallback_message = f"""## Research Assistant - Service Temporarily Limited

We encountered issues while researching **"{topic}"**. Here's what happened:

{chr(10).join(error_summary) if error_summary else "• Multiple service components experienced issues"}

---

### 📚 Suggested Resources to Explore

While our automated research is temporarily limited, here are some trusted resources where you can find information about **{topic}**:

{suggested_resources}

---

### 💡 What You Can Do

1. **Try again in a few moments** - Transient issues often resolve quickly
2. **Refine your topic** - Try a more specific or different search term
3. **Use the links above** - Explore these curated resources directly
4. **Check back later** - Our system logs issues and improves continuously

---

### 🔧 Technical Details

If you're a developer, here's what we tracked:
```
Search Status: {"✅ Success" if not errors.get("search_error") else f"❌ {errors.get('search_error')}"}
Scraper Status: {"✅ Success" if not errors.get("scraper_error") else f"❌ {errors.get('scraper_error')}"}
Writer Status: {"✅ Success" if not errors.get("writer_error") else f"❌ {errors.get('writer_error')}"}
Editor Status: {"✅ Success" if not errors.get("editor_error") else f"❌ {errors.get('editor_error')}"}
```

We apologize for the inconvenience and appreciate your patience! 🙏
"""
    
    return fallback_message


def generate_suggested_links(topic: str) -> str:
    """
    Generate direct search links for the topic.
    """
    encoded_topic = topic.replace(' ', '+')
    
    return f"""### 🔍 Search Resources

- [Google News](https://news.google.com/search?q={encoded_topic}) - Latest news and current events
- [Google Search](https://www.google.com/search?q={encoded_topic}) - General web search
- [Wikipedia](https://en.wikipedia.org/wiki/Special:Search?search={encoded_topic}) - Encyclopedia articles
- [Google Scholar](https://scholar.google.com/scholar?q={encoded_topic}) - Academic papers and research
- [Reddit Search](https://www.reddit.com/search/?q={encoded_topic}) - Community discussions
- [YouTube](https://www.youtube.com/results?search_query={encoded_topic}) - Video content"""
