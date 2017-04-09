function getList() {
    $.ajax({
        url: "/get-list-json",
        dataType : "json",
        success: notify
    });

}

function notify(events) {
	console.log(events);
	console.log(events.length);
	for (var i = 0; i < events.length; i++) {
		var event = events[i];
		var curDate = (new Date()).toISOString();
		var curMoment = moment(new Date());
		if (event.hasOwnProperty('notificationPref') && event.hasOwnProperty('whenToNotify')) {
			if(event.hasOwnProperty('ranges')) {
				var startDate = (event.ranges)[0].r_start + "T" + event.start+"-04:00";
				var endDate = (event.ranges)[0].r_end + "T" + event.end+"-04:00";
				var startMoment = moment(startDate); //moment corrosponding to range start date
				var endMoment = moment(endDate); //moment corrosponding to range end date
				
				if (curMoment.isBefore(startMoment, 'day') || curMoment.isSame(startMoment, 'day') || curMoment.isSame(endMoment, 'day')  ||
					curMoment.isAfter(startMoment, 'day') && curMoment.isBefore(endMoment, 'day')) {
					var currdow = curMoment.day();
					if ((event.dow).indexOf(currdow) !== -1) { //if today is one of the days on which event will happen
						var todayEventStartMoment = moment(curMoment.format('YYYY-MM-DD') + 'T' + event.start+"-04:00");
						//var timeDiff = moment.duration(todayEventStartMoment.diff(curDate)).minutes();
						var timeDiff = todayEventStartMoment.diff(curDate, event.notificationPref);
						console.log(event.title)
						console.log(todayEventStartMoment);
						console.log(timeDiff);
						if (timeDiff >= 0 && timeDiff <= 60) { //time difference between today's start time of evtmt and current time
							var time = todayEventStartMoment.format("hh:mm");
							time = time + ((todayEventStartMoment.hour()) >= 12 ? ' PM' : ' AM');
							var notificationMessage = "Reminder: You have an event coming up today: " + event.title + " at " + time;
							$.notify(notificationMessage, 
									{position:"right bottom", clickToHide: true, 
									 style:"bootstrap", className:"success", autoHide:false});
						}
					}
				}	
			} else {
				var startMoment = moment(event.start + "-04:00");
				var timeDiff = startMoment.diff(curDate, event.notificationPref);
				if (timeDiff >= 0 && timeDiff <= 60) { 
					var time = startMoment.format("hh:mm");
					time = time + ((startMoment.hour()) >= 12 ? ' PM' : ' AM');
					var notificationMessage = "Reminder: You have an event coming up today: " + event.title + " at " + time;
					$.notify(notificationMessage, 
							{position:"right bottom", clickToHide: true, 
							style:"bootstrap", className:"success", autoHide:false});
				}
			}
		}
	} 	
}

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
			eventClick: function(event, element, ev) {
				console.log(JSON.stringify(event));
				var elemId = event["id"];
				addEventPopUP(event,element);
				// window.location.href = "/check_event_privacy/" + elemId;

			},
			eventRender: function(event){
				if(event.hasOwnProperty('ranges')){
					return (event.ranges.filter(function(range){ // test event against all the ranges
						return (event.start.isBefore(range.r_end) &&
								event.end.isAfter(range.r_start));
					}).length)>0; //if it isn't in one of the ranges, don't render it (by returning false)
			}},

		});
		getList();

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
	window.setInterval(getList, 1800000); //set correctly
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

function addEventPopUP(calevent,event){
	if ($('.bubblemain').length > 0) {
	// exists.
		$('.bubblemain').remove();
	}

	var x = event.clientX;
	var y = event.clientY;
	var xd = 160;
	var yd = 20;
	var eventJson = JSON.parse(JSON.stringify(calevent));
	console.log("line 137: "+eventJson);
	console.log(eventJson.id);
	var eventId = eventJson.id;
	var contStr = '<div class = "bubble-title">'+eventJson.title+'</div>'
					+'<div class = "bubble-fname"> Time </div>';
					
	if(eventJson.end == null){
		contStr += '<div class = "bubble-fvalue">'
					+eventJson.start
					+'</div>';
	}
	else{
		contStr += '<div class = "bubble-fvalue">'
					+eventJson.start+'~'
					+eventJson.end
					+'</div>';
	}

	var locStr = "";
	if(!(eventJson.location == "")){
		locStr = '<div class = "bubble-fname"> Location </div>'
				+'<div class = "bubble-fvalue">'
				+eventJson.location
				+'</div>';
	}

	var btnStr1 = '<div id = "div-popup-edit-btn">'
					+'<button type="button" id = "popup-edit-btn" onclick = \
					"jumpToEditPage('+eventId+')">'
					+'Edit'
					+'</button>'
					+'</div>';

	var btnStr2 = '<div id = "div-popup-del-btn">'
					+'<button type="button" id = "popup-del-btn" onclick = \
					"deleteEvent('+eventId+')">'
					+'Delete'
					+'</button>'
					+'</div>';



	var htmlStr = '<div class = "bubblemain"> '
					+'<div class = "bubblecontent"> '
					+'<button type="button" class="close" onclick = "closePopUp(this)">\
					&times;</button>' 
					+contStr
					+locStr
					+btnStr1
					+btnStr2
					+'</div>'
					+'</div>';

	$('#calendar').append(htmlStr);

	win_wid = $(window).width();
	var px = x-xd;
	var py = y+yd;
	var bx = $('.bubblemain').width();
	console.log("win_wid: "+win_wid);
	console.log("pop width: "+ bx);
	if(px<2){
		px = 2;
	}
	else if(px+bx>win_wid){
		px = win_wid-bx-30;
	}


	$('.bubblemain').css('top', py);
	$('.bubblemain').css('left', px);

}

function closePopUp(element){
	var win = $(element).parent().parent();
	win.remove();
}

function jumpToEditPage(eventId){
	window.location.href = "/check_event_privacy/" + eventId;
}

function deleteEvent(eventId){
	console.log("line 207: " + eventId);

}