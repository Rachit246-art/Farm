import os
import re
import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.kamalainfra.in"
LANDING_PAGE_URL = "https://www.kamalainfra.in/sustainable-farmhouse"
WORKSPACE_DIR = os.path.abspath(os.path.dirname(__file__))

print(f"Workspace Dir: {WORKSPACE_DIR}")

# Create directories if they do not exist
def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

# Helper to normalize URL and download resource
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

downloaded_urls = {}

def get_real_url_and_local_path(url):
    """
    Given a URL, determines:
    1. The actual remote URL to download from.
    2. The local relative file path where it should be saved.
    """
    # Join with base URL to handle relative URLs
    abs_url = urllib.parse.urljoin(LANDING_PAGE_URL, url)
    parsed = urllib.parse.urlparse(abs_url)
    
    # We only download resources from kamalainfra.in domain
    if parsed.netloc not in ("www.kamalainfra.in", "kamalainfra.in", ""):
        return None, None

    path = parsed.path
    query = urllib.parse.parse_qs(parsed.query)

    # Next.js image optimizer handler
    if path.startswith("/_next/image") and "url" in query:
        # The real image is in the 'url' query parameter
        img_path = query["url"][0]
        # Recursively get real url and local path for this inner path
        return get_real_url_and_local_path(img_path)

    # Normal files
    # Clean the path (remove leading slash)
    local_rel_path = path.lstrip("/")
    if not local_rel_path:
        local_rel_path = "index.html"
    
    # Strip double slashes or other anomalies
    local_rel_path = os.path.normpath(local_rel_path).replace("\\", "/")
    
    # Build absolute download URL
    download_url = urllib.parse.urlunparse((
        parsed.scheme or "https",
        parsed.netloc or "www.kamalainfra.in",
        path,
        "", "", ""
    ))
    
    return download_url, local_rel_path

def download_file(url):
    """
    Downloads the file from URL and returns the local relative path.
    """
    download_url, local_rel_path = get_real_url_and_local_path(url)
    if not download_url:
        return url # Return original URL if external or invalid
    
    if download_url in downloaded_urls:
        return downloaded_urls[download_url]
    
    local_abs_path = os.path.join(WORKSPACE_DIR, local_rel_path)
    ensure_dir(local_abs_path)
    
    # Don't download again if file already exists
    if os.path.exists(local_abs_path):
        downloaded_urls[download_url] = local_rel_path
        return local_rel_path

    print(f"Downloading: {download_url} -> {local_rel_path}")
    try:
        res = session.get(download_url, timeout=15)
        if res.status_code == 200:
            with open(local_abs_path, "wb") as f:
                f.write(res.content)
            downloaded_urls[download_url] = local_rel_path
            
            # If it's a CSS file, parse it for font and image URLs
            if local_rel_path.endswith(".css"):
                process_css_file(local_abs_path, download_url)
                
            return local_rel_path
        else:
            print(f"Failed to download (Status {res.status_code}): {download_url}")
            return url
    except Exception as e:
        print(f"Error downloading {download_url}: {e}")
        return url

def process_css_file(css_abs_path, css_remote_url):
    """
    Scans a downloaded CSS file for url(...) declarations, downloads resources,
    and updates the CSS content with local relative paths.
    """
    print(f"Processing CSS file: {css_abs_path}")
    with open(css_abs_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Match url(...) pattern (handles url('...'), url("..."), url(...))
    url_pattern = re.compile(r'url\((["\']?)([^)]*?)\1\)')
    matches = url_pattern.findall(content)
    
    replacements = {}
    for quote, url in matches:
        # Ignore data URIs or empty URLs
        if url.startswith("data:") or not url.strip():
            continue
        
        # Resolve path relative to CSS remote URL
        abs_asset_url = urllib.parse.urljoin(css_remote_url, url)
        download_url, local_rel_path = get_real_url_and_local_path(abs_asset_url)
        
        if download_url:
            local_path = download_file(abs_asset_url)
            # We need to make the local path relative to the CSS file location
            css_dir = os.path.dirname(css_abs_path)
            asset_abs_path = os.path.join(WORKSPACE_DIR, local_path)
            rel_path_from_css = os.path.relpath(asset_abs_path, css_dir).replace("\\", "/")
            
            original_match = f"url({quote}{url}{quote})"
            new_match = f"url('{rel_path_from_css}')"
            replacements[original_match] = new_match
            
    if replacements:
        for orig, new in replacements.items():
            content = content.replace(orig, new)
        with open(css_abs_path, "w", encoding="utf-8") as f:
            f.write(content)

def main():
    print(f"Fetching main landing page: {LANDING_PAGE_URL}")
    res = session.get(LANDING_PAGE_URL)
    if res.status_code != 200:
        print(f"Failed to fetch landing page: Status {res.status_code}")
        sys.exit(1)
        
    soup = BeautifulSoup(res.text, "html.parser")
    
    # 1. Process CSS Links
    print("Processing Stylesheets...")
    for link in soup.find_all("link", rel="stylesheet"):
        if link.get("href"):
            local_path = download_file(link["href"])
            link["href"] = local_path
            
    # 2. Process JS Scripts
    print("Processing JS Scripts...")
    for script in soup.find_all("script"):
        if script.get("src"):
            local_path = download_file(script["src"])
            script["src"] = local_path
            
    # 3. Process Preload Fonts and Preload Images
    print("Processing Preloads...")
    for link in soup.find_all("link", rel="preload"):
        # Fonts
        if link.get("as") == "font" and link.get("href"):
            local_path = download_file(link["href"])
            link["href"] = local_path
        # Images preloaded
        if link.get("as") == "image":
            if link.get("href"):
                local_path = download_file(link["href"])
                link["href"] = local_path
            if link.get("imageSrcSet"):
                srcset_parts = link["imageSrcSet"].split(",")
                last_part = srcset_parts[-1].strip().split(" ")[0]
                local_path = download_file(last_part)
                link["imageSrcSet"] = f"{local_path} 1x"
                if link.get("imageSizes"):
                    del link["imageSizes"]

    # 4. Process standard Images
    print("Processing Images...")
    for img in soup.find_all("img"):
        # Handle src
        if img.get("src"):
            local_path = download_file(img["src"])
            img["src"] = local_path
        # Handle srcset
        if img.get("srcset"):
            srcset_parts = img["srcset"].split(",")
            last_part = srcset_parts[-1].strip().split(" ")[0]
            local_path = download_file(last_part)
            img["srcset"] = f"{local_path} 1x"
        # Handle custom tags
        if img.get("srcSet"):
            srcset_parts = img["srcSet"].split(",")
            last_part = srcset_parts[-1].strip().split(" ")[0]
            local_path = download_file(last_part)
            img["srcSet"] = f"{local_path} 1x"
            
    # 5. Process shortcut icons, Apple touch icons, etc.
    print("Processing Icons...")
    for link in soup.find_all("link", rel=lambda r: r and any(x in r for x in ["icon", "shortcut", "apple-touch-icon"])):
        if link.get("href"):
            local_path = download_file(link["href"])
            link["href"] = local_path

    # 6. Scan inline styles for url(...) in the HTML
    print("Scanning inline styles for background images...")
    for tag in soup.find_all(style=True):
        style_val = tag["style"]
        url_pattern = re.compile(r'url\((["\']?)([^)]*?)\1\)')
        matches = url_pattern.findall(style_val)
        for quote, url in matches:
            if not url.startswith("data:") and url.strip():
                local_path = download_file(url)
                style_val = style_val.replace(f"url({quote}{url}{quote})", f"url('{local_path}')")
        tag["style"] = style_val

    # Save the modified HTML to index.html
    index_html_path = os.path.join(WORKSPACE_DIR, "index.html")
    print(f"Saving main page to {index_html_path}")
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
        
    print("Cloning completed successfully!")

if __name__ == "__main__":
    main()
