$(document).ready(function() {
    function postform(uri, user, host) {
        var field = $('<input></input>');
        var form = $('<form></form>');
        var port = '110';

        if (host.indexOf(":") > -1) {
            host, port = host.split(":");
        }

        var data = [["account",user],["hostname",host],["port",port]];

        form.attr("method", "post");
        form.attr("action", $SCRIPT_ROOT + '/delaccount');

        for (var i = 0; i < data.length; i++)
        {
            field = $('<input></input>');
            field.attr("type", "hidden");
            field.attr("name", data[i][0]);
            field.attr("value", data[i][1]);
            form.append(field);
        }

        $(document.body).append(form);
        form.submit();
    }

    $('input[name="delacc"]').bind('click', function() {
        var user = this.parentNode.parentNode.childNodes[3].innerHTML;
        var host = this.parentNode.parentNode.childNodes[5].innerHTML;

        postform('/delaccount', user, host);
    });

    $('input[name="connacc"]').bind('click', function() {
        var user = this.parentNode.parentNode.childNodes[3].innerHTML;
        var host = this.parentNode.parentNode.childNodes[5].innerHTML;

        postform('/headers', user, host);
    });

    $('input#testacc').bind('click', function() {
        var user = document.getElementById("u0").value;
        var host = document.getElementById("h0").value;
        var port = document.getElementById("p0").value;

        if (port && port != 110) {
            host = host+':'+port;
        }

        $.getJSON($SCRIPT_ROOT + '/testaccount', {
           username: user,
           hostname: host,
           }, function(data) {
             $("#estatus").text(data.result);
        });
        return false;
    });
});
