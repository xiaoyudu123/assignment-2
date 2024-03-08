
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
from xml.etree import ElementTree as ET
import requests
import datetime

# Define a class that inherits from ThreadingMixIn and SimpleXMLRPCServer to support multi-threading
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class NoteServer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.tree = ET.parse(db_path)
        self.root = self.tree.getroot()

    def prettify(self, element, level=0):
        indent = "    "
        if len(element):
            if not element.text or not element.text.strip():
                element.text = f"\n{indent * (level + 1)}"
            if not element.tail or not element.tail.strip():
                element.tail = f"\n{indent * level}"
            for element in element:
                self.prettify(element, level + 1)
            if not element.tail or not element.tail.strip():
                element.tail = f"\n{indent * level}"
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = f"\n{indent * level}"

    def add_note(self, topic, note_name, text, timestamp):
        topic_element = self.root.find(f"./topic[@name='{topic}']")
        if topic_element is None:
            topic_element = ET.SubElement(self.root, 'topic', name=topic)

        note_element = ET.SubElement(topic_element, 'note', name=note_name)
        ET.SubElement(note_element, 'text').text = text
        ET.SubElement(note_element, 'timestamp').text = timestamp
        self.prettify(self.root)
        self.tree.write(self.db_path)
        return f"Note '{note_name}' added to topic '{topic}'"

    def get_notes(self, topic):
        notes = []
        topic_element = self.root.find(f"./topic[@name='{topic}']")
        if topic_element is not None:
            for note in topic_element.findall('note'):
                note_name = note.get('name')
                note_text = note.find('text').text
                timestamp = note.find('timestamp').text
                notes.append((note_name, note_text, timestamp))
        return notes

    def query_wikipedia(self, search_term):
        try:
            # using Wikipedia API
            response = requests.get(f"https://en.wikipedia.org/w/api.php",
                                    params={'action': 'query', 'format': 'json', 'prop': 'extracts',
                                            'exintro': '', 'explaintext': '', 'titles': search_term, 'redirects': 1,
                                            'exsentences': 3})
            if response.status_code == 200:
                pages = response.json().get('query', {}).get('pages', {})
                if not pages:
                    return "No result found"
                for page_id in pages:
                    page = pages[page_id]
                    summary = page.get('extract', 'No summary available.')
                    title = page.get('title', search_term)
                    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                    return title, summary, url
            else:
                return None, "Error querying Wikipedia", None
        except Exception as e:
            return None, f"Exception occurred: {str(e)}", None

    def add_note_with_wiki_summary(self, topic, note_name, search_term):
        title, summary, url = self.query_wikipedia(search_term)
        if title and summary and url:
            note_content = f"Wikipedia Summary for '{title}': {summary} Read more: {url}"
            timestamp = datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S")
            self.add_note(topic, note_name, note_content, timestamp)
            return f"Wikipedia summary for '{title}' appended to the notes. Wikipedia link: {url}"
        else:
            return summary

def main():
    # Using ThreadedXMLRPCServer instead of SimpleXMLRPCServer to create server instances
    server = ThreadedXMLRPCServer(("localhost", 8000), allow_none=True)
    server.register_instance(NoteServer('E:\Sophomore\Python\python assigment\distribute\db.xml'))
    server.register_function(server.instance.add_note, "add_note")
    server.register_function(server.instance.get_notes, "get_notes")
    server.register_function(server.instance.query_wikipedia, "query_wikipedia")

    print("Server is running...")
    server.serve_forever()

if __name__ == "__main__":
    main()