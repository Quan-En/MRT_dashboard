$('#start-date').datepicker({
    autoclose:true,
    format:"yyyy-mm-dd",
    clearBtn:true
}).on('changeDate', function(e){
    $("#end-date").datepicker('setStartDate', e.date);
    $("#end-date").focus()
});
$('#end-date').datepicker({
    autoclose:true,
    format:"yyyy-mm-dd",
    clearBtn:true,
});



function getValueFromDateRange() {
    // Get the input element
    // Get the value of the input
    var inputFromValue = document.getElementById("start-date").value;
    var inputToValue = document.getElementById("end-date").value;
    var button = document.getElementById("download-btn");
    // Get the output div element
    var outputModalLabel = document.getElementById("ModelContent");
    var outputStartDateTag = document.getElementById("hidden-tag-start-date");
    var outputEndDateTag = document.getElementById("hidden-tag-end-date");

    // Set the input value as the content of the output div
    if (inputFromValue === "" || inputToValue === "") {
        outputModalLabel.textContent = "Date should not be empty.";
        button.style.display = "none";
    } else {
        outputModalLabel.textContent = "Select date from " + inputFromValue + " to " + inputToValue;
        button.style.display = "block";
        outputStartDateTag.value = inputFromValue;
        outputEndDateTag.value = inputToValue;
    }
};

function getValueFromSelectedDate() {
    // Get the input element
    // Get the value of the input
    var inputDateValue = document.getElementById("selectd-date").value;

    // Get the output div element
    var outputQueryData = document.getElementById("query_data");

    // Set the input value as the content of the output div

    outputQueryData.value = inputDateValue;
};

$(function() {
    $('#datepicker').datepicker({
      autoclose: true,
      clearBtn: true,
      format: 'yyyy-mm-dd'
    }).on('changeDate', function(e) {
      var selectedDate = e.format('yyyy-mm-dd');
      $('#query_data').val(selectedDate);
    });
})