$(document).ready(function() {
    function postform(uri, user, host) {
        var field = $('<input></input>');
        var form = $('<form></form>');
        var port = '110';

        if (host.indexOf(":") > -1) {
            var array = host.split(":");
            host = array[0];
            port = array[1];
        }

        var data = [["account",user],["hostname",host],["port",port]];

        form.attr("method", "post");
        form.attr("action", $SCRIPT_ROOT + uri);

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
        var pswd = document.getElementById("s0").value;

        $.post($SCRIPT_ROOT + '/testaccount', {
           account: user,
           hostname: host,
           port: port,
           passwd: pswd,
           }, function(data, rc) {
              var result = 'Set form parameters provide valid POP3 connection!'
              var tagid = ['#istatus', '#estatus'];

              if (data.result != "OK") {
                result = data.result;
                tagid = ['#estatus', '#istatus'];
              }
              $(tagid[0]).css({'display':'block'});
              $(tagid[0]).html(result);
              $(tagid[1]).css({'display':'none'});
        });

        return false;
    });
});
