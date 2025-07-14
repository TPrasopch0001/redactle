from bs4 import BeautifulSoup
import requests
import os


current_directory = os.getcwd()
page = requests.get("https://en.wikipedia.org/wiki/Gundam_(fictional_robot)")

soup = BeautifulSoup(page.content, 'html.parser')

output = []

output.append(soup.find('h1').get_text() + "\n\n")

content_div = soup.find('div', {'id': 'mw-content-text'})
    

# Extract headers (h1, h2, h3, h4, h5, h6)
headers = []
for header in content_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    # Get header level
    level = int(header.name[1])
    # Get text content, removing edit links
    text = header.get_text().strip()
    # Remove [edit] links
    text = re.sub(r'\[edit\]', '', text).strip()
    
    if text:  # Only add non-empty headers
        headers.append({
            'level': level,
            'text': text,
            'tag': header.name
        })

    # Extract paragraphs
    paragraphs = []
    for p in content_div.find_all('p'):
        text = p.get_text().strip()
        if text:  # Only add non-empty paragraphs
            paragraphs.append(text)

textFile = current_directory + "/redactle_test.txt"
with open(textFile, "w", encoding = "utf-8") as f:
    for line in output:
        f.write(line)

htmlFile = current_directory + "/redactle_html.txt"
with open(htmlFile, "w", encoding="utf-8") as f:
    f.write(soup.prettify())
# print(soup.get_text())