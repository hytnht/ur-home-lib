document.addEventListener("DOMContentLoaded", function () {
    document.querySelector(".insert-close").addEventListener("click", function() {
        document.querySelector("#insert-modal").classList.remove("show");
        document.querySelector(".modal-backdrop").classList.remove("show");
    })
})
let showMode = 'table-cell';
function toggleCol(btn){

    // First isolate the checkbox by name using the
    // name of the form and the name of the checkbox

    btn   = document.forms['toggle-column'].elements[btn];

    // Next find all the table cells by using the DOM function
    // getElementsByName passing in the constructed name of
    // the cells, derived from the checkbox name

    let cells = document.getElementsByName('t'+btn.name);

    // Once the cells and checkbox object has been retrieved
    // the show hide choice is simply whether the checkbox is
    // checked or clear

    let mode = btn.checked ? showMode : 'none';

    // Apply the style to the CSS display property for the cells

    for(let j = 0; j < cells.length; j++) cells[j].style.display = mode;
}


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

// To forgot password
function forgot() {
    fetch('forgot')
        .then(response => response.text())
        .then(text => document.querySelector("#modal-template").innerHTML = text);
}

// To reset code submit
function reset_code() {
    fetch('reset-code')
        .then(response => response.text())
        .then(text => document.querySelector("#modal-template").innerHTML = text);
}

// To change password
function reset_pass() {
    fetch('reset-pass')
        .then(response => response.text())
        .then(text => document.querySelector("#modal-template").innerHTML = text);
}
