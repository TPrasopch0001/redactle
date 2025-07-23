import math
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
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
site : str
guesses : list[list[str, int]] = []

def generateHTML(md : str) -> str:
    html = "<!doctype html> \n <html lang=\"en-US\"> <head> <link href=\"style.css\" rel=\"stylesheet\" /> \n</head> \n<body>\n"
    html += markdown.markdown(md)
    html += "\n</body> \n</html>"
    return html

def loadHTML(html : str, htmlFrame : HtmlFrame) -> None:
    htmlFrame.load_html(html)
    with open(os.path.join(script_dir, 'styles.css')) as css:
        htmlFrame.add_css(css)

def getRandomSite(htmlFrame : HtmlFrame) -> tuple[redactFile.redactFile, dict[str, str | int]]:
    global site
    site = "https://en.wikipedia.org/wiki/Special:Random"
    wikiParser = WikiParser(site)
    global sections
    sections = wikiParser.extract_wikipedia_sections()
    checkLengthCounter = 0
    for section in sections:
        for sectionItem in section['content']:
            if sectionItem['type'] == 'table':
                getRandomSite(htmlFrame)
            elif(checkLengthCounter < 5):
                if sectionItem['type'] == "paragraph":
                    if len(sectionItem['text']) >= 100:
                        checkLengthCounter += 1
            else:
                break
    if checkLengthCounter >= 3:
        global rf
        rf = redactFile.redactFile(sections, {}, [])
        rf.replaceAllSections()
        loadHTML(generateHTML(rf.redactToString()), htmlFrame)
    else:
        getRandomSite(htmlFrame)

def winGame(rf : redactFile.redactFile, htmlFrame : HtmlFrame):
    loadHTML(generateHTML(rf.origToString()), htmlFrame)
# debugging using known site
# site = "https://en.wikipedia.org/wiki/Shin%27asahi,_Shiga"
# wikiParser = WikiParser(site)
# sections = wikiParser.extract_wikipedia_sections()
# rf = redactFile.redactFile(sections, {}, [])
# rf.replaceAllSections()
# loadHTML(generateHTML(rf.redactToString()), htmlFrame)
# print(sections[0])

def createGame(root : tk.Tk):
    for widget in root.winfo_children():
        widget.destroy()
    htmlFrame = HtmlFrame(root, messages_enabled=False)
    htmlFrame.pack(side = 'left', fill = "both")

    interactFrame = tk.Frame(root)
    interactFrame.config(background= root['bg'])
    inputFrame = tk.Frame(interactFrame, background=root['bg'])
    inputFrame.grid(row = 3, column = 0,pady = 10)
    entry_text = tk.StringVar()
    entry_text.trace_add("write", lambda x,y,z : inputButton.config(text=f"Guess ({len(entry_text.get())})"))
    
    inputFieldFrame = tk.Frame(inputFrame, background=root['bg'])
    inputField = tk.Entry(inputFieldFrame, textvariable=entry_text, width = 10, font = ('Sans Serif', 24))
    inputField.bind("<Return>", lambda x: (inputGuess(rf, htmlFrame, entry_text, guessList)))
    inputField.grid(row = 0, column = 0, padx = 5)
    inputButton = tk.Button(inputFieldFrame, text = "Guess (0)", command = lambda: inputGuess(rf, htmlFrame, entry_text, guessList), font = ('Sans Serif', 12))
    inputButton.grid(row = 0,column = 1)
    
    inputFieldFrame.grid(row = 0, column = 0)
    
    guessList = makeGuessTree(inputFrame)
    guessList.grid(row = 1, column = 0, pady = 10)
    optionFrame = tk.Frame(interactFrame, background = root['bg'])
    randButton = tk.Button(optionFrame, text="Randomize", width = 10, command= lambda: [deleteGame(root), createGame(root)], font = ('Sans Serif', 12))
    randButton.grid(row = 0, column = 1, sticky="e")
    exitButton = tk.Button(optionFrame, text = "Exit", command = lambda: deleteGame(root), font = ('Sans Serif', 12))
    exitButton.grid(row = 0, column = 0, sticky="w")
    optionFrame.grid(row = 0, column = 0, pady = 5)
    interactFrame.pack()
    getRandomSite(htmlFrame)

def deleteGame(root : tk.Tk):
    global guesses
    for widget in root.winfo_children():
        widget.destroy()
    guesses = []
    initWindow(root)
    
def initWindow(root : tk.Tk):
    createButton = tk.Button(root, text = "Start Game", command = lambda: createGame(root), font = ('Sans Serif', 24))
    createButton.pack()

def inputGuess(rf : redactFile.redactFile, htmlFrame : HtmlFrame, entry_text : tk.StringVar, guessView : ttk.Treeview):
    global guesses
    guess = entry_text.get()
    rf, guessCount = rf.makeGuess(sections, guess.lower())
    rf.replaceAllSections()
    if(rf.checkWinCond()):
        winGame(rf, htmlFrame)
    else:
        loadHTML(generateHTML(rf.redactToString()), htmlFrame)
    entry_text.set("")
    guesses.append([guess, guessCount])
    updateGuessList(guessView)


def makeGuessTree(frame : tk.Frame):
    headers = ['Guess', 'Count']
    tree = ttk.Treeview(frame, columns = ['Guess', 'Count'], show="headings")
    vsb = tk.Scrollbar(orient="vertical", command=tree.yview)
    hsb = tk.Scrollbar(orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    for col in headers:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby(tree, c, 0))
    return tree

def updateGuessList(tree : ttk.Treeview):
    global guesses
    if(tree.get_children()):
        tree.delete(*tree.get_children())

    for item in guesses:
        print(item)
        tree.insert('', 'end', values=item)


def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    #data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('{}x{}'.format(1200, 600))
    root.config(background="#292e33")
    root.grid_columnconfigure(1,weight=1)
    root.grid_rowconfigure(1, weight = 1)
    root.resizable(width=False, height=False)
    initWindow(root)

    root.mainloop()
