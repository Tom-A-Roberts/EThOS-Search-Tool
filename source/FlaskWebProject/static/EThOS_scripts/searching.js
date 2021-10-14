
var saved_group_data = {};
var saved_ticket_data = {};
var current_ticket_id = 0;

var form = document.getElementById('search_form');
form.addEventListener('submit', submit_ticket_screen);
var raw_list_button = document.getElementById('raw_list_button');
raw_list_button.addEventListener('click', submit_search);




function papersRequest(paper_list) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            papers_response(xmlHttp);
    }
    xmlHttp.ontimeout = function (e) {
        dev_error("Error contacting server!");
    };
    var FD = new FormData();
    FD.append("message_tag", "papers_request");
    FD.append("ticket", 17);
    FD.append("papers", paper_list.toString());


    xmlHttp.open("POST", "/search", true); // false for synchronous request
    //xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlHttp.send(FD);
}


function summarisationRequest(paper_name) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            summarisation_response(xmlHttp);
    }
    xmlHttp.ontimeout = function (e) {
        dev_error("Error contacting server!");
    };
    var FD = new FormData();
    FD.append("message_tag", "summarisation_request");
    FD.append("paper_name", paper_name);


    xmlHttp.open("POST", "/search", true); // false for synchronous request
    //xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlHttp.send(FD);
}
function summarisation_response(xmlHttp_response) {
    var json_response = JSON.parse(xmlHttp_response.responseText);

    $("#summarisation-title").text( json_response.title);
    $("#summarisation-body").text(json_response.summarisation);


}


function request_all_papers_in_ticket() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            search_response(xmlHttp);
    }
    xmlHttp.ontimeout = function (e) {
        dev_error("Error contacting server!");
    };
    var FD = new FormData();
    FD.append("message_tag", "all_papers_in_ticket");
    FD.append("ticket_id", current_ticket_id);


    xmlHttp.open("POST", "/search", true); // false for synchronous request
    //xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlHttp.send(FD);
}

function send_group_search(ticket) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            group_search_response(xmlHttp);
    }
    xmlHttp.ontimeout = function (e) {
        dev_error("Error contacting server!");
    };
    var FD = new FormData();
    FD.append("message_tag", "group_search");
    FD.append("ticket", ticket);

    xmlHttp.open("POST", "/search", true); // false for synchronous request
    //xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlHttp.send(FD);
}
function send_new_ticket(search_input, number_of_groups, clustering_dimensions) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            ticket_queue_response(xmlHttp);
    }
    xmlHttp.ontimeout = function (e) {
        dev_error("Error contacting server!");
    };
    var FD = new FormData();
    FD.append("message_tag", "new_ticket");
    FD.append("search_terms", search_input);
    FD.append("group_size", number_of_groups);
    FD.append("clustering_dimensions", clustering_dimensions);

    xmlHttp.open("POST", "/search", true); // false for synchronous request
    //xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlHttp.send(FD);
}

function send_queue_request() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            ticket_queue_response(xmlHttp);
    }
    xmlHttp.ontimeout = function (e) {
        dev_error("Error contacting server!");
    };
    var FD = new FormData();
    FD.append("message_tag", "queue_request");
    xmlHttp.open("POST", "/search", true);
    xmlHttp.send(FD);
}




function show_ticket(ticket_id) {
    console.log("Ticket number: " + ticket_id);
    send_group_search(ticket_id);
    $("#group-results-zone").empty();
    $("#groups-title").text("Loading...");
    event.preventDefault();
    transition_to_groups();
    current_ticket_id = ticket_id;
}

var current_ticket_text = "";

function submit_ticket_screen() {

    var txt = $("#searchbox").val();

    event.preventDefault();
    transition_to_submit_ticket(txt);
    current_ticket_text = txt;
}

function submit_ticket() {

    var txt = current_ticket_text;
    var clustering_dimensions = 300;

    console.log("Submitting ticket with text: " + txt);

    send_new_ticket(txt, $('#group_number_range').val(), clustering_dimensions);

    event.preventDefault();
    transition_to_start();
}


function submit_search(event) {
    request_all_papers_in_ticket();
    event.preventDefault();
    transition_to_results(title="Showing All Results");
}

function create_PDF_result_HTML(paper_name ,preview, thumbnail_url, pdf_url) {
    var preview_split = preview.split(/\r?\n/);
    var preview_first_line = preview_split[0];
    var preview_rest = "";
    if (preview_split.length > 1) {
        for (var i = 1; i < preview_split.length; i++) {
            if (i == preview_split.length - 1) {
                preview_rest += preview_split[i];
            } else {
                preview_rest += preview_split[i] + "\n";
            }
            
        }
    }

    var PDF_Result_HTML =
        "<div class='row result-row'>" +
            "<div class='col-md-auto'>" +
            "<a href='#' onclick='transition_to_pdf_preview(\"" + pdf_url +"\")'>" +
                "<img src='" + thumbnail_url + "' class='rounded-lg pdf-thumbnail'>" +
            "</a>" +
            "</div>" +
            "<div class='col'>" +
            "<div class='card-block'>" +
        "<h2 class='card-title'>" + preview_first_line + "</h2>" +
            "<p style='margin:0;'>Summary:</p>" +
            "<p class='card-text'>" + preview_rest +"</p>" +
            //"<p class='card-text'>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>" +
            "<a href='#' class='btn btn-primary' onclick='transition_to_pdf_preview(\"" + pdf_url +"\")'>Preview PDF</a>" +
            "<a href='#' class='btn btn-primary' onclick='transition_to_summarisation(\"" + paper_name +"\")'>View Abstract</a>" +
            "<a href='" + pdf_url + "' target='_blank' class='btn btn-primary'>Download</a>" +
            "</div>" +
            "</div>" +
        "</div>";
    return PDF_Result_HTML;
}

function create_group_HTML(group_number, group_tag, group_size, thumnail_source, ticket) {

    var group_HTML =
        "<div class='row group-row' onclick='show_papers_in_group(" + group_number + "," + ticket +")'>" +
            "<div class='col-md-auto'>" +
                "<img src='" + thumnail_source + "' class='rounded-lg pdf-thumbnail'>" +
            "</div>" +
            "<div class='col'>" +
                "<div class='card-block'>" +
                    "<h2 class='card-title'>Group " + (group_number + 1) + "</h2>" +
                    "<p>Concepts commonly found in this group:</p>" +
                    "<h4 class='card-text card-title'>" + group_tag + "</h4>" +
                    "<p>Number of papers in this group: " + group_size +"</p>" +
                "</div>" +
            "</div>" +
        "</div>";
    return group_HTML;
}

function create_ticket_HTML(ticket_id, ticket_name, ticket_progress, ticket_status, ticket_priority) {

    var group_HTML =
        "<div class='row ticket-row' onclick='show_ticket(" + ticket_id + ")'>" +
            "<div class='col'>" +
            "<div class='card-block'>" +
            "<h2 class='card-title'>Search: " + ticket_name+ "</h2>" +
            "<p style='margin-bottom:0;'>Ticket ID: "+ticket_id+". Ticket status: "+ticket_status+". Ticket priority: "+ticket_priority+"</p>" +
            "<p style='margin-bottom:0;'>Ticket progress: " + ticket_progress + "%</p>" +
            "</div>" +
            "</div>" +
            "</div>";
    return group_HTML;
}

function search_response(xmlHttp_response) {
    var json_response = JSON.parse(xmlHttp_response.responseText);

    console.log(json_response);

    $("#results-zone").empty();
    for (var i = 0; i < json_response.paper_names.length; i++) {

        var thumnail_source = json_response.thumbnails[i].substring(16);
        var pdf_source = json_response.pdf_urls[i].substring(16);

        var PDF_Result_HTML = create_PDF_result_HTML(json_response.paper_names[i], json_response.previews[i], thumnail_source, pdf_source);
        $("#results-zone").append(PDF_Result_HTML);

    }
}


function show_papers_in_group(group_number, ticket) {
    current_group = group_number;
    papersRequest(saved_group_data[ticket].papers_in_each_group[group_number], ticket);
}

function papers_response(xmlHttp_response) {
    var json_response = JSON.parse(xmlHttp_response.responseText);
    $("#results-zone").empty();

    
    for (var i = 0; i < json_response.paper_names.length; i++) {

        var thumnail_source = json_response.thumbnails[i].substring(16);
        var pdf_source = json_response.pdf_urls[i].substring(16);

        var PDF_Result_HTML = create_PDF_result_HTML(json_response.paper_names[i], json_response.previews[i], thumnail_source, pdf_source);
        $("#results-zone").append(PDF_Result_HTML);
    }
    transition_to_results(title = "> Group " + (current_group + 1));
}


function show_saved_groups(ticket) {

    $("#group-results-zone").empty();
    $("#groups-title").text("Similar Paper Groups");
    //console.log(Object.keys(saved_group_data.group_tags).length);
    for (var i = 0; i < Object.keys(saved_group_data[ticket].group_tags).length; i++) {
        var thumnail_source = saved_group_data[ticket].thumbnail_urls[i].substring(16);
        var group_number = i;
        var group_tag = saved_group_data[ticket].group_tags[i];
        var group_size = Object.keys(saved_group_data[ticket].papers_in_each_group[i]).length;

        var group_HTML = create_group_HTML(group_number, group_tag, group_size, thumnail_source, ticket);
        $("#group-results-zone").append(group_HTML);
    }
}


function ticket_queue_response(xmlHttp_response) {
    var json_response = JSON.parse(xmlHttp_response.responseText);
    saved_ticket_data = json_response;

    console.log(saved_ticket_data);

    $("#start-tickets-zone").empty();

    if (json_response.length > 0) {
        for (var i = 0; i < json_response.length; i++) {
            var current_ticket_id = saved_ticket_data[i].ticket_id;
            var current_ticket_name = saved_ticket_data[i].ticket_name;
            var current_ticket_progress = saved_ticket_data[i].progress;
            var current_ticket_status = saved_ticket_data[i].status;
            var current_ticket_priority = saved_ticket_data[i].priority;
            var current_ticket_queue_pos = saved_ticket_data[i].queue_pos;

            var ticket_HTML = create_ticket_HTML(current_ticket_id, current_ticket_name, current_ticket_progress, current_ticket_status, current_ticket_priority);
            $("#start-tickets-zone").append(ticket_HTML);
        }
    }

    $("#start-zone-body").text("See all tickets in the system here.");

    //var new_ticket_id = json_response.ticket_id;
    //var new_ticket_name = json_response.ticket_name;
    //var new_ticket_progress = json_response.progress;
    //var new_ticket_status = json_response.status;
    //var new_ticket_priority = json_response.priority;
    //var new_ticket_queue_pos = json_response.queue_pos;



    //show_saved_groups(json_response.ticket);
    // refresh queue list

}

function group_search_response(xmlHttp_response) {
    var json_response = JSON.parse(xmlHttp_response.responseText);


    saved_group_data[json_response.ticket] = json_response;

    show_saved_groups(json_response.ticket);

}



send_queue_request();