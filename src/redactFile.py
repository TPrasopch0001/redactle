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
    def __init__(self, sections, wordList = {}, guesses = []):
        self.sections = sections
        self.wordList = wordList
        self.guesses = guesses

    def redact(match):
        return redactChar * len(match.group(0))
    
    def replaceSectionItem(self, sectionItem):
        redactSectionItem = []
        for word in sectionItem['text'].split():
            wordSplit = re.split('[^a-zA-Z0-9]', word)
            for newWord in wordSplit:
                cleaned_word = re.sub("[^a-zA-Z0-9]+", "", newWord)
                if cleaned_word.lower() in ignoreWords or cleaned_word.lower() in self.guesses:
                    redactSectionItem.append(word)
                else:
                    redactWord = re.sub(r'[a-zA-Z0-9]+', redactFile.redact, newWord)
                    redactSectionItem.append(redactWord)
                    if newWord.lower() in self.wordList:
                        self.wordList[newWord.lower()] += 1
                    else:
                        self.wordList[newWord.lower()] = 1
        return " ".join(redactSectionItem)
    
    def replaceSectionHeader(self, header):
        redactHeader = []
        for word in header.split():
            wordSplit = re.split('[^a-zA-Z0-9]', word)
            for newWord in wordSplit:
                cleaned_word = re.sub("[^a-zA-Z0-9]+", "", newWord)
                if cleaned_word.lower() in ignoreWords or cleaned_word.lower() in self.guesses:
                    redactHeader.append(word)
                else:
                    redactWord = re.sub(r'[a-zA-Z0-9]+', redactFile.redact, newWord)
                    redactHeader.append(redactWord)
                    if newWord.lower() in self.wordList:
                        self.wordList[newWord.lower()] += 1
                    else:
                        self.wordList[newWord.lower()] = 1
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
    
    def replaceAllSections(self):
        redactSections = []
        for section in self.sections:
            redactSections.append(self.replaceSection(section))
        self.sections = redactSections

    def save_sections(self, fileName):
        """Saves sections with their content as markdown form into file fileName"""
        with open(fileName, 'w', encoding = 'utf-8') as f:
            f.write(str(self.wordList) + "\n")
            for section in self.sections:
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

    def section_toString(self):
        """Returns the sections in markdown format as a string"""
        output = ""
        for section in self.sections:
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
    
    def makeGuess(self, sections, guess):
        self.guesses.append(guess.lower())
        return redactFile(sections, {}, self.guesses)
        
if __name__ == "__main__":
    site = "https://en.wikipedia.org/wiki/Gundam_(fictional_robot)"
    wikiParser = wp.WikiParser(site)
    sections = wikiParser.extract_wikipedia_sections()
    rf = redactFile(sections)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    redact_name = 'redactPostTest.md'
    redact_path = os.path.join(script_dir, redact_name)
    redact1_name = 'redactPreTest.md'
    redact1_path = os.path.join(script_dir, redact1_name)
    normal_name = 'controlTest.md'
    control_path = os.path.join(script_dir, normal_name)
    wikiParser.save_sections(control_path, sections)
    rf.replaceAllSections()
    rf.save_sections(redact1_path)
    rf = rf.makeGuess(sections, 'gundam')
    rf.replaceAllSections()
    rf.save_sections(redact_path)
