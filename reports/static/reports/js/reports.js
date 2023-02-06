document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll('.report_input-item')
    const clear_button = document.getElementById('clear_data_id')

    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].value === '') {
            inputs[i].style.border = '1px solid #ff8364'
        }
    }

    for (let i = 0; i < inputs.length; i++) {
        inputs[i].addEventListener('input', function (event) {
            if (event.target.value === '') {
                event.target.style.border = '1px solid #ff8364'
            } else {
                event.target.style.border = '1px solid #dbdbdb'
            }
        })
    }

    clear_button.addEventListener('click', function (event) {
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].value = ""
            inputs[i].style.border = '1px solid #ff8364'
        }
    })
})
