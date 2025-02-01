import os
import requests
import sys
from weasyprint import HTML
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

# Set to store visited URLs to avoid duplicate crawling
visited_urls = set()
sys.setrecursionlimit(5000)

def save_page_as_pdf(url, output_folder):
    """Saves the given URL as a PDF in the specified output folder."""
    try:
        filename = urlparse(url).path.replace('/', '_') or 'index'
        pdf_path = os.path.join(output_folder, f"{filename}.pdf")
        html = HTML(url)
        html.write_pdf(pdf_path)
        print(f"Saved: {pdf_path}")
    except Exception as e:
        print(f"Error saving {url} as PDF: {e}")

def crawl_and_convert(start_url, output_folder, max_depth=2):
    """Crawls webpages iteratively (not recursively) and converts them to PDFs."""
    queue = deque([(start_url, 0)])  # (URL, depth)
    
    while queue:
        url, depth = queue.popleft()
        
        if depth > max_depth or url in visited_urls:
            continue
        
        visited_urls.add(url)
        
        try:
            response = requests.get(url, timeout=10)  # Add timeout to prevent hanging
            if response.status_code != 200:
                print(f"Failed to retrieve {url}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            save_page_as_pdf(url, output_folder)
            
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                if urlparse(next_url).netloc == urlparse(start_url).netloc and next_url not in visited_urls:
                    queue.append((next_url, depth + 1))
        except Exception as e:
            print(f"Error crawling {url}: {e}")

if __name__ == "__main__":
    start_url = "https://docs.snowflake.com/"  # Change this to your starting URL
    output_dir = "webpages_pdfs"
    os.makedirs(output_dir, exist_ok=True)

    print("Installing necessary dependencies...")
    # os.system("brew install pango cairo gdk-pixbuf libffi")
    # os.system("pip install -r requirements.txt")

    crawl_and_convert(start_url, output_dir, max_depth=2)


if __name__ == "__main__":
    start_url =  "https://docs.snowflake.com/"  # Change this to your starting URL
    output_dir = "webpages_pdfs"
    os.makedirs(output_dir, exist_ok=True)

    print("Installing necessary dependencies...")
    os.system("brew install pango cairo gdk-pixbuf libffi")
    os.system("pip install -r requirements.txt")

    crawl_and_convert(start_url, output_dir, max_depth=2)
