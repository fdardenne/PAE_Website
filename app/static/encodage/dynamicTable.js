$(document).ready(function () {
    var counter = $('.dynamicTable tr').length-3;
    $("#addrow").on("click", function () {
        var newRow = $("<tr>");
        var cols = "";

        cols += '<td><input type="text" minlength="9" maxlength="9" class="form-control" name="sigle' + counter + '"/></td>';
        cols += '<td><input type="text" minlength="1" maxlength="150" class="form-control" name="titre' + counter + '"/></td>';
        cols += '<td><input type="number" min="1" max="15" class="form-control minorCts" name="cts' + counter + '"/></td>';

        cols += '<td><input type="button" class="ibtnDel btn btn-md btn-danger "  value="Delete"></td>';
        newRow.append(cols);
        $("table.order-list").append(newRow);
        counter++;
    });



    $("table.order-list").on("click", ".ibtnDel", function (event) {
        var current = parseInt($(this).closest("tr").find(".minorCts").val())
        modifySidebar(current, year, "-")
        $(this).closest("tr").remove();    
        counter -= 1
    });


});