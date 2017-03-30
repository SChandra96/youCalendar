if (window.location.pathname === '/') { 
	$(document).ready(function() {

		// page is now ready, initialize the calendar...

		$('#calendar').fullCalendar({
			// put your options and callbacks here
			header: {left: 'title month, agendaWeek', right: 'prev, next'},
			defaultView: 'basicWeek',
			events:'/get-list-json',
			dayClick: function() {
				alert('a day has been clicked!');
			},
			eventClick: function(event, element) {
				console.log(JSON.stringify(event));
				
				var elemId = event["id"];
				window.location.href = "/edit_event/" + elemId;

				//$('#calendar').fullCalendar('updateEvent', event);
			},
			eventRender: function(event){
				console.log(event);
				if(event.hasOwnProperty('ranges')){
					return (event.ranges.filter(function(range){ // test event against all the ranges
						return (event.start.isBefore(range.r_end) &&
								event.end.isAfter(range.r_start));
					}).length)>0; //if it isn't in one of the ranges, don't render it (by returning false)
			}},

		});

		// $.getJSON('get-timezone-list', function(timezones) {
		// 	$.each(timezones, function(i, timezone) {
		// 		if (timezone != 'UTC') { // UTC is already in the list
		// 			$('#timezone').append(
		// 				$("<option/>").text(timezone).attr('value', timezone)
		// 			);
		// 		}
		// 	});
		// });
	});
}
else {
	$(document).ready(function() {
		$( "#id_datepicker" ).datepicker({
			dateFormat:"yy-mm-dd",
		});
		$("#id_datepicker").on("change",function(){
		var selected = $(this).val();
		console.log(selected);
		});

		$( "#id_datepicker_st" ).datepicker({
			dateFormat:"yy-mm-dd",
		});
		$("#id_datepicker_st").on("change",function(){
		var selected = $(this).val();
		console.log(selected);
		});

		$( "#id_datepicker_end" ).datepicker({
			dateFormat:"yy-mm-dd",
		});
		$("#id_datepicker_end").on("change",function(){
		var selected = $(this).val();
		console.log(selected);
		});
	});
}