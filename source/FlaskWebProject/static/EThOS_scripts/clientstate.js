

var zone_state = "start";



var transition_duration = 100;
var current_group = 0;





function transition_to_results(title=null) {
    if (zone_state !== "results") {

        //if (zone_state == "start") {
        //    $(".start-zone").hide(transition_duration);
        //}
        //if (zone_state == "pdf_preview") {
        //    $(".pdf-zone").hide(transition_duration);
        //    $("#search-zone").show(transition_duration);
        //}
        //if (zone_state == "summarisation") {
        //    $(".summarisation-zone").hide(transition_duration);
        //}
        //if (zone_state == "groups") {
        //    $(".groups-zone").hide(transition_duration);
        //}
        hide_current_state();

        if (title !== null) {
            $("#results-title").text(title);
        }
        

        $(".results-zone").show(transition_duration);
        zone_state = "results";

    }
}

function transition_to_pdf_preview(pdf_url) {
    if (zone_state !== "pdf_preview") {

        jQuery("#pdf-iframe").attr("src", pdf_url);


        //if (zone_state == "start") {
        //    $(".start-zone").hide(transition_duration);
        //}
        //if (zone_state == "results") {
        //    $(".results-zone").hide(transition_duration);
        //}
        //if (zone_state == "summarisation") {
        //    $(".summarisation-zone").hide(transition_duration);
        //}
        //if (zone_state == "groups") {
        //    $(".groups-zone").hide(transition_duration);
        //}
        hide_current_state();

        $("#search-zone").hide(transition_duration);
        $(".pdf-zone").show(transition_duration);
        zone_state = "pdf_preview";
    }
}

function transition_to_summarisation(paper_name) {
    if (zone_state !== "summarisation") {

        //if (zone_state == "results") {
        //    $(".results-zone").hide(transition_duration);
        //}
        //if (zone_state == "start") {
        //    $(".start-zone").hide(transition_duration);
        //}
        //if (zone_state == "pdf_preview") {
        //    $(".pdf-zone").hide(transition_duration);
        //    $("#search-zone").show(transition_duration);
        //}
        //if (zone_state == "groups") {
        //    $(".groups-zone").hide(transition_duration);
        //}
        hide_current_state();

        $("#summarisation-title").text("Loading...");
        $("#summarisation-body").text("...");
        summarisationRequest(paper_name);



        $(".summarisation-zone").show(transition_duration);
        zone_state = "summarisation";
    }
}

function transition_to_start() {
    if (zone_state !== "start") {

        //if (zone_state == "results") {
        //    $(".results-zone").hide(transition_duration);
        //}
        //if (zone_state == "summarisation") {
        //    $(".summarisation-zone").hide(transition_duration);
        //}
        //if (zone_state == "pdf_preview") {
        //    $(".pdf-zone").hide(transition_duration);
        //    $("#search-zone").show(transition_duration);
        //}
        //if (zone_state == "groups") {
        //    $(".groups-zone").hide(transition_duration);
        //}
        hide_current_state();

        $(".start-zone").show(transition_duration);
        zone_state = "start";
    }
}

function transition_to_groups() {
    if (zone_state !== "groups") {

        //if (zone_state == "results") {
        //    $(".results-zone").hide(transition_duration);
        //}
        //if (zone_state == "summarisation") {
        //    $(".summarisation-zone").hide(transition_duration);
        //}
        //if (zone_state == "pdf_preview") {
        //    $(".pdf-zone").hide(transition_duration);
        //    $("#search-zone").show(transition_duration);
        //}
        //if (zone_state == "start") {
        //    $(".start-zone").hide(transition_duration);
        //}
        hide_current_state();

        $(".groups-zone").show(transition_duration);
        zone_state = "groups";
    }
}

function transition_to_submit_ticket(ticket_text) {
    if (zone_state !== "submit-ticket") {

        //if (zone_state == "results") {
        //    $(".results-zone").hide(transition_duration);
        //}
        //if (zone_state == "summarisation") {
        //    $(".summarisation-zone").hide(transition_duration);
        //}
        //if (zone_state == "pdf_preview") {
        //    $(".pdf-zone").hide(transition_duration);
        //    $("#search-zone").show(transition_duration);
        //}
        //if (zone_state == "start") {
        //    $(".start-zone").hide(transition_duration);
        //}
        hide_current_state();
        $("#submit-ticket-zone-body").text("Ticket's search text: " + ticket_text);

        $(".submit-ticket-zone").show(transition_duration);
        zone_state = "submit-ticket";
    }
}



function hide_current_state() {
    // zone_state: current zone state BEFORE transition
    if (zone_state == "results") {
        $(".results-zone").hide(transition_duration);
    }
    if (zone_state == "summarisation") {
        $(".summarisation-zone").hide(transition_duration);
    }
    if (zone_state == "pdf_preview") {
        $(".pdf-zone").hide(transition_duration);
        $("#search-zone").show(transition_duration);
    }
    if (zone_state == "start") {
        $(".start-zone").hide(transition_duration);
    }
    if (zone_state == "groups") {
        $(".groups-zone").hide(transition_duration);
    }
    if (zone_state == "submit-ticket") {
        $(".submit-ticket-zone").hide(transition_duration);
    }
    console.log("Hiding zone: " + zone_state)
}


$(".summarisation-zone").hide();
$(".results-zone").hide();
$(".pdf-zone").hide();
$(".groups-zone").hide();
$(".submit-ticket-zone").hide();