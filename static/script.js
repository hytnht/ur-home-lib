document.addEventListener("DOMContentLoaded", function () {

        setTimeout(function() {
            $('.alert').fadeOut('slow');
        }, 2000); // <-- time in milliseconds
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


