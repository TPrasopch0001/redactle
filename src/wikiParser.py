import requests
from bs4 import BeautifulSoup
import re

class WikiParser:
    def __init__(self,url):
        self.url = url

    def clean_footnote(self,text):
        """
        Remove footnote references like [1], [2], [note 1], etc. from text
        """
        
        # Remove various footnote patterns
        patterns = [
            r'\[\d+\]',                    # [1], [2], [123]
            r'\[note \d+\]',               # [note 1], [note 2]
            r'\[citation needed\]',         # [citation needed]
            r'\[when\?\]',                 # [when?]
            r'\[who\?\]',                  # [who?]
            r'\[where\?\]',                # [where?]
            r'\[why\?\]',                  # [why?]
            r'\[how\?\]',                  # [how?]
            r'\[which\?\]',                # [which?]
            r'\[clarification needed\]',    # [clarification needed]
            r'\[dubious - discuss\]',      # [dubious – discuss]
            r'\[according to whom\?\]',     # [according to whom?]
            r'\[better source needed\]',    # [better source needed]
            r'\[original research\?\]',     # [original research?]
            r'\[peacock terms\]',          # [peacock terms]
            r'\[weasel words\]',           # [weasel words]
            r'\[verify\]',                 # [verify]
            r'\[further explanation needed\]', # [further explanation needed]
            r'\[\w+\s?\d*\]',              # Generic pattern for other bracketed references
        ]
        
        cleaned_text = text
        for pattern in patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Clean up multiple spaces and trim
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def extract_wikipedia_sections(self):
        """
        Extract content organized by sections
        """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        content_div = soup.find('div', {'id': 'mw-content-text'})
        
        sections = [ {'header' : soup.find('h1').get_text().strip(), 'level' : 1, 'content' : []}]
        current_section = None
        skip_section = False
        
        for element in content_div.find_all(['h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol']):
            if element.name.startswith('h'):
                # New header found
                if current_section and not skip_section:
                    sections.append(current_section)
                
                level = int(element.name[1])
                text = re.sub(r'\[edit\]', '', element.get_text()).strip()
                skip_section = text.lower() in ['references', 'external links']
                if not skip_section:
                    current_section = {
                        'header': text,
                        'level': level,
                        'content': []
                    }
                else:
                    current_section = None
            elif current_section and element.name in ['p', 'ul', 'ol']:
                if element.name == 'p':
                    content_item = element.get_text().strip()
                    current_section['content'].append({'type' : 'paragraph', 'text' : self.clean_footnote(content_item)})
                elif element.name in ['ul', 'ol']:
                    list_item = self.extract_list(element)
                    if list_item['items']:
                        current_section['content'].append(list_item)
        
        # Add the last section
        if current_section:
            sections.append(current_section)
        
        return sections

    def extract_list(self, list_element):
        """
        Extract list items with their links, handling nested lists properly
        """
        list_type = 'ordered' if list_element.name == 'ol' else 'unordered'
        items = []
        
        for li in list_element.find_all('li', recursive=False):  # Only direct children
            # Get text content excluding nested lists
            text = self.extract_text_excluding_nested_lists(li)

            # Handle nested lists
            nested_lists = []
            for nested_list in li.find_all(['ul', 'ol'], recursive=False):
                nested_items = self.extract_list(nested_list)
                nested_lists.append(nested_items)
            
            if text.strip():
                item = {
                    'text': self.clean_footnote(text)
                }
                if nested_lists:
                    item['nested_lists'] = nested_lists
                items.append(item)
        
        return {
            'type': 'list',
            'list_type': list_type,
            'items': items
        }
        
    def extract_text_excluding_nested_lists(self, element):
        """
        Extract text from an element while excluding text from nested lists
        """
        # Clone the element to avoid modifying the original
        temp_element = element.__copy__()
        
        # Remove all nested ul/ol elements
        for nested_list in temp_element.find_all(['ul', 'ol']):
            nested_list.decompose()
        
        return temp_element.get_text().strip()
    
    # Example usage for sections
    def print_sections(self, sections):
        """Print sections with their content including lists"""
        for section in sections:
            print(f"SECTION: {section['header']} (Level {section['level']})\n")
            
            for i, content_item in enumerate(section['content'], 1):
                if content_item['type'] == 'paragraph':
                    print(f"{content_item['text']}\n")
                
                
                elif content_item['type'] == 'list':
                    print(f"   Type: {content_item['list_type']} list")
                    for j, item in enumerate(content_item['items'], 1):
                        print(f"{item['text']}\n")
                        
    def save_sections(self, fileName, sections):
        """Saves sections with their content as markdown form into file fileName"""
        with open(fileName, 'w', encoding = 'utf-8') as f:
            for section in sections:
                # f.write(f"\nSECTION: {section['header']} (Level {section['level']})\n")
                f.write(f"\n{'#' * section['level']} {section['header']}\n")
                
                
                for i, content_item in enumerate(section['content'], 1):
                    if content_item['type'] == 'paragraph':
                        f.write(f"{content_item['text']}\n")
                    
                    
                    elif content_item['type'] == 'list':
                        # f.write(f"   Type: {content_item['list_type']} list\n")
                        if content_item['list_type'] == 'ordered':
                            for j, item in enumerate(content_item['items'], 1):
                                f.write(f"{j}. {item['text']}\n")
                        else:
                            for item in content_item['items']:
                                f.write(f"- {item['text']}\n")
                        
    def section_toString(self, sections):
        """Returns the sections in markdown format as a string"""
        output = ""
        for section in sections:
                # f.write(f"\nSECTION: {section['header']} (Level {section['level']})\n")
                output += (f"\n{'#' * section['level']} {section['header']}\n")
                
                
                for i, content_item in enumerate(section['content'], 1):
                    if content_item['type'] == 'paragraph':
                        output += (f"{content_item['text']}\n")
                    
                    
                    elif content_item['type'] == 'list':
                        # f.write(f"   Type: {content_item['list_type']} list\n")
                        if content_item['list_type'] == 'ordered':
                            for j, item in enumerate(content_item['items'], 1):
                                output += (f"{j}. {item['text']}\n")
                        else:
                            for item in content_item['items']:
                                output += (f"- {item['text']}\n")
        return output



if __name__ == "__main__":
    site = "https://en.wikipedia.org/wiki/Gundam_(fictional_robot)"
    wikiParser = WikiParser(site)
    sections = wikiParser.extract_wikipedia_sections()
        # save_sections('redactle_test2.md',extract_wikipedia_sections("https://en.wikipedia.org/wiki/Gundam_(fictional_robot)"))
    wikiParser.save_sections("wikiParserTest.md", sections)
