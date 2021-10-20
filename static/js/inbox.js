$(document).ready(function() {
    function fetchMessage() {
        $("#loadMoreMessages").hide();
        $("#loadAlert").text("Loading messages...")
    
        $.ajax({
            type: "POST",
            url: "/process/inbox/fetch"
        })
        .done(function (data) {
            $("main").append(data.text)
    
            if (data.empty) {
                $("#loadMoreMessages").off("click")
                $("#loadMoreMessages").hide();
            } else {
                $("#loadMoreMessages").show();
                $("#loadAlert").text("")
            }
        });
    };

    $("#loadMoreMessages").on("click", function(event) {
        fetchMessage();
        event.preventDefault();
    });

    $("form").on("submit", function (event) {
        event.preventDefault();
    });

    // Inital function call
    fetchMessage();
});