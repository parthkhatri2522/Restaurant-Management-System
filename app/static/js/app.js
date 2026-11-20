document.addEventListener("DOMContentLoaded", function () {

    // Display the current year in the footer.
    const yearElement = document.getElementById("current-year");

    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }

});