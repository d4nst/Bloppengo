
function delete_article(data) {
    if (data.msg === "success") {
        $("#article-" + data.article_id).remove()
    } else {
        alert(data.msg);
    }
};

function save_article(data) {

    if (data.msg === "success") {
        if ($("#section-header").html() == "My Saved Articles") {
            $("#article-" + data.article_id).remove()
        } else {
            $("#article-" + data.article_id + " .glyphicon-bookmark").toggleClass("icon-green")
        }
    } else {
        alert(data.msg);
    }
};

function favourite_article(data) {
    if (data.msg === "success") {
        if ($("#section-header").html() == "My Favourite Articles") {
            $("#article-" + data.article_id).remove()
        } else {
            $("#article-" + data.article_id + " .glyphicon-star").toggleClass("icon-yellow")
        }
    } else {
        alert(data.msg);
    }
};

function delete_user(data) {
    if (data.msg === "success") {
        $("#row-" + data.user_id).remove()
    } else {
        alert(data.msg);
    }
};


function toggle_checkbox(data) {
    if (data.msg === "success") {
        if ($("#row-" + data.user_id + " #checkbox-" + data.role).prop('checked') == true) {
            $("#row-" + data.user_id + " #checkbox-" + data.role).prop('checked', false);
        } else {
            $("#row-" + data.user_id + " #checkbox-" + data.role).prop('checked', true);
        }
    } else {
        alert(data.msg);
    }
};