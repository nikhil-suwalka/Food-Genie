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

function fetch(tags_json, allowed_list_json, value){
    $.ajax({
            type: "POST",
            url: "/fetch/",
            dataType: "json",
            data: {"tags": tags_json, "allowed_list": allowed_list_json, "calorie_slider": value},
            headers: {"X-CSRFToken": cookies["csrftoken"]},

            success:
                function (data) {
                    var recipes = data.recipes;

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

function process() {
    var tags_json = JSON.stringify(tags);
    var allowed_list_json = JSON.stringify(allowed_list);
    value = $('.range-slider__range').val()
    if(tags.length === 0){
        //random
       $.ajax({
        type: "POST",
        url: "/random/",
        dataType: "json",
         // async: false,
        data: {},
        headers: {"X-CSRFToken": cookies["csrftoken"]},

        success:
            function (data) {
                tags_json = data["data"];
                data = JSON.parse(data["data"]);
                allowed_list_json = [];
                for(var i=0;i<data.length;i++)
                    allowed_list_json.push(1);
                allowed_list_json = JSON.stringify(allowed_list_json);

                $("#loading_text").html("Randomly picking recipes...");
                fetch(tags_json,allowed_list_json,value);
            },
        error:
            function (data) {
                alert("ERROR");
            }

        });
    }else {
        fetch(tags_json,allowed_list_json,value);
    }

}
