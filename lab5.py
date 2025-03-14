import argparse
import socket
import hashlib
import os
from urllib.parse import urlparse, quote
from bs4 import BeautifulSoup

CACHE_DIR = "./cache"


def make_http_request(host, path, port=80, follow_redirects=True):
    """Makes a raw HTTP request using sockets and follows redirects"""
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(request.encode())
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
    response = response.decode(errors="ignore")

    # Handle redirects if needed
    if follow_redirects:
        if response.startswith("HTTP/1.1 301") or response.startswith("HTTP/1.1 302"):
            location = None
            for line in response.splitlines():
                if line.lower().startswith("location:"):
                    location = line.split(":", 1)[1].strip()
                    break
            if location:
                print(f"Redirected to: {location}")
                # Recursively follow the redirect
                return follow_redirect(location)

    return response


def follow_redirect(url):
    """Handles the redirection by making a new request"""
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path if parsed_url.path else "/"
    if parsed_url.query:
        path += '?' + parsed_url.query
    return make_http_request(host, path, follow_redirects=False)


def parse_http_response(response):
    """Extracts body content from raw HTTP response"""
    headers, _, body = response.partition("\r\n\r\n")
    return body


def clean_html(html):
    """Removes HTML tags and returns readable text"""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def cache_response(cache_key, data):
    """Caches the response to a file"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    with open(os.path.join(CACHE_DIR, cache_key), "w", encoding="utf-8") as f:
        f.write(data)


def get_cached_response(cache_key):
    """Retrieves cached response if available"""
    cache_file = os.path.join(CACHE_DIR, cache_key)
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()
    return None


def go_to_url(url):
    """Fetches and prints a web page response"""
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path if parsed_url.path else "/"

    cache_key = hashlib.md5(url.encode()).hexdigest()
    cached_data = get_cached_response(cache_key)
    if cached_data:
        print(cached_data)
        return

    response = make_http_request(host, path, port=80)
    body = parse_http_response(response)
    text = clean_html(body)

    cache_response(cache_key, text)
    print(text)

def search_web(query):
    """Searches the web using DuckDuckGo and prints top 10 results"""
    search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
    parsed_url = urlparse(search_url)
    host = parsed_url.netloc
    path = parsed_url.path + "?" + parsed_url.query

    cache_key = hashlib.md5(search_url.encode()).hexdigest()
    cached_data = get_cached_response(cache_key)
    if cached_data:
        print(cached_data)
        return

    response = make_http_request(host, path)
    body = parse_http_response(response)
    soup = BeautifulSoup(body, "html.parser")

    results = []
    for result in soup.select(".result__title a")[:10]:
        title = result.get_text(strip=True)
        link = result["href"]
        results.append(f"{title}\n{link}\n")

    output = "\n".join(results)
    cache_response(cache_key, output)
    print(output)


def show_help():
    """Displays the help message"""
    help_text = """
=== go2web Help ===
Commands:
  1. Fetch a webpage (-u) - Enter a URL to retrieve and display its content
  2. Search the web (-s)  - Enter a search term to find top 10 results
  h. Show this help menu
  q. Exit the program
"""
    print(help_text)


def interactive_menu():
    """Interactive CLI menu for user input"""
    while True:
        print("\n=== go2web CLI ===")
        print("u. Fetch a webpage (-u)")
        print("s. Search the web (-s)")
        print("h. Show help (-h)")
        print("q. Exit")
        choice = input("Enter your choice: ").strip().lower()

        if choice == "u":
            url = input("Enter URL: ").strip()
            if url:
                go_to_url(url)
        elif choice == "s":
            query = input("Enter search term: ").strip()
            if query:
                search_web(query)
        elif choice == "h":
            show_help()
        elif choice == "q":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


parser = argparse.ArgumentParser(description="go2web - a CLI web client")
parser.add_argument("-u", "--url", help="Fetch content from a URL")
parser.add_argument("-s", "--search", help="Search for a term online")

args = parser.parse_args()

if args.url:
    go_to_url(args.url)
elif args.search:
    search_web(args.search)
else:
    interactive_menu()


if __name__ == "__main__":
    main()
