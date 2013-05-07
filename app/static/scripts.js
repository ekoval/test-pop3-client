// Post to the provided URL with the specified parameters.
function post(path, user, host) {
    var form = $('<form></form>');
    var field = $('<input></input>');

    form.attr("method", "post");
    form.attr("action", path);

    field.attr("type", "hidden");
    field.attr("name", "account");
    field.attr("value", user);
    form.append(field);

    field = $('<input></input>');
    field.attr("type", "hidden");
    field.attr("name", "hostname");
    field.attr("value", host);
    form.append(field);

    // The form needs to be a part of the document in
    // order for us to be able to submit it.
    $(document.body).append(form);
    form.submit();
}
