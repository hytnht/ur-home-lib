// Initialize tooltips
$(document).ready(function () { $('[data-bs-toggle=tooltip]').tooltip();});

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
function check_all(box, toggleMode, tableHide) {
    let col = document.getElementsByClassName('c-' + box.name)
    for (let i = 0; i < col.length; i++) {
        col[i].checked = box.checked
        if (toggleMode) {
            toggle(col[i].getAttribute("name"), toggleMode)
        }
    }
    if (tableHide) {
        if (box.checked == false)
            document.getElementById("table-display").style.display = 'none'
        else
            document.getElementById("table-display").style.display = 'table'
    }
}

// Checkbox toggle column which name = checkbox's name omitted the starting 'b' (button)
function toggle(boxName, mode) {
    let box = document.getElementsByName(boxName)[0];
    let col = document.getElementsByName(boxName.substring(1))
    if (box.checked) {
        document.getElementById("table-display").style.display = 'table'
        for (let i = 0; i < col.length; i++)
            col[i].style.display = mode
    }
    else
        for (let i = 0; i < col.length; i++)
            col[i].style.display = 'none'
}

// Edit data modal
function edit(id) {
    current =  window.location.href.split('?')[0].split('#')[0]
    console.log(id)
    return window.location.replace(current + "/edit?id=" + id)
}

//<editor-fold desc="Login modal">
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
//</editor-fold>


//<editor-fold desc="Calendar
// Change calendar display
function display_mode() {
    let mode = document.getElementById("display-content").getAttribute("mode");
    if (mode === "calendar") {
        window.location.replace('/calendar?display=table');
    } else {
        window.location.replace('/calendar?display=calendar');
    }
}
document.addEventListener("DOMContentLoaded", function () {
    let mode = document.getElementById("display-content").getAttribute("mode");
    let button = document.getElementById("display-button");
    let deleteBtn = document.getElementById("delete-button");
    if (mode === "calendar") {
        button.innerHTML = '<i class="fa-solid fa-calendar-check"></i>';
        deleteBtn.style.display = "none";
    } else {
        button.innerHTML = '<i class="fa-solid fa-table"></i>';
        deleteBtn.style.display = "inline-block";
    }
})

/* This calendar is based on tutorial:
   How to Make a Monthly Calendar With Real Data by Mateusz Rybczonek
   https://css-tricks.com/how-to-make-a-monthly-calendar-with-real-data/"> */
dayjs.extend(window.dayjs_plugin_weekday)
dayjs.extend(window.dayjs_plugin_weekOfYear);
const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const TODAY = dayjs().format("YYYY-MM-DD");
const INITIAL_YEAR = dayjs().format("YYYY");
const INITIAL_MONTH = dayjs().format("M");
let showMonth = dayjs(new Date(INITIAL_YEAR, INITIAL_MONTH - 1, 1));
let currentList, preList, nextList;

function display_calendar() {
    WEEKDAYS.forEach((weekday) => {
        let headCell = document.createElement("li");
        headCell.innerText = weekday;
        document.getElementById("calendar-header").appendChild(headCell);
    });

    calendar();
    switch_month();
}

function calendar(year = INITIAL_YEAR, month = INITIAL_MONTH) {
    let body = document.getElementById("calendar-body");
    document.getElementById("current-month").innerText = dayjs(new Date(year, month - 1)).format("MMMM YYYY");

    while (body.firstElementChild) {
        body.firstElementChild.remove();
    }

    currentList = current_list(year, month, dayjs(`${year}-${month}-01`).daysInMonth());
    preList = previous_list(year, month);
    nextList = next_list(year, month);

    [...preList, ...currentList, ...nextList].forEach((day) => {
        append_cell(day, body);
    });
}

function append_cell(day, body) {
    let bodyCell = document.createElement("li");
    bodyCell.classList.add("calendar-cell");
    let dayNo = document.createElement("span");
    dayNo.innerText = day.number;
    let data = document.createElement("div")
    let id = showMonth.format("YYYY-MM") + "-" + String(day.number).padStart(2, "0");
    data.setAttribute("id", id)
    bodyCell.appendChild(data);
    bodyCell.appendChild(dayNo);
    body.appendChild(bodyCell);

    if (!day.current) {
        bodyCell.classList.add("other-day");
    }
    if (day.date === TODAY) {
        bodyCell.classList.add("today");
    }
}

function calendar_data(data) {
    let objects = JSON.parse(data);
    for (let obj of objects) {
        let element = document.getElementById(obj.date);
        let series = document.createElement("div");
        series.setAttribute("data-bs-toggle", "tooltip");
        series.setAttribute("data-bs-placement", "right");
        series.setAttribute("title", obj.title);
        series.innerText = obj.title;
        element.appendChild(series);
    }
}

function current_list(year, month) {
    return [...Array(dayjs(`${year}-${month}-01`).daysInMonth())].map((day, index) => {
        return {
            date: dayjs(`${year}-${month}-${index + 1}`).format("YYYY-MM-DD"),
            number: index + 1,
            current: true
        };
    });
}

function previous_list(year, month) {
    let firstWeekday = dayjs(currentList[0].date).weekday();
    let preMonth = dayjs(`${year}-${month}-01`).subtract(1, "month");
    let preVisible = 6
    if (firstWeekday) {
        preVisible = firstWeekday - 1
    }
    let preLastMon = dayjs(currentList[0].date).subtract(preVisible, "day").date();
    return [...Array(preVisible)].map((day, index) => {
        return {
            date: dayjs(`${preMonth.year()}-${preMonth.month() + 1}-${preLastMon + index}`).format("YYYY-MM-DD"),
            number: preLastMon + index,
            current: false
        };
    });
}

function next_list(year, month) {
    let lastWeekday = dayjs(`${year}-${month}-${currentList.length}`).weekday()
    let nextMonth = dayjs(`${year}-${month}-01`).add(1, "month");
    let nextVisible = lastWeekday
    if (lastWeekday) {
        nextVisible = 7 - lastWeekday
    }
    return [...Array(nextVisible)].map((day, index) => {
        return {
            date: dayjs(`${nextMonth.year()}-${nextMonth.month() + 1}-${index + 1}`).format("YYYY-MM-DD"),
            number: index + 1,
            current: false
        };
    });
}

function switch_month() {
    document.getElementById("pre-month").addEventListener("click", function () {
        showMonth = dayjs(showMonth).subtract(1, "month");
        calendar(showMonth.format("YYYY"), showMonth.format("M"));
    });

    document.getElementById("this-month").addEventListener("click", function () {
        showMonth = dayjs(new Date(INITIAL_YEAR, INITIAL_MONTH - 1, 1));
        calendar(showMonth.format("YYYY"), showMonth.format("M"));
    });

    document.getElementById("next-month").addEventListener("click", function () {
        showMonth = dayjs(showMonth).add(1, "month");
        calendar(showMonth.format("YYYY"), showMonth.format("M"));
    });
}

//</editor-fold>

