$(document).ready(function () {

    $.ajax({
        data: {
            uid: $("h1").attr("uid")
        },
        type: "POST",
        url: "/process/draft/message"
    })
    .done(function (data) {
        $("#infoAlert").hide();

        $("#receiver").val(data.to);
        $("#subject").val(data.subject);
        tinyMCE.get('body').setContent(data.text)
        $("main").show();
    });
});