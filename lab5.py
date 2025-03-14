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
        print("1. Fetch a webpage (-u)")
        print("2. Search the web (-s)")
        print("h. Show help")
        print("q. Exit")
        choice = input("Enter your choice: ").strip().lower()

        if choice == "1":
            url = input("Enter URL: ").strip()
            if url:
                go_to_url(url)
        elif choice == "2":
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

interactive_menu()