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
        headers, body = response.split(b"\r\n\r\n", 1)

        # Decode response
        body_text = body.decode(errors="ignore")

        # Strip HTML tags for readability
        return clean_html(body_text)
    except Exception as e:
        return f"Error: {e}"


def clean_html(text):
    """Removes HTML tags from text."""
    return re.sub(r"<.*?>", "", text)


def search_duckduckgo(query):
    """Search DuckDuckGo and return the first 10 results."""
    host = "html.duckduckgo.com"
    path = f"/html/?q={query.replace(' ', '+')}"

    response = make_http_request(host, path)

    # Extracting search results (crude parsing)
    results = re.findall(r'(?<=<a rel="nofollow" class="result__url" href=")(.*?)"', response)

    # Formatting output
    if results:
        return "\n".join(results[:10])
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
