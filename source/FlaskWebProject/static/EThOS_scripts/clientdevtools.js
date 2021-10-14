
var log_text = $("#dev-log");
log_text.text("Clientside Loaded");

var timeout_var;



function dev_error(err) {
    //if (timeout_var !== null) {
    //    clearTimeout(timeout_var);
    //}
    log_text.text(err);
}
function dev_log(txt) {
    log_text.text(txt);
    //if (timeout_var !== null) {
    //    clearTimeout(timeout_var);
    //}
    //timeout_var = setTimeout(
    //    function () {
    //        log_text.text("Clientside Idle");
    //    }, 15000);
}


function clear_search() {
    dev_log("Clearing search");
    $("#results-zone").empty();
    $("#group-results-zone").empty();
    saved_group_data = {};
    transition_to_start();
    dev_log("Cleared");
}

function refresh_backend() {
   //send_devtool_message("completion_update", "", devtool_message_update);
   send_devtool_message("completion_update", "", devtool_message_update);
}


function delete_generated_data() {
    dev_log("Deleting generated data...");
    $("#progress_percent").css("width", "0"+"%");
    send_devtool_message("delete_generated_data", "", devtool_message_update);
    $("#progressbar").show(100);

}

function rebuild_generated_data() {
    dev_log("Rebuilding generated data...");
    $("#progress_percent").css("width", "0" + "%");
    send_devtool_message("rebuild_generated_data", "", devtool_message_update);
    $("#progressbar").show(100);

}
function delete_sumarisations() {

}

function rebuild_summarisations() {

}

function devtool_message_update(xmlHttp_response) {
    var json_response = JSON.parse(xmlHttp_response.responseText);

    dev_log(json_response.body);
    var percent_complete = json_response.percent_complete;

    $("#progressbar").show(100);
    $("#progress_percent").css("width", (percent_complete*100).toString() + "%");


    if (timeout_var !== null) {
        clearTimeout(timeout_var);
    }

    if (percent_complete == 1) {
        timeout_var = setTimeout(
            function () {
                $("#progressbar").hide(100);
            }, 1000);
    }

}

function send_devtool_message(message_tag, body, return_function) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            return_function(xmlHttp);
    }
    xmlHttp.ontimeout = function (e) {
        dev_error("Error contacting server!");
    };
    var FD = new FormData();
    FD.append("message_tag", message_tag);
    FD.append("body", body);


    xmlHttp.open("POST", "/devtool", true);
    xmlHttp.send(FD);
}

$("#progressbar").hide();



var group_number_range = document.getElementById('group_number_range');
var group_number_range_indicator = document.getElementById('group_number_range_indicator');

group_number_range_indicator.innerHTML = group_number_range.value;

// use 'change' instead to see the difference in response
group_number_range.addEventListener('input', function () {
    group_number_range_indicator.innerHTML = group_number_range.value;
}, false);