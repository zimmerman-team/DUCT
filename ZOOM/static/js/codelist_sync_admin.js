$(document).ready(function (){
    $('#sync-codelists').click(function(){

       var btn = $('#sync-codelists');

       $.ajax({
           type: "GET",
           url: "/admin/iati_synchroniser/codelist/sync-codelists/",
           beforeSend: function() {
               btn.removeClass("btn-success");
               btn.addClass("btn-warning");
               btn.text("Updating...");
           },
           statusCode: {
               200: function() {
                   btn.addClass("btn-info");
                   btn.text("Updated");
               },
               404: function() {
                   btn.addClass("btn-danger");
                   btn.text("404 error...");
               },
               500: function() {
                   btn.addClass("btn-danger");
                   btn.text("500 error...");
               }
           }
       });
   });
});