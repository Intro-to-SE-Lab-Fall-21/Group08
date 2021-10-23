$(document).ready(function() {
    const inboxStateEnum = {
        idle: 0,
        fetch: 1,
        search: 2
    };
    let currentInboxState = inboxStateEnum.idle;

    // Inital calls
    $("#search").val("")
    fetchMessage();

    function fetchMessage() {
        currentInboxState = inboxStateEnum.fetch;

        $("#loadMoreMessages").hide();
        $("#loadAlert").text("Loading messages...")

        $.ajax({
            type: "POST",
            url: "/process/inbox/fetch"
        })
        .done(function (data) {
            $("main").append(data.text)

            if (data.empty) {
                $("#loadMoreMessages").hide();
            } else {
                $("#loadMoreMessages").show();
            }
            $("#loadAlert").text("")

            currentInboxState = inboxStateEnum.idle;
        });
    };

    function submitSearch() {
        currentInboxState = inboxStateEnum.search;

        // Gets value from the search bar
        const searchQuery = $("#search").val();

        $.ajax({
            data: {
                search: searchQuery
            },
            type: "POST",
            url: "/process/inbox/search"
        })
        .done(function (data) {
            currentInboxState = inboxStateEnum.idle;

            if (data.empty) {
                $("#loadAlert").text("No messages found.")
            } else {
                fetchMessage();
            }
        });

        $("main").empty(); // Clear messages from the page
        $("#loadMoreMessages").hide() // Hide load more messages link
        $("#loadAlert").text("Searching...")
    };

    $("#loadMoreMessages").on("click", function(event) {
        fetchMessage();
        event.preventDefault();
    });

    $("form").submit(function (event) {
        if (currentInboxState == inboxStateEnum.idle) {
            submitSearch(); // Submit query to the server
        } else {
            const elementName = "form > span"
            $(elementName).text("Cannot search now.").show();
            $(elementName).fadeOut(1000);
        }
        event.preventDefault();
    });

});