cookies = document.cookie.split(';').reduce((cookies, cookie) => {
    const [name, value] = cookie.split('=').map(c => c.trim());
    cookies[name] = value;
    return cookies;
}, {});


// Post to the provided URL with the specified parameters.
function post(path, parameters) {
    var form = $('<form></form>');
    form.innerHTML = '<input type="hidden" name="csrfmiddlewaretoken" value=" ' + cookies["csrftoken"] + '">'
    form.attr("method", "post");
    form.attr("action", path);

    $.each(parameters, function (key, value) {
        var field = $('<input></input>');

        field.attr("type", "hidden");
        field.attr("name", key);
        field.attr("value", value);

        form.append(field);
    });

    // The form needs to be a part of the document in
    // order for us to be able to submit it.
    $(document.body).append(form);
    form.submit();
}

function process() {


    var tags_json = JSON.stringify(tags);
    var allowed_list_json = JSON.stringify(allowed_list);

    $.ajax({
        type: "POST",
        url: "/fetch/",
        dataType: "json",
        data: {"tags": tags_json, "allowed_list": allowed_list_json},
        headers: {"X-CSRFToken": cookies["csrftoken"]},

        success:
            function (data) {
                var recipes = data.recipes;
                console.log(recipes);

                var form = $("#dataform");
                $('#rec').val(JSON.stringify(recipes));
                form.submit();

            },
        error:
            function (data) {
                alert("ERROR");
            }

    });

}
