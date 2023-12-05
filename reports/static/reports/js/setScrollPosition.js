document.addEventListener("DOMContentLoaded", function() {
    window.onload = function () {
        let scrollPos = localStorage.getItem('scrollPos');

        document.getElementById('productsContainer').scrollTop = scrollPos || 0;
        document.getElementById('productsContainer').onscroll = function () {
            localStorage.setItem('scrollPos', this.scrollTop);
        };
    }
})