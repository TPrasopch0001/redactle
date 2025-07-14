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

content = []

with open(output_path, 'r', encoding='utf-8') as f:
    for line in f:
        for word in line.split(','):
            word = regex.sub('',word.lower())
            if(word not in content and (len(word) > 1  or word == 'a')):
                content.append(word)

file_name = 'test.txt'
output_path = os.path.join(script_dir, file_name)
with open(output_path, 'r', encoding='utf-8') as f:
    for line in f:
        for word in line.split():
            word = regex.sub('',word.lower())
            if(word not in content and (len(word) > 1  or word == 'a')):
                content.append(word)

file_name = 'ignoreWords.txt'
output_path = os.path.join(script_dir, file_name)

content.sort()
with open(output_path, 'w', encoding = 'utf-8') as f:
    counter = 0
    for word in content:
        if(counter < 4):
            f.write(word + ",")
            counter += 1
        else:
            f.write(word + "\n")
            counter = 0
    f.flush()

print(content)
class redactFile:
    def __init__(self, content):
        self.content = content
    
    