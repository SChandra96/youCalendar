function popRepeatPage(checkbox) {
	if(checkbox.checked == true){
		alert("Hello!");
	}else{
		document.getElementById("submit").addAttribute("disabled");
   }
}

// function popRepeatPage2(checkbox) {
// 	if(checkbox.checked == true){
// 		$('#myModal').modal('show');
// 	}else{
// 		document.getElementById("submit").addAttribute("disabled");
//    }
// }


// ​$("[id^=repeat2]").on("change", function(e){
// 	if(e.target.checked){
// 	$('#myModal').modal();
// 	}
// });