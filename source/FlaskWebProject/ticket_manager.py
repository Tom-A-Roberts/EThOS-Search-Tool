import FlaskWebProject.data_processing as backend
import os
import jsonpickle

tickets = {}
biggest_ticket_id = -1
TICKETS_PATH = 'FlaskWebProject/database/tickets/'

def check_folder():
    global TICKETS_PATH
    if not os.path.exists(TICKETS_PATH):
        os.makedirs(TICKETS_PATH)
        print("Created folder path: " + TICKETS_PATH)

check_folder()


class Ticket:
    """A specific search by some user"""

    def __init__(self, _ID, _search):
        self.ID = _ID
        self.search = _search
        self.papers_and_ids = {}
        self.completed = False;
        self.group_tags = {}
        self.papers_in_each_group = {}
        self.thumbnail_urls = {}
        self.priority = 1
        self.number_of_groups = 10;
        self.cluster_size = 300;
        self.status = "Waiting to begin"
        self.progress = 0

    def check_if_complete(self):
        global summarised_papers
        if len(self.paper_names) == 0:
            return False
        for paper_name in self.paper_names:
            if not paper_name in summarised_papers:
                return False
        return True

    def add_papers(self, paper_enumerable, e):
        for p in paper_enumerable:
            self.paper_names.add(p)


def write_tickets_to_file():
    """
    Updates all tickets in the files where necessary
    """
    global tickets, TICKETS_PATH
    for i, ticket_key in enumerate(tickets):
        write_certain_ticket_to_file(ticket_key)
        #current_ticket = tickets[ticket_key]
        #ticket_id = current_ticket.ID
        #priority = current_ticket.priority
        ##ticket_name = tickets[ticket_key].search
        ##progress = 0
        ##status = "Waiting to begin"
        ##priority = 1
        ##queue_pos = i
        ##contents = ""
        #f_path = TICKETS_PATH + str(priority) + "_"+ str(ticket_id) + ".txt"
        #f = open(f_path, "w")
        #encoded_var = jsonpickle.encode(current_ticket, unpicklable=True)
        #f.write(encoded_var)
        #f.close()

def write_certain_ticket_to_file(ticket_id):
    global TICKETS_PATH, tickets
    current_ticket = tickets[ticket_id]
    ticket_id = current_ticket.ID
    priority = current_ticket.priority
    #ticket_name = tickets[ticket_key].search
    #progress = 0
    #status = "Waiting to begin"
    #priority = 1
    #queue_pos = i
    #contents = ""
    f_path = TICKETS_PATH + str(priority) + "_"+ str(ticket_id) + ".txt"
    f = open(f_path, "w")
    encoded_var = jsonpickle.encode(current_ticket, unpicklable=True)
    f.write(encoded_var)
    f.close()


def load_tickets_from_file():
    global tickets, TICKETS_PATH, biggest_ticket_id
    biggest_ticket_id = 0
    tickets = {}
    for ifile in os.listdir(TICKETS_PATH):
        filename = os.fsdecode(ifile)
        if filename.lower().endswith(".txt"):
            f = open(TICKETS_PATH + ifile, "r")
            latest_obj = jsonpickle.decode(f.read())

            tickets[latest_obj.ID] = latest_obj
            if latest_obj.ID > biggest_ticket_id:
                biggest_ticket_id = latest_obj.ID
            print(latest_obj)
            print(type(latest_obj))
            f.close()


# Not currently referenced:
def process_ticket(ticket):
    """
    NOT COMPLETE!
    Takes a ticket object and performs ALL PROCESSING on it, start to finish.
    This should be performed in the background to the other processing.
    """
    # Do some web-scraping
    #downloaded_ids = webscraper.scrape("python", 1, backend.download_folder)

    print(ticket.search)
    #downloaded_ids = webscraper.scrape(ticket.search, 2, backend.download_folder)
    
    ticket.papers_and_ids = {}

    found_ids = []
    found_names = []
    for filename in os.listdir(backend.download_folder):
        if filename.endswith(".pdf"):
            ethos_id = filename.split(".")[-2]
            f= open(backend.download_folder + "\\" + ethos_id + ".txt","r", encoding="utf-8")
            name = f.read()
            f.close()
            found_ids.append(ethos_id)
            found_names.append(name)
            ticket.papers_and_ids[ethos_id] = name


    move_to_path = backend.PDF_INPUT_PATH
    #for id in found_ids:

    #    shutil.move(backend.download_folder + "\\" + id + ".pdf", "path/to/new/destination/for/file.foo")


    #print(downloaded_ids)
    #tickets[ticket_id].paper_names = backend.get_paper_names_in_folder('')



    backend.process_ticket(ticket)


def create_new_ticket(searched_text, group_size, clustering_dimensions):
    """
    NOT COMPLETE!
    Creates a new ticket, adds it to the ticket array, and writes it to file.
    TEMP: Adds ALL known papers to it
    """
    global tickets, biggest_ticket_id
    ticket_id = biggest_ticket_id + 1
    biggest_ticket_id = ticket_id

    tickets[ticket_id] = Ticket(ticket_id, searched_text)
    tickets[ticket_id].number_of_groups = group_size
    
    # TEMPORARILY just load all the papers from the input folder:
    tickets[ticket_id].paper_names = backend.get_paper_names_in_folder('')

    #if "python" in searched_text.lower():
    #    tickets[ticket_id].paper_names = backend.get_paper_names_in_folder("Python")
    #else:


    print("created ticket:", tickets[ticket_id])
    
    write_tickets_to_file()

def get_papers_in_ticket(ticket_id):
    global tickets
    return tickets[ticket_id].paper_names

def get_ticket(ticket_id):
    """Gets the ticket object from an ID integer"""
    global tickets
    return tickets[ticket_id]

def get_ticket_queue():
    global tickets
    ticket_list = []
    for i, ticket_key in enumerate(tickets):
        ticket_id = tickets[ticket_key].ID
        ticket_name = tickets[ticket_key].search
        progress = tickets[ticket_key].progress
        status = tickets[ticket_key].status
        priority = tickets[ticket_key].priority
        queue_pos = i
        ticket_list.append({"ticket_id": ticket_id, "ticket_name": ticket_name, "progress":progress, "status":status, "priority":priority, "queue_pos":queue_pos})
    print("ticket number: ", len(ticket_list))
    return ticket_list

load_tickets_from_file()

print("Loaded Ticket Manager...\n")


search_input = "14th,15th,century,weaponry,pilgrim,coffin"
search_input = "medieval,post-medieval,artefact,assemblage"
search_input = "medieval,post-medieval,burial ground"
#downloaded_ids = webscraper.scrape(search_input, 3, backend.download_folder)