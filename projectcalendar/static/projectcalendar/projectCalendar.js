
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
						if (timeDiff >= 0 && timeDiff <= event.whenToNotify) { //time difference between today's start time of evtmt and current time
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
				if (timeDiff >= 0 && timeDiff <= event.whenToNotify) { 
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

function addEventPopUP(calevent,event){
	if ($('.bubblemain').length > 0) {
	// exists.
		$('.bubblemain').remove();
	}

	var month_names_short =  ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
		'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
	console.log(month_names_short[1]);
	var x = event.clientX;
	var y = event.clientY;
	var xd = 160;
	var yd = 20;
	var eventJson = JSON.parse(JSON.stringify(calevent));
	console.log("line 137: "+eventJson);
	console.log(eventJson);
	var eventId = eventJson.id;
	var contStr = '<div class = "bubble-title">'+eventJson.title+'</div>'
					+'<div class = "bubble-fname"> Time </div>';
					
	var start_date = eventJson.start.substring(0,10);
	var start_month = start_date.substring(5,7);
	var start_day = start_date.substring(8,10);
	console.log(start_day);
	var s_mon = Number(start_month);
	var s_mon_name = month_names_short[s_mon-1];
	var start_time = eventJson.start.substring(11,16);
	var start_str = start_time;
	if(Number(start_time.substring(0,2))>=12){
		start_str += 'pm';
	}
	else{
		start_str += 'am';
	}
	
	if(eventJson.end == null){
		contStr += '<div class = "bubble-fvalue">'
					+start_str
					+'</div>';
	}
	else{
		var end_date = eventJson.end.substring(0,10);
		var end_time = eventJson.end.substring(11,16);
		var end_str = end_time;
		if(Number(end_time.substring(0,2))>=12){
			end_str += 'pm';
		}
		else{
			end_str += 'am';
		}
		contStr += '<div class = "bubble-fvalue">'+s_mon_name+' '+start_day
					+', '
					+start_str+' - '
					+end_str
					+'</div>';
	}

	var locStr = "";
	if(!(eventJson.location == null || eventJson.location == "None")){
		locStr = '<div class = "bubble-fname"> Location </div>'
				+'<div class = "bubble-fvalue">'
				+eventJson.location
				+'</div>';
	}

	if (calevent.isApptSlot == null) {
		console.log(event);
		 if (calevent.apptEvent) {
			var apptUrl = '<div class = "bubble-fname"> Appointment URL: </div>'
							+'<div class = "bubble-fvalue">'
							+'<a href=' + calevent.apptURL + ' target="_blank" >' + calevent.apptURL + '</a>' 
							+'</div>';
		}
		else {
			var apptUrl = "";
		}
		var btnStr1 = '<div id = "div-popup-edit-btn">'
					+'<button type="button" id = "popup-edit-btn" \
					class = "btn btn-lg btn-primary btn-block" onclick = \
					"jumpToEditPage('+eventId+')">'
					+'Edit'
					+'</button>'
					+'</div>';

		var btnStr2 = '<div id = "div-popup-del-btn">'
						+'<button type="button" id = "popup-del-btn" \
						 class = "btn btn-lg btn-primary btn-block"  onclick = \
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
						+apptUrl
						+btnStr1
						+btnStr2
						+'</div>'
						+'</div>';
		}
		else {
			var htmlStr = '<div class = "bubblemain"> '
						+'<div class = "bubblecontent"> '
						+'<button type="button" class="close" onclick = "closePopUp(this)">\
						&times;</button>' 
						+contStr
						+locStr
						+'</div>'
						+'</div>';
		}
		$('#calendar').append(htmlStr);

		win_wid = $(window).width();
		win_hei = $(window).height();
		var px = x-xd;
		var py = y+yd;
		var bx = $('.bubblemain').width();
		var by = $('.bubblemain').height()
		console.log("win_wid: "+win_wid);
		console.log("pop width: "+ bx);
		if(px<2){
			px = 2;
		}
		else if(px+bx>win_wid){
			px = win_wid-bx-30;
		}
		else{
			var pi = px/(win_wid/7);
			px = pi*win_wid/7;
		}

		if(py+by+20>win_hei){
			py = win_hei-by-20;
		}
		else{
			var pi = py/(win_hei/10);
			py = pi*win_hei/10;
		}

		if(py<140){
			py = 140;
		}
	console.log("py: "+py);
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
	window.location.href = "/delete_event/" + eventId;
}

if (window.location.pathname === '/') { 
	$(document).ready(function() {
		console.log("line 63");
		// page is now ready, initialize the calendar...
			//setInterval(function(){$('#calendar').fullCalendar('refetchEvents')}, 3000);
		$("#calnames").click(function() {
				var calNames=[];
				$.each($("input[name='calendars']:checked"), function(){            
                		calNames.push($(this).val());
            	});
            	console.log(calNames.join(","));
            	if (calNames.length != 0) {
            		var url = '/get-cal-specific-list-json/' + calNames.join(",");
            	} else {
            		var url = '/get-list-json';
            	}
            	console.log(url)
            	$('#calendar').fullCalendar('removeEvents');
            	$('#calendar').fullCalendar('addEventSource', url);
            	$('#calendar').fullCalendar('rerenderEvents');
            	
			});
		$('#calendar').fullCalendar({
		// put your options and callbacks here
				header: {left: 'title month, agendaWeek', right: 'prev, next'},
				// defaultView: 'basicWeek',
				defaultView: 'agendaWeek',
				eventSources: ['/get-list-json'],
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
		window.setInterval(getList, 30*60000); //set correctly
	});
}
else if (window.location.pathname.slice(1, 5) === "edit") {
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

//window.onload = refresh();

