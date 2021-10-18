function setupText(uids) {
    for (let i = 0; i < uids.length; i++) {
        let uid = "#" + uids[i];

        // When the user clicks on the link, text should show up
        // below the message
        $(uid).on("click", function (event) {
            $.ajax({
                data: {
                    uid: uids[i]
                },
                type: "POST",
                url: "/inbox/search/show"
            })
            .done(function (data) {
                $(uid + "-text").html(data.text).show();

                $(uid).off("click");
                $(uid).on("click", function (event) {
                    $(uid + "-text").toggle();
                });
            });

            $(uid + "-text").text("...loading").show();
        });
    };
};

function handleData(data) {
    if (data.error) {
        $("main").hide();
        $("#errorAlert").text(data.error).show();
    } else {
        $("main").html(data.htmlText).show();
        $("#errorAlert").hide();
        setupText(data.uids);
    }
    $("#loadingAlert").hide();
}

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
            handleData(data);
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
            handleData(data);
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
            handleData(data);
            if (!data.canPrev) {
                $("#prev").hide();
            }
            $("#next").text("Next").show();
        });

        $("#loadingAlert").text("...loading next search").show();
        event.preventDefault();
    });
});