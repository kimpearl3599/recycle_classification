$(document).ready(function () {
    $('.item1').addClass('active')
    $('#tap1').show()
})

function openItem(evt, itemName) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(itemName).style.display = "block";
    evt.currentTarget.className += " active";
}


function go_pic() {
    window.location.href = '/'
}

function go_review() {
    window.location.href = '/review'
}

function go_crwaling() {
    window.location.href = '/search'
}

function go_category() {
    window.location.href = '/category'
}