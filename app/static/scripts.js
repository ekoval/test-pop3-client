$(document).ready(function() {
    $('button[name="delacc"]').bind('click', function() {
        var id = $('button[name="delacc"]').val();

        $.getJSON($SCRIPT_ROOT + '/delaccount', {
           username: $('u'+id).val(),
           hostname: $('h'+id).val(),
           }, function(data) {
             $("estatus").text(data.result);
        });
        return false;
    });

    $('button[name="connacc"]').bind('click', function() {
        var id = $('button[name="delacc"]').val();
        var field = $('<input></input>');
        var form = $('<form></form>');
        var user = $('u'+id).val();
        var host = $('h'+id).val();
        var port = '110';

        if (host.indexOf(":") > -1) {
            var arr = host.split(":");
            host = arr[0];
            port = arr[1];
        }

        var data = [["account",user],["hostname",host],["port",port]];

        form.attr("method", "post");
        form.attr("action", $SCRIPT_ROOT + '/headers');

        for (var i = 0; i < b.length; i++)
        {
            field = $('<input></input>');
            field.attr("type", "hidden");
            field.attr("name", data[0]);
            field.attr("value", data[1]);
            form.append(field);
        }

        $(document.body).append(form);
        form.submit();
    }

    $('input[name="testacc"]').bind('click', function() {
        var user = $('input#u0').val();
        var host = $('input#h0').val();
        var port = $('input#p0').val();

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
