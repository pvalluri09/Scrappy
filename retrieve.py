from bs4 import BeautifulSoup

# Read the HTML file
with open('h2.html.py', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Extract the entire text content from the HTML document
text_content = soup.get_text(separator='\n', strip=True)
print(text_content)
