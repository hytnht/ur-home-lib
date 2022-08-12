// document.addEventListener("DOMContentLoaded", function () {
//     document.querySelector(".insert-close").addEventListener("click", function() {
//         document.querySelector("#insert-modal").classList.remove("show");
//         document.querySelector(".modal-backdrop").classList.remove("show");
//     })
// })

// Select all checkboxes which classes included 'c' + checkbox's name
function checkAll(box) {
    col = document.getElementsByClassName('c-'+box.name)
    for (let i = 0; i < col.length; i++)
        col[i].checked = box.checked
}

// Checkbox toggle column which name = checkbox's name omitted the starting 'b'
function toggle(box_name,mode) {
    let box = document.getElementsByName(box_name)[0];
    let col = document.getElementsByName(box_name.substring(1))
    if (box.checked)
        for (let i = 0; i < col.length; i++)
            col[i].style.display = mode
    else
        for (let i = 0; i < col.length; i++)
            col[i].style.display = 'none'

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
