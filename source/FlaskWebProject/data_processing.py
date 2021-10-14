
import FlaskWebProject.ATS_demo as esearch
import FlaskWebProject.getTag as groupsystem
from tika import parser
import string
from pdf2image import convert_from_path
import os
from os import path
from PIL import Image
import math
import numpy as np
import collections
from shutil import copyfile

print("Loaded imports...\n")

# Paths:
SUMMARISED_PATH = 'FlaskWebProject/database/summarised/'
RAW_TEXT_PATH = 'FlaskWebProject/database/raw_text/'
PREVIEWS_PATH = 'FlaskWebProject/database/previews/'
DOWNLOADS_PATH = 'FlaskWebProject/database/downloaded/'

PDF_INPUT_PATH = 'FlaskWebProject/static/PDF_Files_Input/'
THUMBS_PATH = 'FlaskWebProject/static/thumbs/'

WORD_VECTOR_PATH = 'FlaskWebProject/database/word_vectors/'
NAMES_ORDER_PATH = 'FlaskWebProject/database/name_orders.txt'

download_folder = os.path.dirname(os.path.abspath(__file__)) + "\\database\\downloaded"

# Globals
paper_queue = []
stop_word = []
stop_word_set = set()
all_paper_names = set()


papers_in_folder = {}

paper_locations = {}


changed_paper_names = {}

summarised_papers = {}
paper_previews = {}


word_vector_names_order = []
word_vector_matrix = []

def check_folders():
    global PDF_INPUT_PATH,SUMMARISED_PATH,RAW_TEXT_PATH,THUMBS_PATH,PREVIEWS_PATH,WORD_VECTOR_PATH,DOWNLOADS_PATH
    folders = [PDF_INPUT_PATH,SUMMARISED_PATH,RAW_TEXT_PATH,THUMBS_PATH,PREVIEWS_PATH,WORD_VECTOR_PATH,DOWNLOADS_PATH]
    for f in folders:
        if not os.path.exists(f):
            os.makedirs(f)
            print("Created folder path: " + f)


def SummarisePaper(paper_name):
    global stop_word, RAW_TEXT_PATH
    print("Summarising: " + paper_name)

    input = ""

    input = get_abstract(paper_name)

    summarization = ""
    min_characters = 300.0
    abstract_characters = len(input)
    proportion = min_characters / abstract_characters

    ### ML CODE:
    sentence_set,sentence_with_index = esearch.split_sentence(input, punctuation_list="!.?")
    tfidf_matrix = esearch.get_tfidf_matrix(sentence_set,stop_word)
    sentence_with_words_weight = esearch.get_sentence_with_words_weight(tfidf_matrix)
    sentence_with_position_weight = esearch.get_sentence_with_position_weight(sentence_set)
    sentence_score = esearch.get_similarity_weight(tfidf_matrix)
    sort_sent_weight = esearch.ranking_base_on_weigth(sentence_with_words_weight,sentence_with_position_weight,sentence_score, feature_weight = [0.6,0.2,0.2])
    summarization = esearch.get_summarization(sentence_with_index,sort_sent_weight,topK_ratio =proportion)
    ### END OF ML CODE
    
    return summarization.strip()

def clean_files(all_paper_names):
    global SUMMARISED_PATH,RAW_TEXT_PATH,THUMBS_PATH,PREVIEWS_PATH,WORD_VECTOR_PATH
    folders = [SUMMARISED_PATH,RAW_TEXT_PATH,THUMBS_PATH,PREVIEWS_PATH,WORD_VECTOR_PATH]
    for f_path in folders:

        filelist = [ f for f in os.listdir(f_path) if f.endswith(".txt") or  f.endswith(".jpeg")]
        for filei in filelist:
            filename = os.fsdecode(filei)
            filename = os.path.splitext(filename)[0]
            if not filename in all_paper_names:
                print("DELETING: " + filename)

                os.remove(os.path.join(f_path, filei))



def refresh_summarisation_queue():
    global all_paper_names, paper_queue, RAW_TEXT_PATH, SUMMARISED_PATH
    clean_files(all_paper_names)
    
    paper_queue_set = set(all_paper_names)

    for ifile in os.listdir(SUMMARISED_PATH):
        filename = os.fsdecode(ifile)
        if filename.endswith(".txt"):
            filename_no_extension = os.path.splitext(filename)[0]
            if filename_no_extension in all_paper_names:
                paper_queue_set.remove(filename_no_extension)
    
    paper_queue = list(paper_queue_set)

def complete_summarisation_queue():
    global all_paper_names, paper_queue, stop_word, stop_word_set, summarised_papers, SUMMARISED_PATH

    if len(stop_word) < 2:
        stop_word = []
        with open('FlaskWebProject/stopWordList.txt','r') as f:
            for line in f.readlines():
                cword = line.strip()
                stop_word.append(cword)
                stop_word_set.add(cword)

    count = 0
    total = len(paper_queue)
    if len(paper_queue) > 0:

        while len(paper_queue) > 0:
            current_paper_name = paper_queue.pop()
            result = SummarisePaper(current_paper_name)
            count += 1
            print(str(round(count*100/total))+ "% Summarised: " + current_paper_name)

            summarised_papers[current_paper_name] = result
            f = open(SUMMARISED_PATH + current_paper_name + ".txt", "w") #, encoding="utf8"
            f.write(result)
            f.close()
            #print("written file: " + current_paper_name)
    else:
        print("Files up to date")


def update_database_memory(percentage_to_cache):
    global all_paper_names, summarised_papers

    number_of_papers = len(all_paper_names)
    number_to_cache = math.floor(number_of_papers * percentage_to_cache)

    count_f = 0
    for current_paper_name in all_paper_names:
        get_summarised_text(current_paper_name)
        count_f += 1
        if count_f > number_to_cache:
            break

    if count_f > 0:
        print("Read " + str(count_f) + " summarised files to memory.")
    else:
        print("No summarised files read from memory.")


def count_pdfs():
    global PDF_INPUT_PATH
    count=0
    for ifile in os.listdir(PDF_INPUT_PATH):
        filename = os.fsdecode(ifile)
        if filename.lower().endswith(".pdf"):
            count += 1
    return count

def load_data_into_memory():
    check_folders()
    load_names()



def update_database(rebuild_summarisations):
    # OLD PROCESS
    global processes_total, processes_complete, current_process_status,word_vector_names_order, word_vector_matrix, all_paper_names
    print("\n###\n- Performing backend pre-processing:\n")

    processes_total = count_pdfs() * 2
    processes_complete = 0

    # Check relevant folders exist. If not, create them.
    check_folders()
    # Convert pdf's in pdf_input into raw text where required.
    update_raw_text()

    # work out which papers need to be summarised, load paper names into memory
    refresh_summarisation_queue()

    update_previews()
    print("Previews finished.")

    if rebuild_summarisations:

        # ASYNC - summarise all papers that need to be summarised
        complete_summarisation_queue()
        # Load the summarised files into python memory
        update_database_memory(1)
    # Extract previews from raw text (headers, body etc)

    # Ensure word vectors matrix is up to date, and the name order list.
    check_word_vector_paper_names()
    print("\n\n- Backend pre-processing complete.\n###\n")

    processes_complete = 1
    processes_total = 1
    current_process_status = "Idle"


def process_ticket(ticket):
    """Takes a ticket_manager ticket object and performs ALL PROCESSING on it, start to finish.
    """
    global processes_total, processes_complete, current_process_status,word_vector_names_order, word_vector_matrix, all_paper_names
    print("\n###\n- Performing backend pre-processing:\n")
    # Check relevant folders exist. If not, create them.
    check_folders()

    # Convert pdf's in pdf_input into raw text where required.
    #update_raw_text()

    update_database(True)






# Set of allowed characters for the ML code
printable = set(string.printable)
printable.remove('!')

def cleanup_text(text):
    global printable

    #current_line = ''.join(filter(lambda x: x in printable, text)).strip()

    new_text = ""
    text = text.splitlines()
    for current_line in text:
        if len(current_line.strip()) < 5:
            continue
        if "...." in current_line:
            continue

        current_line = ''.join(filter(lambda x: x in printable, current_line))
        new_text += current_line + "\n"
    

    return new_text

def read_and_store_pdf(paper_name):
    """Reads a single PDF and converts it to raw text"""
    global PDF_INPUT_PATH, RAW_TEXT_PATH, changed_paper_names, paper_locations

    out_str = ""

    pdf_path = paper_locations[paper_name]#PDF_INPUT_PATH + paper_name + '.pdf'

    #if paper_name in changed_paper_names:
    #    pdf_path = PDF_INPUT_PATH + changed_paper_names[paper_name] + '.pdf'


    raw = parser.from_file(pdf_path)
    out_str = raw['content']

    if out_str == None:
        print("WARNING!: paper '" + paper_name + "' failed to be converted to text!")
        return None

    

    out_str = cleanup_text(out_str)
    
    if len(out_str) < 5:
        print("WARNING!: paper '" + paper_name + "' failed to be converted to text!")
    else:

        f = open(RAW_TEXT_PATH + paper_name + ".txt", "w")  #, encoding="utf8"
        f.write(out_str)
        f.close()

        
def load_names():
    """
    Activated upon program load
    """
    global RAW_TEXT_PATH, PDF_INPUT_PATH, processes_complete, current_process_status, changed_paper_names, all_paper_names, paper_locations, papers_in_folder
    all_paper_names = set()
    count = 0
    files_to_search = []
    current_folders = []
    for ifile in os.listdir(PDF_INPUT_PATH):
        f_path = PDF_INPUT_PATH + ifile
        f_path = os.fsdecode(f_path)
        files_to_search.append(f_path)
        current_folders.append("")
    list_subfolders_with_paths = [f.name for f in os.scandir(PDF_INPUT_PATH) if f.is_dir()]
    for subfolder in list_subfolders_with_paths:
        for ifile in os.listdir(PDF_INPUT_PATH + subfolder):
            f_path = PDF_INPUT_PATH + subfolder + "/" + ifile
            f_path = os.fsdecode(f_path)
            files_to_search.append(f_path)
            current_folders.append(subfolder)
    total = len(files_to_search)
    for i, ifile in enumerate(files_to_search):
        filename = os.path.basename(ifile)
        if filename.lower().endswith(".pdf"):
            filename_no_extension = os.path.splitext(filename)[0]
            if "," in filename_no_extension or "%" in filename_no_extension or "'" in filename_no_extension or "." in filename_no_extension:
                new_name = filename_no_extension.replace(",","")
                new_name = new_name.replace("%","")
                new_name = new_name.replace("'","")
                new_name = new_name.replace(".","")
                print(" CHANGING file name:")
                print(ifile)
                print(PDF_INPUT_PATH + new_name + ".pdf")
                os.rename(ifile, PDF_INPUT_PATH + new_name + ".pdf")
                filename_no_extension = new_name
    
            all_paper_names.add(filename_no_extension)

            current_folder = current_folders[i]
            if current_folder in papers_in_folder:
                papers_in_folder[current_folder].add(filename_no_extension)
            else:
                papers_in_folder[current_folder] = set()
                papers_in_folder[current_folder].add(filename_no_extension)

            paper_locations[filename_no_extension] = ifile
            raw_text_version_path = RAW_TEXT_PATH + filename_no_extension + '.txt'

            count += 1
            if not path.exists(raw_text_version_path):
                read_and_store_pdf(filename_no_extension)
                print(str(round(count*100/total)) + "% PDF '" + filename_no_extension + "' read successfully")

            processes_complete += 1
            current_process_status = "Creating text from: " + filename_no_extension


    total = len(files_to_search)



def update_raw_text():
    """Reads all PDFS and converts them to raw text"""
    global RAW_TEXT_PATH, PDF_INPUT_PATH, processes_complete, current_process_status, changed_paper_names, all_paper_names, paper_locations, papers_in_folder

    # OLD:
    all_paper_names = set()
    count = 0
    

    files_to_search = []
    current_folders = []

    for ifile in os.listdir(PDF_INPUT_PATH):
        f_path = PDF_INPUT_PATH + ifile
        f_path = os.fsdecode(f_path)
        files_to_search.append(f_path)
        current_folders.append("")
    



    list_subfolders_with_paths = [f.name for f in os.scandir(PDF_INPUT_PATH) if f.is_dir()]
    for subfolder in list_subfolders_with_paths:
        for ifile in os.listdir(PDF_INPUT_PATH + subfolder):
            f_path = PDF_INPUT_PATH + subfolder + "/" + ifile
            f_path = os.fsdecode(f_path)
            files_to_search.append(f_path)
            current_folders.append(subfolder)
            
    # END OLD
    
    total = len(files_to_search)


    for i, ifile in enumerate(files_to_search):
        filename = os.path.basename(ifile)
        if filename.lower().endswith(".pdf"):
            


            filename_no_extension = os.path.splitext(filename)[0]

            if "," in filename_no_extension or "%" in filename_no_extension or "'" in filename_no_extension or "." in filename_no_extension:
                original = filename_no_extension
                filename_no_extension = filename_no_extension.replace(",","")
                filename_no_extension = filename_no_extension.replace("%","")
                filename_no_extension = filename_no_extension.replace("'","")
                filename_no_extension = filename_no_extension.replace(".","")
                #print("changed PDF from:" + original + " to: " + f)
                changed_paper_names[filename_no_extension] = original
            
            all_paper_names.add(filename_no_extension)

            current_folder = current_folders[i]
            if current_folder in papers_in_folder:
                papers_in_folder[current_folder].add(filename_no_extension)
            else:
                papers_in_folder[current_folder] = set()
                papers_in_folder[current_folder].add(filename_no_extension)

            paper_locations[filename_no_extension] = ifile
            raw_text_version_path = RAW_TEXT_PATH + filename_no_extension + '.txt'

            count += 1
            if not path.exists(raw_text_version_path):
                read_and_store_pdf(filename_no_extension)

                print(str(round(count*100/total)) + "% PDF '" + filename_no_extension + "' read successfully")
            processes_complete += 1
            current_process_status = "Creating text from: " + filename_no_extension


#def update_raw_text_for_ticket(ticket_obj):
#    global RAW_TEXT_PATH, PDF_INPUT_PATH, changed_paper_names

#    all_paper_names = set()

#    count = 0
#    total = len(os.listdir(PDF_INPUT_PATH))

#    for ifile in os.listdir(PDF_INPUT_PATH):
#        filename = os.fsdecode(ifile)
#        if filename.lower().endswith(".pdf"):
            


#            filename_no_extension = os.path.splitext(filename)[0]

#            if "," in filename_no_extension or "%" in filename_no_extension or "'" in filename_no_extension or "." in filename_no_extension:
#                original = filename_no_extension
#                filename_no_extension = filename_no_extension.replace(",","")
#                filename_no_extension = filename_no_extension.replace("%","")
#                filename_no_extension = filename_no_extension.replace("'","")
#                filename_no_extension = filename_no_extension.replace(".","")
#                #print("changed PDF from:" + original + " to: " + f)
#                changed_paper_names[filename_no_extension] = original
            
#            all_paper_names.add(filename_no_extension)

#            raw_text_version_path = RAW_TEXT_PATH + filename_no_extension + '.txt'

#            count += 1
#            if not path.exists(raw_text_version_path):
#                read_and_store_pdf(filename_no_extension)

#                print(str(round(count*100/total)) + "% PDF '" + filename_no_extension + "' read successfully")
#            processes_complete += 1
#            current_process_status = "Creating text from: " + filename_no_extension

def LineIsTitle(line):
    line = line.strip()
    if line.isupper():
        return True
    if len(line) > 3:
        if (line[0].isupper() and len(line) < 25) or line[0].isdigit():
            if len(line.split(" ")) < 10:
                if line.endswith('.'):
                    return False
                return True
    return False

def findTitle(paper_name):
    global download_folder
    
    #download_folder = os.path.dirname(os.path.abspath(__file__)) + "\\database\\downloaded"
    #if not path.exists(raw_text_version_path):
    test_path = download_folder + "\\" + paper_name +".txt"
    if path.exists(test_path):
        f = open(test_path, "r")
        out = f.read()
        f.close()
        return out + "\n"

    return None
    
def write_paper_preview(paper_name, start_line = 0):
    global paper_previews, PREVIEWS_PATH, RAW_TEXT_PATH

    f = open(RAW_TEXT_PATH + paper_name + ".txt", "r")
    
    out_str = ""
    print("Extracting abstract from: " + paper_name)

    line_read_total = 0



    # Find title
    while True:
        try:
            current_line_text = f.readline()
            if current_line_text == "":
                break
            out_str = current_line_text
            if len(current_line_text.strip()) > 15:
                break
        except:
            break
    
    new_title = findTitle(paper_name)
    if new_title != None:
        out_str = new_title

    if start_line > 0:
        for i in range(0, start_line):
            current_line_text = f.readline()
            line_read_total += 1
    # Find start of abstract
    while True:
        try:
            current_line_text = f.readline()
            if current_line_text == "":
                break
            line_read_total += 1
            line = current_line_text.strip()
            if (len(line) < 28 and len(line) > 3) or (len(line) > 3 and line[0].isdigit() and len(line) < 32):

                linelower = line.lower()
                if linelower.strip() == "abstract":
                    break
                if line[0].isupper() or line[0].isdigit():
                    if "intro" in linelower:
                        break
                    if "synopsis" in linelower:
                        break
                    if "abstract" in linelower:
                        break
                    if "summary" in linelower:
                        break

        except:
            break

    
    line_count = 0
    consecutive_titles = 0
    last_line_was_title = True
    while True:
        try:
            current_line_text = f.readline()
            if current_line_text == "":
                break
            line_read_total += 1

            line = current_line_text.strip()

            if LineIsTitle(line):
                if last_line_was_title and consecutive_titles < 5:
                    consecutive_titles += 1
                    last_line_was_title = True
                    continue
                else:
                    #Failed abstract
                    if line_count < 4:
                        print("Failed to find abstract")
                        out_str = ""
                        f.close()
                        write_paper_preview(paper_name, start_line = line_read_total)
                        return None
                    break
            
            out_str += current_line_text.strip() + "\n"
            line_count += 1
            last_line_was_title = False
            if line_count > 100:
                break
        except:
            break
    
    f.close()

    f = open(PREVIEWS_PATH + paper_name + ".txt", "w")
    f.write(out_str)
    f.close()
    paper_previews[paper_name] = out_str
    print("Extracted abstract for: " + paper_name)








def update_previews():
    global all_paper_names, processes_complete, current_process_status
    current_process_status = "Starting preview process"
    for f in all_paper_names:
        get_paper_preview(f)
        processes_complete += 1

        current_process_status = "Creating preview for: " + f
    current_process_status = "Process complete"


def create_word_vectors():
    global RAW_TEXT_PATH, WORD_VECTOR_PATH, NAMES_ORDER_PATH, all_paper_names, word_vector_names_order, word_vector_matrix
    

    matrix, names_order = groupsystem.create_word_matrix(all_paper_names, RAW_TEXT_PATH, WORD_VECTOR_PATH)

    with open(NAMES_ORDER_PATH, 'w') as f:
        for name in names_order:
            f.write("%s\n" % name)
    word_vector_names_order = names_order
    word_vector_matrix = matrix
        

def get_word_vector(paper_name , percent_complete):
    global RAW_TEXT_PATH, WORD_VECTOR_PATH

    vec_path = WORD_VECTOR_PATH + paper_name + ".txt"
    
    if path.exists(vec_path):
        
        return np.loadtxt(vec_path, delimiter=',')
    else:
        print(" - Creating word vector for: " + paper_name)
        vect = groupsystem.create_word_vector(RAW_TEXT_PATH, paper_name)
        print(percent_complete + "% Got word vector for: " + paper_name)
        np.savetxt(vec_path, vect, delimiter=',')
        return vect


def load_existing_word_vectors():
    global word_vector_names_order, word_vector_matrix, WORD_VECTOR_PATH, all_paper_names

    word_vector_matrix = []
    word_vector_names_order = []
    names_order_set = set()

    reset_required = False


    count = 0
    total = 1

    with open(NAMES_ORDER_PATH, 'w') as f:
        f.write("")

    if path.exists(NAMES_ORDER_PATH):
        with open(NAMES_ORDER_PATH, 'r') as f:
            texti = f.read().splitlines()
            for cname in texti:
                word_vector_names_order.append(cname)
                names_order_set.add(cname)
                count += 1
                
                word_vector_matrix.append(get_word_vector(cname, str(round(count*100 / total))))
                if not cname in all_paper_names:
                    reset_required = True
                    break
    
    if reset_required:
        word_vector_matrix = []
        word_vector_names_order = []
        names_order_set = set()

    
    
    total = len(all_paper_names)

    for cname in all_paper_names:
        if cname not in names_order_set:
            word_vector_names_order.append(cname)
            names_order_set.add(cname)

            
            count += 1
            word_vector_matrix.append(get_word_vector(cname, str(round(count*100 / total))))

            
            
            


    word_vector_matrix = np.array(word_vector_matrix)

    update_order_list()
            

def update_order_list():
    global NAMES_ORDER_PATH, word_vector_names_order

    with open(NAMES_ORDER_PATH, 'w') as f:
        for name in word_vector_names_order:
            f.write("%s\n" % name)

def check_word_vector_paper_names():
    global word_vector_names_order, word_vector_matrix, WORD_VECTOR_PATH, NAMES_ORDER_PATH, all_paper_names
    
    names_order_set = set()

    load_existing_word_vectors()
    print("Loaded word matrix")

    if path.exists(NAMES_ORDER_PATH) and True == False:

        load_existing_word_vectors()


        word_vector_names_order = []
        with open(NAMES_ORDER_PATH, 'r') as f:
            texti = f.read().splitlines()
            for cname in texti:
                word_vector_names_order.append(cname)
                names_order_set.add(cname)

        for cname in all_paper_names:
            if cname not in names_order_set:
                create_word_vectors()
                return None
        
        word_vector_matrix = np.loadtxt(WORD_VECTOR_PATH, delimiter=',')
        print("Loaded word matrix.")
    #else:
        #create_word_vectors()


def write_groups_to_folders(papers_in_each_group):
    global PDF_INPUT_PATH, changed_paper_names
    for paper_group in range(0, len(papers_in_each_group)):
        group_directory = 'FlaskWebProject/static/groups/Group ' + str(paper_group + 1) + '/'
        if not os.path.exists(group_directory):
            os.makedirs(group_directory)
        print("Group location: " + group_directory)
        for paper_name in papers_in_each_group[paper_group]:
            file_name = paper_name + '.pdf'
            if paper_name in changed_paper_names:
                file_name = changed_paper_names[paper_name] + '.pdf'
            
            original_path = PDF_INPUT_PATH + file_name
            target_path = group_directory + file_name
            copyfile(original_path, target_path)







######## ACCESSORS:


def get_summarised_text(paper_name):
    global summarised_papers, SUMMARISED_PATH
    if paper_name in summarised_papers:
        return summarised_papers[paper_name]
    else:
        try:
            f = open(SUMMARISED_PATH + paper_name + ".txt", "r") #, encoding="utf8"
            summarised_papers[paper_name] = f.read()
            f.close()
        except FileNotFoundError:
            refresh_summarisation_queue()
            complete_summarisation_queue()
            try:
                f = open(SUMMARISED_PATH + paper_name + ".txt", "r") #, encoding="utf8"
                summarised_papers[paper_name] = f.read()
                f.close()
            except:
                return None
        return summarised_papers[paper_name]



def get_thumbnail_url(paper_name):
    global THUMBS_PATH, PDF_INPUT_PATH, paper_locations
    thumb_path = THUMBS_PATH + paper_name + '.jpeg'
    if path.exists(thumb_path):
        return thumb_path
    else:
        try:
            images = convert_from_path(paper_locations[paper_name], first_page=1,last_page=1,size=200)
            images[0].save(thumb_path, "JPEG")
            print("Created thumbnail for: " + paper_name)
            return thumb_path
        except:
            image = Image.new('RGB', (142,201))
            image.save(thumb_path, "JPEG")
            print("WARNING: Thumbnail FAILED for: " + paper_name)
            return thumb_path


def get_paper_pdf_url(paper_name):
    global PDF_INPUT_PATH, changed_paper_names, paper_locations
    #if paper_name in changed_paper_names:
    #    return PDF_INPUT_PATH + changed_paper_names[paper_name] + '.pdf'
    return paper_locations[paper_name] #PDF_INPUT_PATH + paper_name + '.pdf'

def get_paper_preview(paper_name):
    global PREVIEWS_PATH, paper_previews
    if paper_name in paper_previews:
        return paper_previews[paper_name]
    else:
        if not os.path.exists(PREVIEWS_PATH + paper_name + ".txt"):
            write_paper_preview(paper_name)
        else:
            f = open(PREVIEWS_PATH + paper_name + ".txt", "r") #, encoding="utf8"
            paper_previews[paper_name] = f.read()
            f.close()

        return paper_previews[paper_name]

def get_abstract(paper_name):
    full_text = get_paper_preview(paper_name)
    return "\n".join(full_text.split("\n")[1:])

def get_raw_text(paper_name):
    global RAW_TEXT_PATH
    text = ""

    with open(RAW_TEXT_PATH + paper_name + ".txt",'r') as f:
        text = f.read()
    return text

def get_title(paper_name):
    global paper_previews
    preview_text = paper_previews[paper_name]
    return preview_text.split("\n")[0]

def get_all_paper_names():
    global all_paper_names
    return all_paper_names




processes_complete = 0
processes_total = 1
current_process_status = "idle"

#def rebuild_generated_data():
#    global process_completion, current_process_status
#    process_completion = 0
#    current_process_status = "Started.."
#    for i in range(0,10):
#        time.sleep(1)
#        current_process_status = "completed second: " + str(i)
#        process_completion = i/10
#        print(current_process_status)


#    process_completion = 1
#    current_process_status = "Finished rebuilding."

def get_stop_word():
    global stop_word
    return stop_word

def get_process_update():
    global processes_complete, processes_total, current_process_status
    return processes_complete /processes_total, current_process_status

def delete_generated_data():
    global THUMBS_PATH, PREVIEWS_PATH, RAW_TEXT_PATH, paper_previews, all_paper_names
    paths_to_clear = [THUMBS_PATH, PREVIEWS_PATH, RAW_TEXT_PATH]
    for f_path in paths_to_clear:
        filelist = [ f for f in os.listdir(f_path) if f.endswith(".txt") or  f.endswith(".jpeg")]
        for f in filelist:
            os.remove(os.path.join(f_path, f))
    all_paper_names = set()
    paper_previews = {}
    check_folders()

def get_paper_names_in_folder(folder_name):
    global papers_in_folder
    return papers_in_folder[folder_name]

def get_group_tag(papers_in_group):
    global stop_word_set
    
    stop_word_set.add("a")

    wordcount = {}
    
    count = 0
    total = len(papers_in_group)

    for paper_name in papers_in_group:
        all_text = ""
        all_text += get_raw_text(paper_name)
        count += 1

        for word in all_text.lower().split():
            word = word.replace(".","")
            word = word.replace(",","")
            word = word.replace(":","")
            word = word.replace("\"","")
            word = word.replace("!","")
            word = word.replace("â€œ","")
            word = word.replace("â€˜","")
            word = word.replace("*","")
            if len(word) < 3:
                continue
            if word.isdigit():
                continue
            if word not in stop_word_set:
                if word not in wordcount:
                    wordcount[word] = 1
                else:
                    wordcount[word] += 1
    
        print(str(round(count*100 / total)) + "%")
        
        del all_text
        

    word_counter = collections.Counter(wordcount)
    

    TAG_NUMBER = 10

    out_tag = ""
    for word, count in word_counter.most_common(TAG_NUMBER):
        #out_tag += word + " (" + str(word_counter[word]) + "), "
        out_tag += word + ", "

    return out_tag[:-2].capitalize()


def process_groups(ticket):
    """Takes a ticket, and performs k-means on the papers within it. Returns 3 arrays describing the papers in each group"""
    ticket.group_tags = {}
    ticket.papers_in_each_group = {}
    ticket.thumbnail_urls = {}

    if len(ticket.papers_and_ids) == 0 and len(ticket.paper_names) > 0:
        for paper_name in ticket.paper_names:
            ticket.papers_and_ids[paper_name] = paper_name

    papers_to_cluster = ticket.papers_and_ids
    amount_of_groups = ticket.number_of_groups

    if amount_of_groups > len(ticket.papers_and_ids):
        amount_of_groups = len(ticket.papers_and_ids)

    current_ordering = []
    current_matrix = []
    for i, name in enumerate(word_vector_names_order):
        if name in ticket.papers_and_ids:
            current_ordering.append(name)
            current_matrix.append(word_vector_matrix[i])


    clustered_groups = groupsystem.k_means_clustering(current_matrix, current_ordering, amount_of_groups)
    #clustered_groups = groupsystem.k_means_clustering(word_vector_matrix, word_vector_names_order, amount_of_groups)



    for current_group_id in range(amount_of_groups):
        print("Starting group: " + str(current_group_id))
        ticket.group_tags[current_group_id] = "No tag"
        ticket.thumbnail_urls[current_group_id] = "No URL"
        ticket.papers_in_each_group[current_group_id] = []

        for paper_name in clustered_groups[current_group_id]:

            ticket.papers_in_each_group[current_group_id].append(paper_name)
            
            ticket.thumbnail_urls[current_group_id] = get_thumbnail_url(paper_name)
        
        ticket.group_tags[current_group_id] = get_group_tag(ticket.papers_in_each_group[current_group_id])
        print("Finished group: " + str(current_group_id))
    


def get_all_group_data(ticket):
    """Takes a ticket, and if it's not already been done, performs k-means on the papers within it. Returns 3 arrays describing the papers in each group"""
    
    print(len(ticket.papers_in_each_group))

    # TEMP, REMOVE THIS!!!!
    ticket.papers_in_each_group = {}


    # If not already clustered:
    if len(ticket.papers_in_each_group) <= 0:
        process_groups(ticket)
    ticket.status = "fully processed"
    ticket.progress = 100
    ticket.completed = True
    return ticket.group_tags, ticket.papers_in_each_group, ticket.thumbnail_urls





#def get_cluster_from_paper_set(paper_set, amount_of_groups):
#    global word_vector_names_order, word_vector_matrix

#    groups = groupsystem.k_means_clustering(word_vector_matrix, word_vector_names_order, amount_of_groups)

#    group_tags = {}
#    papers_in_each_group = {}
#    thumbnail_urls = {}


#    return groups