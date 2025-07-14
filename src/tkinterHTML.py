import math
import tkinter as tk
from tkinterweb import HtmlFrame
import markdown
import tempfile
from wikiParser import *
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
file_name = 'htmlTest.txt'
output_path = os.path.join(script_dir, file_name)


def getRandomSite():
    site = "https://en.wikipedia.org/wiki/Special:Random"
    wikiParser = WikiParser(site)
    sections = wikiParser.extract_wikipedia_sections()
    checkLengthCounter = 0
    checkFailCount = 0
    for section in sections:
        if(checkLengthCounter < 3 and checkFailCount < 5):
            for sectionItem in section['content']:
                if sectionItem['type'] == "paragraph":
                    if len(sectionItem['text']) < 25:
                        checkLengthCounter += 1
                    else:
                        checkFailCount += 1
        else:
            break
    if checkLengthCounter >= 3 or checkFailCount >= 5:
        wikiParser.save_sections(output_path, sections)
        m_html = markdown.markdown(wikiParser.section_toString(sections))
        htmlFrame.load_html(m_html)
    else:
        getRandomSite()

root = tk.Tk(baseName= "Redactle")
root.geometry('{}x{}'.format(1200, 600))
root.resizable(width=False, height=False)
htmlFrame = HtmlFrame(root, messages_enabled=False)
getRandomSite()
htmlFrame.pack(side = "left")


    
root.update()
inputFrame = tk.Frame(root)
redbutton = tk.Button(inputFrame, text="Red", fg="red", width = math.floor(root.winfo_width()/100), height = math.floor(root.winfo_height()/100), command= getRandomSite)
redbutton.grid(row = 0, column = 0, sticky = "E W")
inputFrame.pack(side = "right")
root.grid_columnconfigure(1,weight=1)
root.grid_rowconfigure(1, weight = 1)
root.mainloop()
