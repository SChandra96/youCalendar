function popRepeatPage(checkbox) {
    if(checkbox.checked == true){
        alert("Hello!");
    }else{
        document.getElementById("submit").addAttribute("disabled");
   }
}