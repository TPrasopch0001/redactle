import wikiParser as wp
import math
import markdown
import os
import re

regex = re.compile('[^a-zA-Z]')

redactChar = '█'

script_dir = os.path.dirname(os.path.abspath(__file__))

file_name = 'ignoreWords.txt'
output_path = os.path.join(script_dir, file_name)

ignoreWords = []

with open(output_path, 'r', encoding='utf-8') as f:
    for line in f:
        for word in line.split(','):
            word = regex.sub('',word.lower())
            if(word not in ignoreWords and (len(word) > 1  or word == 'a')):
                ignoreWords.append(word)

    """
    Takes in a text file that holds a redactle puzzle and collects words that are kept
    Used for generating words that are often ignored
    """
# file_name = 'test.txt'
# output_path = os.path.join(script_dir, file_name)
# with open(output_path, 'r', encoding='utf-8') as f:
#     for line in f:
#         for word in line.split():
#             word = regex.sub('',word.lower())
#             if(word not in ignoreWords and (len(word) > 1  or word == 'a')):
#                 ignoreWords.append(word)

# file_name = 'ignoreWords.txt'
# output_path = os.path.join(script_dir, file_name)

    """
    Saves all of the words in the ignoreWords list to a file
    """
# ignoreWords.sort()
# with open(output_path, 'w', encoding = 'utf-8') as f:
#     counter = 0
#     for word in ignoreWords:
#         if(counter < 4):
#             f.write(word + ",")
#             counter += 1
#         else:
#             f.write(word + "\n")
#             counter = 0
#     f.flush()


class redactFile:
    def __init__(self, content):
        self.content = content
    
    def redact(match):
        return redactChar * len(match.group(0))
    
    def replaceSectionItem(self, sectionItem):
        redactSectionItem = []
        for word in sectionItem['text'].split():
            if word in ignoreWords:
                redactSectionItem.append(word)
            else:
                redactWord = re.sub(r'[a-zA-Z0-9]+', redactFile.redact, word)
                redactSectionItem.append(redactWord)
        return " ".join(redactSectionItem)
    
    def replaceSectionHeader(self, header):
        redactHeader = []
        for word in header.split():
            if word in ignoreWords:
                redactHeader.append(word)
            else:
                redactWord = re.sub(r'[a-zA-Z0-9]+', redactFile.redact, word)
                redactHeader.append(redactWord)
        return " ".join(redactHeader)
    
    def replaceSectionList(self, section):
        redactItems = []
        keys = section.keys()
        for listItem in section['items']:
            newItem = {'text': self.replaceSectionItem(listItem)}
            if 'nested_lists' in keys:
                newItem['nested_lists'] = self.replaceSectionList(listItem)
            redactItems.append(newItem)
        return redactItems
    
    def replaceSection(self, section):
        redactSection = []
        for sectionItem in section['content']:
            if(sectionItem['type'] == 'list'):
                redactItems = self.replaceSectionList(sectionItem)
                redactSection.append({'type' : 'list', 'list_type' : sectionItem['list_type'], 'items' : redactItems})
            else:
                redactSectionText = self.replaceSectionItem(sectionItem)
                redactSection.append({'type' : sectionItem['type'], 'text' : redactSectionText})
        return {'header' : self.replaceSectionHeader(section['header']), 'level' : section['level'], 'content' : redactSection}
    
    def replaceAllSections(self, sections):
        redactSections = []
        for section in sections:
            redactSections.append(self.replaceSection(section))
        return redactSections

    def save_sections(self, fileName, sections):
        """Saves sections with their content as markdown form into file fileName"""
        with open(fileName, 'w', encoding = 'utf-8') as f:
            for section in sections:
                # f.write(f"\nSECTION: {section['header']} (Level {section['level']})\n")
                f.write(f"\n{'#' * section['level']} {section['header']}\n\n")
                
                
                for i, content_item in enumerate(section['content'], 1):
                    if content_item['type'] == 'paragraph':
                        f.write(f"{content_item['text']}\n\n")
                    
                    if content_item['type'] == 'blockquote':
                        f.write(f"> {content_item['text']}\n\n")
                    
                    elif content_item['type'] == 'list':
                        # f.write(f"   Type: {content_item['list_type']} list\n")
                        if content_item['list_type'] == 'ordered':
                            for j, item in enumerate(content_item['items'], 1):
                                f.write(f"{j}. {item['text']}\n")
                        else:
                            for item in content_item['items']:
                                f.write(f"- {item['text']}\n")


if __name__ == "__main__":
    site = "https://en.wikipedia.org/wiki/Raj_%26_DK"
    wikiParser = wp.WikiParser(site)
    sections = wikiParser.extract_wikipedia_sections()
    rf = redactFile(sections)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    redact_name = 'redactTest.md'
    redact_path = os.path.join(script_dir, redact_name)
    normal_name = 'controlTest.md'
    control_path = os.path.join(script_dir, normal_name)
    
    wikiParser.save_sections(control_path, sections)
    
    rf.save_sections(redact_path, rf.replaceAllSections(sections))