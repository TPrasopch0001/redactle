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


site = "https://en.wikipedia.org/wiki/Gundam_(fictional_robot)"
wikiParser = WikiParser(site)
sections = wikiParser.extract_wikipedia_sections()
# save_sections('redactle_test2.md',extract_wikipedia_sections("https://en.wikipedia.org/wiki/Gundam_(fictional_robot)"))


m_html = markdown.markdown(wikiParser.section_toString(sections))
temp_html = tempfile.NamedTemporaryFile(mode='w', encoding = 'utf-8', delete = False)
with open(output_path, mode = 'w', encoding = 'utf-8') as f:
    f.write(m_html)
    f.flush()
    f.close()
temp_html.write(m_html)
temp_html.flush()

root = tk.Tk(baseName= "Redactle")
root.geometry('{}x{}'.format(1200, 600))
root.resizable(width=False, height=False)
htmlFrame = HtmlFrame(root, messages_enabled=False)
htmlFrame.load_file(temp_html.name)
htmlFrame.pack(side = "left")

root.update()
inputFrame = tk.Frame(root)
redbutton = tk.Button(inputFrame, text="Red", fg="red", width = math.floor(root.winfo_width()/100))
redbutton.grid(row = 0, column = 0, sticky = "E W")
inputFrame.pack(side = "right")
root.grid_columnconfigure(1,weight=1)
root.grid_rowconfigure(1, weight = 1)

root.mainloop()
temp_html.close()
os.unlink(temp_html.name)