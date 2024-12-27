import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import zipfile

# Base URL of the Kubernetes documentation
BASE_URL = "https://kubernetes.io/docs/home/"
DOMAIN = "kubernetes.io"

# Directory to store the text files temporarily
OUTPUT_DIR = "kubernetes_docs"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

# Set to store visited URLs
visited_urls = set()

def fetch_and_save_page(url, output_dir):
    """Fetch a page, extract its text, and save it as a .txt file."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the main content of the page
        content = soup.find("main")  # Kubernetes docs use <main> for main content
        if not content:
            return

        # Extract text and clean it
        text = content.get_text(separator="\n", strip=True)

        # Generate a valid filename from the URL
        parsed_url = urlparse(url)
        filename = parsed_url.path.strip("/").replace("/", "_") or "index"
        filename = f"{filename}.txt"

        # Save the text to a file
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(text)

        print(f"Saved: {filepath}")
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")

def crawl_and_save(base_url, output_dir):
    """Crawl the documentation site and save all pages as .txt files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    to_visit = [base_url]

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)
        try:
            response = requests.get(current_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Save the current page
            fetch_and_save_page(current_url, output_dir)

            # Find all links on the page
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = urljoin(current_url, href)

                # Ensure the link is within the same domain and not already visited
                if DOMAIN in urlparse(full_url).netloc and full_url not in visited_urls:
                    to_visit.append(full_url)
        except Exception as e:
            print(f"Failed to crawl {current_url}: {e}")

def create_zip(output_dir, zip_filename):
    """Create a zip file containing all .txt files in the output directory."""
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.endswith(".txt"):
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, output_dir)
                    zipf.write(filepath, arcname)
    print(f"Created zip file: {zip_filename}")

def main():
    # Step 1: Crawl and save documentation
    print("Crawling Kubernetes documentation...")
    crawl_and_save(BASE_URL, OUTPUT_DIR)

    # Step 2: Create a zip file
    zip_filename = "kubernetes_docs.zip"
    print("Creating zip file...")
    create_zip(OUTPUT_DIR, zip_filename)

    # Step 3: Clean up (optional)
    print("Cleaning up temporary files...")
    for root, _, files in os.walk(OUTPUT_DIR):
        for file in files:
            os.remove(os.path.join(root, file))
    os.rmdir(OUTPUT_DIR)

    print("Done!")

if __name__ == "__main__":
    main()