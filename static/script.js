document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".insert-close").addEventListener("click", function() {
        document.querySelector("#insert-modal").classList.remove("show");
        document.querySelector(".modal-backdrop").classList.remove("show");
    })

    // book_form = document.getElementById('book-form');
    // book_form.onsubmit = function() {
    //     book_form.reset();
    // }
    //
    // series_form = document.getElementById('series-form');
    // series_form.onsubmit = function() {
    //     series_form.reset();
    // }

})
// Change login modal
let modal = document.querySelector("#modal-template");

// To login
function login() {
    fetch('login')
        .then(response => response.text())
        .then(text => document.querySelector("#modal-template").innerHTML = text);
}

// To register
function register() {
    fetch('register')
        .then(response => response.text())
        .then(text => document.querySelector("#modal-template").innerHTML = text);
}

function forgot() {
    fetch('forgot')
        .then(response => response.text())
        .then(text => document.querySelector("#modal-template").innerHTML = text);
}

function reset_code() {
    fetch('reset-code')
        .then(response => response.text())
        .then(text => document.querySelector("#modal-template").innerHTML = text);
}

function reset_pass() {
    fetch('reset-pass')
        .then(response => response.text())
        .then(text => document.querySelector("#modal-template").innerHTML = text);
}
