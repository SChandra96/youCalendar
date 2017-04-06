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
}, 1000)};