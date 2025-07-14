import math
import tkinter as tk
from tkinterweb import HtmlFrame
import markdown
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
    for section in sections:
        for sectionItem in section['content']:
            if sectionItem['type'] == 'table':
                break
            elif(checkLengthCounter < 5):
                if sectionItem['type'] == "paragraph":
                    if len(sectionItem['text']) >= 50:
                        checkLengthCounter += 1
            else:
                break
    if checkLengthCounter >= 5:
        # wikiParser.save_sections(output_path, sections)
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
interactFrame = tk.Frame(root)
randbutton = tk.Button(interactFrame, text="Randomize"
                      , width = 10,
                      command= lambda: [print("BUTTON PRESSED!"),getRandomSite()])
randbutton.pack()


inputFrame = tk.Frame(interactFrame)
inputFrame.pack()

def updateGuess(*args):
    inputButton.config(text=f"Guess ({len(entry_text.get())})")

inputButton = tk.Button(inputFrame, text = "Guess (0)")
inputButton.grid(row = 0,column = 1)

entry_text = tk.StringVar()
entry_text.trace_add("write", updateGuess)
inputField = tk.Entry(inputFrame, textvariable=entry_text)
inputField.grid(row = 0, column = 0)
interactFrame.pack()

root.grid_columnconfigure(1,weight=1)
root.grid_rowconfigure(1, weight = 1)
root.mainloop()
