import math
import tkinter as tk
from tkinterweb import HtmlFrame
import markdown
from wikiParser import *
import os
import redactFile

script_dir = os.path.dirname(os.path.abspath(__file__))
file_name = 'htmlTest.txt'
output_path = os.path.join(script_dir, file_name)

def generateHTML(md):
    html = "<!doctype html> \n <html lang=\"en-US\"> <head> <link href=\"style.css\" rel=\"stylesheet\" /> \n</head> \n<body>\n"
    html += markdown.markdown(md)
    html += "\n</body> \n</html>"
    return html

def loadHTML(rf):
    m_html = generateHTML(rf.section_toString())
    htmlFrame.load_html(m_html)
    with open(os.path.join(script_dir, 'styles.css')) as css:
        htmlFrame.add_css(css)

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
        rf = redactFile.redactFile(sections, {}, {})
        rf.replaceAllSections()
        loadHTML(rf)
    else:
        getRandomSite()

root = tk.Tk()
root.title = "Redactle"
root.geometry('{}x{}'.format(1200, 600))
root.config(background="#292e33")
root.resizable(width=False, height=False)
htmlFrame = HtmlFrame(root, messages_enabled=False)
htmlFrame.pack(side = "left")

site = "https://en.wikipedia.org/wiki/Special:Random"
wikiParser = WikiParser(site)
sections = wikiParser.extract_wikipedia_sections()
print(sections[0])
rf = redactFile.redactFile(sections, {}, [])
rf.replaceAllSections()
loadHTML(rf)
root.update()
interactFrame = tk.Frame(root)
interactFrame.config(background="#292e33")
randbutton = tk.Button(interactFrame, text="Randomize"
                      , width = 10,
                      command= lambda: [print("BUTTON PRESSED!"),getRandomSite()])
randbutton.pack()


inputFrame = tk.Frame(interactFrame)
inputFrame.pack()

def updateGuess(*args):
    inputButton.config(text=f"Guess ({len(entry_text.get())})")

def inputGuess(rf):
    guess = entry_text.get()
    rf = rf.makeGuess(sections, guess.lower())
    rf.replaceAllSections()
    loadHTML(rf)
    entry_text.set("")

inputButton = tk.Button(inputFrame, text = "Guess (0)", command = lambda: inputGuess(rf))
inputButton.grid(row = 0,column = 1)

entry_text = tk.StringVar()
entry_text.trace_add("write", updateGuess)
inputField = tk.Entry(inputFrame, textvariable=entry_text)
inputField.bind("<Return>", lambda x: (inputGuess(rf)))
inputField.grid(row = 0, column = 0)
interactFrame.pack()

root.grid_columnconfigure(1,weight=1)
root.grid_rowconfigure(1, weight = 1)
root.mainloop()
