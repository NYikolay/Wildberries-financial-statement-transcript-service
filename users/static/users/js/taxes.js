document.addEventListener("DOMContentLoaded", function () {
    const addTaxRateButton = document.getElementById('add-tax-rate')
    const addTaxRateForm = document.getElementById('add-tax-rate-from')
    const closeTaxFormButton = document.getElementById('close-tax-form')
    const changeTaxRateButtons = document.querySelectorAll('#change-tax')
    const changeTaxRateFormWrappers = document.querySelectorAll('#change-tax-rate-form-wrapper')

    const dateInputs = document.querySelectorAll('#commencement_date')
    const taxRateInputs = document.querySelectorAll('#tax_rate')

    function setMaxAndMinValuesToDateInput() {
        for (let i = 0; i < dateInputs.length; i++) {
            dateInputs[i].max = new Date().toLocaleDateString('fr-ca')

            if (i !== 0) {
                const pastDateValue = dateInputs[i - 1].valueAsDate
                pastDateValue.setDate(pastDateValue.getDate() + 1)
                dateInputs[i].min = pastDateValue.toLocaleDateString('fr-ca')

            }
        }
    }

    const hideCreateTaxForm = () => {
        if (addTaxRateButton) {
            addTaxRateForm.classList.add("hidden")
            addTaxRateButton.classList.remove("hidden")
        }
    }

    const openCreateTaxForm = () => {
        if (addTaxRateButton) {
            addTaxRateForm.classList.remove("hidden")
            addTaxRateButton.classList.add("hidden")
        }
    }

    // handle change tax form click
    changeTaxRateButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            const taxId = button.getAttribute("data-tax-id")
            const form = document.querySelector("[data-tax-id-form='" + taxId + "']")

            if (form.classList.contains("hidden")) {
                form.classList.remove("hidden")
            } else if (!form.classList.contains("hidden")) {
                form.classList.add("hidden")
            }

            hideCreateTaxForm()
        })
    })

    if (addTaxRateButton) {
        addTaxRateButton.addEventListener("click", (event) => {
            openCreateTaxForm()

            // Close all tax change forms
            changeTaxRateFormWrappers.forEach((wrapper) => {
                wrapper.classList.add("hidden")
            })
        })
    }

    closeTaxFormButton.addEventListener("click", (event) => {
        hideCreateTaxForm()
    })

    setMaxAndMinValuesToDateInput()
})