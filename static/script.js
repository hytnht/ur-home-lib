// Sort columns
function sort(column) {
    let table = document.getElementById("table-display");
    let direction = "asc";
    let i, x, y, reverse, count = 0;
    let swap = true
    while (swap) {
        swap = false;
        let rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            x = rows[i].getElementsByTagName("td")[column];
            y = rows[i + 1].getElementsByTagName("td")[column];
            if (direction === "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    reverse = true;
                    break;
                }
            } else {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    reverse = true;
                    break;
                }
            }
        }
        if (reverse) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            swap = true;
            count++;
        } else if (count === 0 && direction === "asc") {
            direction = "desc";
            swap = true;
        }
    }
}

// Select all checkboxes which classes included 'c' (check) + checkbox's name
function checkAll(box, toggleMode) {
    let col = document.getElementsByClassName('c-' + box.name)
    for (let i = 0; i < col.length; i++) {
        col[i].checked = box.checked
        if (toggleMode) {
            toggle(col[i].getAttribute("name"), toggleMode)
        }
    }
}

// Checkbox toggle column which name = checkbox's name omitted the starting 'b' (button)
function toggle(boxName, mode) {
    let box = document.getElementsByName(boxName)[0];
    let col = document.getElementsByName(boxName.substring(1))
    if (box.checked)
        for (let i = 0; i < col.length; i++)
            col[i].style.display = mode
    else
        for (let i = 0; i < col.length; i++)
            col[i].style.display = 'none'

}

// Change login modal to login
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


