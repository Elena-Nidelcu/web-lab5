#!/usr/bin/env python3
import socket
import sys
import re

USER_AGENT = "Mozilla/5.0 (compatible; go2web/1.0)"


def make_http_request(host, path):
    """Manually performs an HTTP GET request using sockets."""
    try:
        # Create a socket and connect
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 80))

        # Form the HTTP request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {USER_AGENT}\r\nConnection: close\r\n\r\n"
        s.sendall(request.encode())

        # Receive the response
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        s.close()

        # Extract headers and body
        parts = response.split(b"\r\n\r\n", 1)
        if len(parts) < 2:
            return "No body content found in response"

        body = parts[1]

        # Decode response
        body_text = body.decode(errors="ignore")

        # Strip HTML tags for readability
        return clean_html(body_text)
    except Exception as e:
        return f"Error: {e}"


def clean_html(text):
    """Removes HTML tags and cleans up the text for better readability with trimmed output."""
    # Remove scripts and style sections completely
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)

    # Replace common HTML entities
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)

    # Remove special Unicode and hex entities (like &#xE5CF;)
    text = re.sub(r'&#x[0-9A-Fa-f]+;', '', text)
    text = re.sub(r'&#[0-9]+;', '', text)

    # Replace block elements with newlines
    text = re.sub(r'<br[^>]*>', '\n', text)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'</div>', '\n', text)
    text = re.sub(r'</h[1-6]>', '\n\n', text)
    text = re.sub(r'</tr>', '\n', text)
    text = re.sub(r'</li>', '\n', text)

    # Add newlines for common block elements
    text = re.sub(r'<(div|p|h[1-6]|tr|td|li|ul|ol)[^>]*>', '\n', text)

    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]*>', '', text)

    # Clean up excessive whitespace
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\t+', ' ', text)  # Tabs to space

    # Process line by line
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        # Skip empty lines and lines with just special characters
        if line and not re.match(r'^[\s\*\=\-\_\+\.\,\;\:]*$', line):
            lines.append(line)

    # Join non-empty lines
    text = '\n'.join(lines)

    # Remove redundant newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove common junk text patterns (customize as needed)
    text = re.sub(r'[0-9]+\s*\>', '', text)  # Remove patterns like "767>"
    text = re.sub(r'minProd\)\s*&&\s*\(\$index', '', text)  # Remove code fragments

    return text.strip()

def search_duckduckgo(query):
    """Search DuckDuckGo and return the first 10 results."""
    host = "html.duckduckgo.com"
    path = f"/html/?q={query.replace(' ', '+')}"

    response = make_http_request(host, path)

    # More robust result extraction
    results = []
    lines = response.split('\n')
    for line in lines:
        if "result__url" in line and "http" in line:
            match = re.search(r'https?://\S+', line)
            if match and len(results) < 10:
                url = match.group(0).strip(',"\'')
                if url not in results:  # Avoid duplicates
                    results.append(url)

    # Formatting output
    if results:
        return "Search results:\n" + "\n".join(f"{i + 1}. {url}" for i, url in enumerate(results))
    else:
        return "No results found."


def main():
    """Command-line argument handling."""
    if len(sys.argv) < 2:
        print("Usage: go2web -u <URL> | -s <search-term> | -h")
        sys.exit(1)

    command = sys.argv[1]

    if command == "-h":
        print("Usage:")
        print("  go2web -u <URL>         # Fetches and prints content from the URL")
        print("  go2web -s <search-term> # Searches the term on DuckDuckGo and shows top 10 results")
        print("  go2web -h               # Displays this help message")

    elif command == "-u" and len(sys.argv) > 2:
        url = sys.argv[2]
        if "://" in url:
            url = url.split("://")[1]  # Remove http/https prefix

        host, path = (url.split("/", 1) + [""])[:2]
        path = "/" + path if path else "/"

        print(make_http_request(host, path))

    elif command == "-s" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        print(search_duckduckgo(query))

    else:
        print("Invalid command. Use -h for help.")


if __name__ == "__main__":
    main()