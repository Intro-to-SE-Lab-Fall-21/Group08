$(document).ready(function () {
    $("form").on("submit", function (event) {
        $.ajax({
            data : {
                query: $("#query").val()
            },
            type: "POST",
            url: "/inbox/search/process"
        })
        .done(function (data) {
            if (data.error) {
                $("main").hide();
                $("#errorAlert").text(data.error).show();
            } else {
                $("main").html(data.htmlText).show();
                $("#errorAlert").hide();
                $("#next").text("Next").show();
            }
            $("#loadingAlert").hide();
            $("#prev").hide();

            if (data.canNext) {
                $("#next").text("Next").show();
            } else {
                $("#next").hide();
            }
        });

        $("#errorAlert").hide();
        $("#loadingAlert").text("...loading").show();
        event.preventDefault();
    });

    $("#next").on("click", function (event) {
        $.ajax({
            data: {
                value: 1
            },
            type: "POST",
            url: "/inbox/search/next"
        })
        .done(function (data) {
            if (data.error) {
                $("main").hide();
                $("#errorAlert").text(data.error).show();
            } else {
                $("main").html(data.htmlText).show();
                $("#errorAlert").hide();
            }
            $("#loadingAlert").hide();

            if (!data.canNext) {
                $("#next").hide();
            }
            $("#prev").text("Prev").show();
        });

        $("#loadingAlert").text("...loading next search").show();
        event.preventDefault();
    });

    $("#prev").on("click", function (event) {
        $.ajax({
            data: {
                value: -1
            },
            type: "POST",
            url: "/inbox/search/next"
        })
        .done(function (data) {
            if (data.error) {
                $("main").hide();
                $("#errorAlert").text(data.error).show();
            } else {
                $("main").html(data.htmlText).show();
                $("#errorAlert").hide();
            }
            $("#loadingAlert").hide();

            if (!data.canPrev) {
                $("#prev").hide();
            }
            $("#next").text("Next").show();
        });

        $("#loadingAlert").text("...loading next search").show();
        event.preventDefault();
    });
});