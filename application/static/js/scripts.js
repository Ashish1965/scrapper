$("#hamberger").click(()=>{

    $("#hamberger").toggleClass("fa-xmark");
        $(".nav-list").toggleClass("open"); 
    
})


document.querySelectorAll(".nav-links").forEach((Element) => {Element.addEventListener("click",()=>{
    $("#hamberger").toggleClass("fa-xmark");
    $(".nav-list").toggleClass("open")
})})