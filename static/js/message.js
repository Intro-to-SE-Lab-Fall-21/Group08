$(document).ready(function () {
    $("main").hide();

    $.ajax({
        data: {
            uid: $("h1").attr("uid")
        },
        type: "POST",
        url: "/process/inbox/message"
    })
    .done(function (data) {
        $("#infoAlert").hide();

        $("#subject").html(data.subject);
        $("#from").append(data.from);
        $("#to").append(data.to);
        $("#date").append(data.date);
        $("#body").append(data.text);
        $("main").show();
    });
});