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

rf : redactFile.redactFile
sections : list[dict[str, str | int]]

def generateHTML(md : str) -> None:
    html = "<!doctype html> \n <html lang=\"en-US\"> <head> <link href=\"style.css\" rel=\"stylesheet\" /> \n</head> \n<body>\n"
    html += markdown.markdown(md)
    html += "\n</body> \n</html>"
    return html

def loadHTML(rf : redactFile, htmlFrame : HtmlFrame) -> None:
    m_html = generateHTML(rf.section_toString())
    htmlFrame.load_html(m_html)
    with open(os.path.join(script_dir, 'styles.css')) as css:
        htmlFrame.add_css(css)

def getRandomSite(htmlFrame : HtmlFrame) -> tuple[redactFile.redactFile, dict[str, str | int]]:
    site = "https://en.wikipedia.org/wiki/Special:Random"
    wikiParser = WikiParser(site)
    global sections
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
        global rf
        rf = redactFile.redactFile(sections, {}, [])
        rf.replaceAllSections()
        loadHTML(rf, htmlFrame)
    else:
        getRandomSite(htmlFrame)

root = tk.Tk()
root.geometry('{}x{}'.format(1200, 600))
root.config(background="#292e33")
root.resizable(width=False, height=False)

# debugging using known site
# site = "https://en.wikipedia.org/wiki/Shin%27asahi,_Shiga"
# wikiParser = WikiParser(site)
# sections = wikiParser.extract_wikipedia_sections()
# rf = redactFile.redactFile(sections, {}, [])
# rf.replaceAllSections()
# loadHTML(rf, htmlFrame)
# print(sections[0])

entry_text = tk.StringVar()
def createGame(frame : tk.Frame):
    global entry_text
    for widget in frame.master.winfo_children():
        if widget is not frame:
            widget.destroy()
    frame.config(background="#292e33")
    htmlFrame = HtmlFrame(frame.master, messages_enabled=False)
    htmlFrame.pack(side = "left")

    randButton = tk.Button(frame, text="Randomize"
                        , width = 10,
                        command= lambda: getRandomSite(htmlFrame))
    randButton.pack()
    inputFrame = tk.Frame(frame)
    inputFrame.pack()
    inputButton = tk.Button(inputFrame, text = "Guess (0)", command = lambda: inputGuess(rf, htmlFrame))
    inputButton.grid(row = 0,column = 1)
    entry_text.trace_add("write", lambda x,y,z : inputButton.config(text=f"Guess ({len(entry_text.get())})"))
    inputField = tk.Entry(inputFrame, textvariable=entry_text)
    inputField.bind("<Return>", lambda x: (inputGuess(rf, htmlFrame)))
    inputField.grid(row = 0, column = 0)
    testDestroyButton = tk.Button(inputFrame, text = "Delete Me", command = lambda: deleteGame(frame.master))
    testDestroyButton.grid(row = 3, column = 0)
    frame.pack()
    getRandomSite(htmlFrame)

def deleteGame(root):
    for widget in root.winfo_children():
        widget.destroy()
    newFrame = tk.Frame(root)
    label = tk.Button(newFrame, text = "Testing", command = lambda: createGame(tk.Frame(root)))
    label.grid(row = 0, column = 0)
    newFrame.pack()
    
def initWindow():
    global root
    
def inputGuess(rf : redactFile.redactFile, htmlFrame : HtmlFrame):
    guess = entry_text.get()
    rf = rf.makeGuess(sections, guess.lower())
    rf.replaceAllSections()
    print(rf.checkWinCond())
    loadHTML(rf, htmlFrame)
    entry_text.set("")


interactFrame = tk.Frame(root)
createGame(interactFrame)

root.grid_columnconfigure(1,weight=1)
root.grid_rowconfigure(1, weight = 1)
root.mainloop()
