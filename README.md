# Introduction

The search tool is designed to help a user with narrowing down a set of 100+ theses to just a few theses that the user deems useful for their work.
The tool has two main functions: clustering and text summarisation.

For the clustering side, the user inputs how many groups they'd like, for example, 10 groups. The 100+ theses are then grouped into 10 groups, based on their contents. The machine learning algorithm analyses the contents of each thesis and determines which theses contain similar concepts - putting them in the same group.
The user can then browse the groups, looking for which group holds the set of theses they are most interested in.

The search tool also performs text summarisation. The summarisation algorithm searches through each thesis, looking for which phrases appear to be the most important, and that describe the overall concept of the thesis most closely. These phrases are extracted and stitched together to form a few sentences that are quickly readable.
These quick summarisations are smaller than an abstract but contain more information than the thesis title. In the search tool's user interface, the summarisations are displayed next to each thesis, allowing the user to skim over the summaries to help them decide which theses may be useful to their work.

This project is an in-development prototype for this search tool.

# Setup

## Required python modules

spacy (<https://spacy.io/usage>)  
numpy (<https://numpy.org/install/>)  
sklearn (<https://scikit-learn.org/stable/install.html>)  
flask (<https://pypi.org/project/Flask/>)  
tika (<https://pypi.org/project/tika/>)  
jsonpickle (<https://pypi.org/project/jsonpickle/>)  
pdf2image (<https://pypi.org/project/pdf2image/>)  
PIL (<https://pypi.org/project/Pillow/>)  

Downloading the pre-trained NLP model:  
python -m spacy download en_core_web_sm  

### Optional (to get the optional file "webscraper.py" to work)

selenium (<https://pypi.org/project/selenium/>). Make sure to install read the instructions carefully as the process is odd.

## Running

Run using:  
python runserver.py  
Then in your browser, navigate to: <http://localhost:5555/>

## How to use
Once loaded, clicking on any ticket will cause the program to process the PDF files in the [Input Folder](#Input-folder). Once processing is complete, the groups should be displayed in the browser so they can be looked through.

To change the number of k-means clustering groups, submit another ticket by using the searchbar (search any arbitrary string as it has no effect), submit the ticket, then open that ticket. This is intended to be changed in the future when the ticketing system is put back together.

# File Documentation

A short description of what each python file in the project does.

## "ATS_demo.py"

Written by Jinjie Huang, this file has the machine learning functions which can be used to summarise papers and provide the papers with a latent space vector representation.

## "getTag.py"

Written by Jinjie Huang, this file provides functions to group the papers using their latent space representations (with k-means clustering)

## "data_processing.py"

The main messy script file. This holds a large number of auxilliary functions which have been created and used during prototyping.
Since the machine learning processing takes a while, much of the code in this file is dedicated to storing any processed information as it goes along, then loading it up again (for example in
the event of a program crash).

The main entry point for this file is 'process_ticket' which recieves a ticket class (defined in ticket_manager). This promptly calls 'update_database' (I had to roll back some functionality
here, hence the odd function structure). This function is the important one in this file:

- It checks that all required paths exist, then goes through the database (./FlaskWebProject/database) reading all the data into memory.
- It converts all PDFs in the input folder into raw text
- It identifies which papers still need to be summarised (summarisation takes a while) and adds them to a queue.
- It summarises any papers in the database that need summarising still. If any papers have been previously summarised, it just loads the saved .txt with this info in.
- It extracts the abstract and title from each paper using a very naive method. If this step has previously been performed on a particular paper, it just loads the saved .txt with this info in.
- It creates a latent vector representation of every paper in the database, saving these representations in 'WORD_VECTOR_PATH'. It skips papers that already have been processed.

## "ticket_manager.py"

This file handles the ticket system (which had to be rolled back to limited functionality).
The idea being, each user search creates a ticket which is added to a ticket queue. Each ticket is processed in the background (since the machine learning takes a while).

Sadly at the moment only 1 ticket works at once - each ticket just looks in the database for the list of theses to process (instead of each ticket holding an independent list of theses to process).
When a ticket is created, it used to use "webscraping.py" to webscrape EThOS theses off the EThOS site, adding them into their own folder for processing. The processing would then be done in the background. The user can click on a ticket to see the result after processing.

## "views.py"

This file simply interfaces with the website client, managing the flask POST and GET requests.
The client will make a POST request using the /search URL, attatching a message_tag to describe what sort of search it wants.
The important request is "group_search" which tells the backend to process a particular ticket.
"views.py" is purely for handling the interface between frontend and backend, so it just calls relevant functions and returns the results to the web.

## "webscraping.py"

This file is currently independant to the rest of the project - I use it to download any number of thesis PDFs off the website and store their titles in a .txt.
Requires Selenium to be installed (slightly odd installation, as you'll need to install the Chrome Web Driver as well as the selenium library. Simply follow the standard selenium installation process online)
Running webscraping.py should work straight away (as it'll do an example scrape) with two search terms: python and physics. It should scrape 3 pages worth of theses.

## Input folder

"/FlaskWebProject/static/PDF_Files_Input" holds the input PDFs that should be processed. As the processing happens, all the intermediate saved data is saved into "./FlaskWebProject/database".
Feel free to change the input PDF files (currently these are just examples)
