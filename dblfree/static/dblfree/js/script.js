function toggleNavbar() {
    let navbar = document.getElementById("navbar");
    if (navbar.className === "nav-list") {
        navbar.className += " display-menu";
    }
    else {
        navbar.className = "nav-list";
    }
}