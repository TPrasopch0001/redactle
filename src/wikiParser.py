import os
import requests
from bs4 import BeautifulSoup
import re
import unicodedata

skipped_sections = ['references', 'external links', 'sources', 
                    'notes', 'further reading', 'works cited', 
                    'footnotes', 'sources and further reading', 'references and notes'
                    ]
    
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
        cleaned_text = unicodedata.normalize('NFD', cleaned_text)
        cleaned_text = cleaned_text.encode('ascii','ignore')
        cleaned_text = cleaned_text.decode('utf-8')
        return "".join([c for c in cleaned_text if not unicodedata.combining(c)])
    def extract_wikipedia_sections(self):
        """
        Extract content organized by sections
        """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        content_div = soup.find('div', {'id': 'mw-content-text'})
        
        sections = []
        current_section = None
        
        # First, get the main h1 title and any content before the first h2
        h1_title = soup.find('h1')
        if h1_title:
            main_title = h1_title.get_text().strip()
            current_section = {
                'header': main_title,
                'level': 1,
                'content': []
            }
        
        # Initialize skip_section variable
        skip_section = False
        
        for element in content_div.find_all(['h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'blockquote']):
            if not element.find_parents("table"):
                if element.name.startswith('h'):
                    # New header found
                    if current_section and not skip_section:
                        sections.append(current_section)
                    
                    level = int(element.name[1])
                    text = re.sub(r'\[edit\]', '', element.get_text()).strip()
                    skip_section = text.lower() in skipped_sections
                    if not skip_section:
                        current_section = {
                            'header': text,
                            'level': level,
                            'content': []
                        }
                    else:
                        current_section = None
                elif current_section and element.name in ['p', 'ul', 'ol', 'blockquote']:
                    if element.name == 'p':
                        content_item = element.get_text().strip()
                        if content_item:  # Only add non-empty paragraphs
                            current_section['content'].append({'type': 'paragraph', 'text': self.clean_footnote(content_item)})
                    elif element.name in ['ul', 'ol']:
                        list_item = self.extract_list(element)
                        if list_item['items']:
                            current_section['content'].append(list_item)
                    elif element.name == 'blockquote':
                        content_item = element.get_text().strip()
                        if content_item:
                            current_section['content'].append({'type' : 'blockquote', 'text' : self.clean_footnote(content_item)})

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

                elif content_item['type'] == 'blockquote':
                    print(f"QUOTE")
                    print(f"{item['type']}\n")
                
    def save_sections(self, fileName, sections):
        """Saves sections with their content as markdown form into file fileName"""
        with open(fileName, 'w', encoding = 'utf-8') as f:
            for section in sections:
                # f.write(f"\nSECTION: {section['header']} (Level {section['level']})\n")
                f.write(f"{'#' * section['level']} {section['header']}\n")
                
                
                for i, content_item in enumerate(section['content'], 1):
                    if content_item['type'] == 'paragraph':
                        f.write(f"{content_item['text']}\n")
                    
                    if content_item['type'] == 'blockquote':
                        f.write(f"> {content_item['text']}\n")
                    
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
                output += (f"{'#' * section['level']} {section['header']}\n\n")
                
                
                for i, content_item in enumerate(section['content'], 1):
                    if content_item['type'] == 'paragraph':
                        output += (f"{content_item['text']}\n\n")
                    
                    if content_item['type'] == 'blockquote':
                        output += (f"> {content_item['text']}\n\n")
                    
                    elif content_item['type'] == 'list':
                        # f.write(f"   Type: {content_item['list_type']} list\n")
                        if content_item['list_type'] == 'ordered':
                            for j, item in enumerate(content_item['items'], 1):
                                output += (f"{j}. {item['text']}\n")
                        else:
                            for item in content_item['items']:
                                output += (f"- {item['text']}\n")
        return output


script_dir = os.path.dirname(os.path.abspath(__file__))

file_name = 'test.html'
output_path = os.path.join(script_dir, file_name)


if __name__ == "__main__":
    
    site = "https://en.wikipedia.org/wiki/Raj_%26_DK"
    response = requests.get(site)
    soup = BeautifulSoup(response.content, 'html.parser')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
        f.flush()
        f.close()
        
    wikiParser = WikiParser(site)
    sections = wikiParser.extract_wikipedia_sections()
        # save_sections('redactle_test2.md',extract_wikipedia_sections("https://en.wikipedia.org/wiki/Gundam_(fictional_robot)"))
    wikiParser.save_sections("wikiParserTest.md", sections)