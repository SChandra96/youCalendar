function unCheckRepeat(){
	$('#repeat').attr('checked', false);

}

$('.rp-date').click(function(){
	var td = $('#date-checkbox-td');
	td.children('input').each(function(){
		alert(this.id);
	});
});