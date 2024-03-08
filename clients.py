from xmlrpc.client import ServerProxy
import xmlrpc.client
import datetime

def print_menu():
    print("\nWelcome to the Notebook Application")
    print("1. Add a Note")
    print("2. Retrieve Notes by Topic")
    print("3. Search Wikipedia and Append Information to a Note")
    print("4. Exit")

def main():
    server = ServerProxy('http://localhost:8000')

    while True:
        print_menu()
        choice = input("Please select an operation: ")

        try:
            if choice == '1':
                topic = input("Enter topic: ")
                note_name = input("Enter note name: ")
                text = input("Enter text content: ")
                timestamp = datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
                print(server.add_note(topic, note_name, text, timestamp))

            elif choice == '2':
                topic = input("Enter the topic for which you want to retrieve notes: ")
                notes = server.get_notes(topic)
                if notes:
                    for note in notes:
                        print(f"Note name: {note[0]}, text content: {note[1]}, Timestamp: {note[2]}")
                else:
                    print("No notes found for this topic.")

            elif choice == '3':
                topic = input("Enter the topic to which you want to append Wikipedia summary: ")
                note_name = input("Enter note name: ")
                search_term = input("Enter Wikipedia search term: ")
                result = server.add_note_with_wiki_summary(topic, note_name, search_term)
                print(result)

            elif choice == '4':
                print("Thank you for using the application. Goodbye!")
                break

            else:
                print("Invalid input, please select again.")

        except xmlrpc.client.Fault as fault:
            print(f"XML-RPC fault occurred: {fault.faultString}")
        except Exception as e:
            print(f"Unable to connect to the server, please check that the server is running")

if __name__ == "__main__":
    main()