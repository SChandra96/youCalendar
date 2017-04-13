var urlArray = window.location.pathname.split("/");
var token = urlArray[urlArray.length-1];
var apptId;
function check(events) {
	console.log(events);
}
function getList() {
    $.ajax({
        url: "/get-appt-list-json/" +token,
        dataType : "json",
        success: check,
    });

}
function bookAppointment() {
	window.location.href = "/book_appt/" + token + "/" + apptId;
}
$(document).ready(function() {

		// page is now ready, initialize the calendar...
		$('#calendar').fullCalendar({
			// put your options and callbacks here
			header: {left: 'title month, agendaWeek', right: 'prev, next'},
			defaultView: 'basicWeek',
			events:'/get-appt-list-json/' + token,
			eventClick: function(event, element) {
				if (!(event["isBooked"])) {
					apptId = event["id"];
					console.log(apptId);
					$('#bookAppointmentModal').modal('show');
				}
				
				//window.location.href = "/check_event_privacy/" + elemId;

			},
		});
		getList();
		window.setInterval(getList, 1800000)
});