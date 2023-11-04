document.addEventListener("DOMContentLoaded", function () {
    const addTaxRateButton = document.getElementById('add-tax-rate')
    const addTaxRateForm = document.getElementById('add-tax-rate-from')
    const closeTaxFormButton = document.getElementById('close-tax-form')
    const changeTaxRateButtons = document.querySelectorAll('#change-tax')
    const changeTaxRateForms = document.querySelectorAll('#change-tax-rate-from')

    changeTaxRateButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            const taxId = button.getAttribute("data-tax-id")

            const form = document.querySelector("[data-tax-id-form='" + taxId + "']");

            if (form) {
                form.classList.remove("hidden")
            }
        })
    })

    addTaxRateButton.addEventListener("click", (event) => {
        addTaxRateForm.classList.remove("hidden")
        addTaxRateButton.classList.add("hidden")
    })

    closeTaxFormButton.addEventListener("click", (event) => {
        addTaxRateForm.classList.add("hidden")
        addTaxRateButton.classList.remove("hidden")
    })
})