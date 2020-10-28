document.getElementById('toggle').addEventListener('click', () => {
    let navbar = document.getElementById("navbar");
    if (navbar.className === "nav-list") {
        navbar.className += " display-menu";
    }
    else {
        navbar.className = "nav-list";
    }
});