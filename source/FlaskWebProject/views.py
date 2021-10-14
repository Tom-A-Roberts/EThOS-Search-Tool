"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, jsonify
from FlaskWebProject import app
import FlaskWebProject.data_processing as backend
import FlaskWebProject.ticket_manager as ticketmanager

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/search', methods=['POST', 'GET'])
def search():
    error = None
    if request.method == 'POST':
        message_tag = request.form['message_tag']
        result = ""
        if message_tag == "all_papers_in_ticket":
            result = all_papers_in_ticket(int(request.form['ticket_id']))
        elif message_tag == "papers_request":
            result = papers_request(request.form['papers'], request.form['ticket'])
        elif message_tag == "summarisation_request":
            result = summarisation_request(request.form['paper_name'])
        elif message_tag == "group_search":
            result = begin_process_ticket(int(request.form['ticket']))
            #result = get_groups(int(request.form['group_size']),int(request.form['clustering_dimensions']), int(request.form['ticket']))
            #result = get_groups(request.form['search_terms'], int(request.form['group_size']),int(request.form['clustering_dimensions']), int(request.form['ticket']))
        elif message_tag == "new_ticket":
            result = submit_ticket(request.form['search_terms'], int(request.form['group_size']),int(request.form['clustering_dimensions']))
        elif message_tag == "queue_request":
            result = get_ticket_queue_json()
        return result

    return "NO DATA"

@app.route('/devtool', methods=['POST', 'GET'])
def devtool():
    error = None
    if request.method == 'POST':
        message_tag = request.form['message_tag']
        result = ""
        if message_tag == "delete_generated_data":
            result = devtool_delete_generated_data()
        if message_tag == "rebuild_generated_data":
            result = devtool_rebuild_generated_data()
        if message_tag == "completion_update":
            result = devtool_get_update()

        return result
    return "NO DATA"

def devtool_delete_generated_data():
    backend.delete_generated_data()
    return jsonify({"body": "Data deleted.", "percent_complete": 1})

def devtool_rebuild_generated_data():
    backend.update_database(False)
    return jsonify({"body": "Finished rebuilding.", "percent_complete": 1})

def devtool_get_update():
    process_completion, current_process_status = backend.get_process_update()
    return jsonify({"body": current_process_status, "percent_complete": process_completion})


def summarisation_request(paper_name):
    return jsonify({"summarisation": backend.get_abstract(paper_name), "title":backend.get_title(paper_name)})


def papers_request(papers, ticket_id):
    paper_list = papers.split(',')

    return create_json_from_papers(paper_list, ticket_id)

def all_papers_in_ticket(ticket_id):
    current_ticket = ticketmanager.get_ticket(ticket_id)

    return create_json_from_papers(current_ticket.paper_names, ticket_id)

def submit_ticket(searched_text, group_size, clustering_dimensions):
    """Simply submits the searched text as a new ticket, then returns a JSON description of the queue"""
    global group_amount

    ticketmanager.create_new_ticket(searched_text, group_size, clustering_dimensions)

    #current_ticket = ticketmanager.get_ticket(ticket_id)
    #group_tags, papers_in_each_group, thumbnail_urls = backend.get_all_group_data(group_size, current_ticket)

    # return ticket info:
    return get_ticket_queue_json()

def get_ticket_queue_json():
    return jsonify(ticketmanager.get_ticket_queue())

# Convert to "process all papers":
def begin_process_ticket(ticket_id):
    """TEMP FUNCTION: creates a new ticket with the searched text and parameters,
    Performs k-means on it, then returns the JSON result to the page.
    """
    # Create results set (temporarily this is first 10 papers)
    # Create thumbnails for results set
    # Gather data about each result
    # Format data into JSON

    current_ticket = ticketmanager.get_ticket(ticket_id)

    ticketmanager.process_ticket(current_ticket)

    group_tags, papers_in_each_group, thumbnail_urls = backend.get_all_group_data(current_ticket)

    ticketmanager.write_certain_ticket_to_file(ticket_id)
    return jsonify({"group_tags": group_tags, "papers_in_each_group": papers_in_each_group, "thumbnail_urls":thumbnail_urls, "ticket":ticket_id})
    return None

#def runAISearch(input, ticket_id):

#    # User input parsing:
#    input = input.replace(',', ' ')
#    input_split = input.split(' ')
#    input_split = [x.strip() for x in input_split if len(x) > 1 or (len(x) == 1 and x[0] != ' ')]
#    # Create results set (temporarily this is first 10 papers)
#    # Create thumbnails for results set
#    # Gather data about each result
#    # Format data into JSON
#    backend.create_new_ticket(ticket_id, input)
#    # If ticket is complete
#    papers_in_ticket = ticketmanager.get_papers_in_ticket(ticket)
#    #all_papers = backend.get_all_paper_names()
#    return create_json_from_papers(papers_in_ticket, ticket)

def create_json_from_papers(enumerable_of_papers, ticket_id):
    names_array = []
    previews_array = []
    thumbnail_url_array = []
    pdf_url_array = []


    for paper in enumerable_of_papers:
        pdf_url_array.append(backend.get_paper_pdf_url(paper))
        thumbnail_url_array.append(backend.get_thumbnail_url(paper))
        title = backend.get_title(paper)
        previews_array.append(title + "\n" + backend.get_summarised_text(paper))
        names_array.append(paper)

    return jsonify({
        "paper_names": names_array, 
        "previews": previews_array,
        "thumbnails": thumbnail_url_array,
        "pdf_urls": pdf_url_array,
        "ticket": ticket_id
        })

#backend.update_database(True)
backend.load_data_into_memory()