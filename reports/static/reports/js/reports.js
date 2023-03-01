document.addEventListener("DOMContentLoaded", function() {
    window.onload = function() {
        let scrollPos = localStorage.getItem('scrollPos');

        document.getElementById('reports-left-filters').scrollTop = scrollPos || 0 ;
        document.getElementById('reports-left-filters').onscroll = function () {
            localStorage.setItem('scrollPos', this.scrollTop);
        };
    }
    const inputs = document.querySelectorAll('.report_input-item')
    const clearButton = document.getElementById('clear_data_id')

    inputs.forEach(input => {
        if (input.value === '') {
            input.style.border = '1px solid #ff8364'
        }

        input.addEventListener('input', function(event) {
            if (event.target.value === '') {
                event.target.style.border = '1px solid #ff8364'
            } else {
                event.target.style.border = '1px solid #dbdbdb'
            }
        })
    });

    clearButton.addEventListener('click', function(event) {
        inputs.forEach(input => {
            input.value = ""
            input.style.border = '1px solid #ff8364'
        });
    })
});
