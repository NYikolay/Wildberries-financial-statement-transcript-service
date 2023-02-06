paginatorInput = document.getElementsByClassName('paginator_input')

function generateInputValidationForPaginator() {

    paginatorInput[0].addEventListener('input', function () {

        if (this.value > parseInt(this.attributes[2].value)) {
            this.value = parseInt(this.attributes[2].value)
        }
        if (this.value < 0) {
            this.value = parseInt(this.attributes[2].value)
        }
    })

    paginatorInput[0].addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            window.location = window.location.origin + window.location.pathname + `?page=${this.value}`
        }
    })
}