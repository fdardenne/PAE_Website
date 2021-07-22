function totalSidebar(){
    var availableYear = ["#bac1", "#bac2", "#bac3", "#mineure", "#hors_programme"]
    for(var i=0; i< availableYear.length; i++){
        var BAC = parseInt($(availableYear[i]).text())
        var total = parseInt($('#Total').text())
        $('#Total').html(total + BAC)

    }
}

function modifySidebar(cts, bac, operation) {
    var BAC = parseInt($(bac).text())
    var total = parseInt($('#Total').text())

    if (operation == "+"){
        $(bac).html(BAC + cts)
        $('#Total').html(total + cts)
    }else{
        $(bac).html(BAC - cts)
        $('#Total').html(total - cts)
    }
}

function minorChange(bool, firstTime=false){

    if (year != "#mineure"){
        return
    }
    if(bool){
        $("#courseFormOther").hide()
        $("#courseForm").show()
        $("#submitForm").attr("form", "courseForm")
        $("#appSinf").attr("form", "courseForm")
        

        $(".minorCts").each(function(index){
            var cts = parseInt($(this).val())
            if ($.isNumeric(cts)){
                modifySidebar(cts, year, "-")
            }
        })

        if(!firstTime){
            $('#courseForm :checkbox:checked').each(function(index) {
                var cts = parseInt($(this).attr("cts"))
                modifySidebar(cts, year, "+")
            })
        }
       
    }else{
        $("#courseFormOther").show()
        $("#courseForm").hide()
        $("#submitForm").attr("form", "courseFormOther")
        $("#appSinf").attr("form", "courseFormOther")

        $('#courseForm :checkbox:checked').each(function(index) {
            var cts = parseInt($(this).attr("cts"))
            modifySidebar(cts, year, "-")
        })

        if(!firstTime){
            
            $(".minorCts").each(function(index){
                var cts = parseInt($(this).val())
                if ($.isNumeric(cts)){
                    modifySidebar(cts, year, "+")
                }
            })
        }
    }
}


var year = "#" + $('#title').text()
if (year == "Hors programme") {
    year = "#horsProgramme"
}

// Hide/Show the custom minor in function of the checkbox
minorChange($('#appSinf').is(":checked"), true)
$('#appSinf').change(function() {
    minorChange(this.checked)
})

// Compute the total of the sidebar 
totalSidebar()

// When the student check/uncheck a course
$('#courseForm :checkbox').change(function() {

    // this will contain a reference to the checkbox   
    if (this.checked) {
        var cts = parseInt($(this).attr("cts"))
        modifySidebar(cts, year, "+")
    } else {
        var cts = parseInt($(this).attr("cts"))
        modifySidebar(cts, year, "-")
    }
});

// When the page load, count the number of credits of the actual checked
$('#courseForm :checkbox:checked').each(function(index) {
    var cts = parseInt($(this).attr("cts"))
    modifySidebar(cts, year, "+")
})

// Sidebar custom minor credits
$('#minorTable').on('focusin',".minorCts", function(){
    if ($.isNumeric($(this).val())){
        $(this).data('val', $(this).val());
    }else{
        $(this).data('val', 0);
    }
});



$("#minorTable").on("change", ".minorCts", function(event){
    if  (!$('#appSinf').is(":checked")){
        var prev = parseInt($(this).data('val'));
        var current = parseInt($(this).val());

        modifySidebar(prev, year, "-")
        modifySidebar(current, year, "+")
    }
});

$(".minorCts").each(function(index){
    var cts = parseInt($(this).val())
    if ($.isNumeric(cts)){
        modifySidebar(cts, year, "+")
    }
})



