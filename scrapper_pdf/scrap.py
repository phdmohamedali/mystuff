import os
import requests
from weasyprint import HTML

import pdfkit
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Set to store visited URLs to avoid duplicate crawling
visited_urls = set()
def save_page_as_pdf(url, output_folder):
    """Saves the given URL as a PDF using WeasyPrint."""
    try:
        filename = urlparse(url).path.replace('/', '_') or 'index'
        pdf_path = os.path.join(output_folder, f"{filename}.pdf")
        html = HTML(url)
        html.write_pdf(pdf_path)
        print(f"Saved: {pdf_path}")
    except Exception as e:
        print(f"Error saving {url} as PDF: {e}")

        
def crawl_and_convert(url, output_folder, depth=2):
    """Recursively crawls webpages and converts them to PDFs."""
    if depth == 0 or url in visited_urls:
        return
    
    visited_urls.add(url)
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        save_page_as_pdf(url, output_folder)
        
        for link in soup.find_all('a', href=True):
            next_url = urljoin(url, link['href'])
            if urlparse(next_url).netloc == urlparse(url).netloc:  # Stay within domain
                crawl_and_convert(next_url, output_folder, depth - 1)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

if __name__ == "__main__":
    start_url = "https://google.com"  # Change this to your starting URL
    output_dir = "webpages_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    crawl_and_convert(start_url, output_dir, depth=2)
