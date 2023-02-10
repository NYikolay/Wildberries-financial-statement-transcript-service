document.addEventListener("DOMContentLoaded", function() {
    const inputs = document.querySelectorAll('.report_input-item')
    const clear_button = document.getElementById('clear_data_id')

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

    clear_button.addEventListener('click', function(event) {
        inputs.forEach(input => {
            input.value = ""
            input.style.border = '1px solid #ff8364'
        });
    })
});
