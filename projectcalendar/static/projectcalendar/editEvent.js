function unCheckRepeat(){
	$('#repeat').attr('checked', false);

}

$('.rp-date').click(function(){
	var td = $('#date-checkbox-td');
	td.children('input').each(function(){
		alert(this.id);
	});
});


// $('#google-map-Modal').on('shown.bs.modal', function () {
//     google.maps.event.trigger(map, "resize");
// });

function initMapModal() {
setTimeout(function () {
    google.maps.event.trigger(map, 'resize');
}, 500)};

function saveLocation(){
  var s_box = $('#pac-input');
  console.log(s_box);
  var addr = s_box[0].value;
  console.log(addr);
  var loc_input = $('#location');
  loc_input[0].value = addr;
  

}