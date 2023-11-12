document.addEventListener("DOMContentLoaded", function () {
    const addTaxRateButton = document.getElementById('open-create-form')
    const addTaxRateForm = document.getElementById('add-tax-rate-from')
    const closeTaxFormButton = document.getElementById('close-tax-form')
    const changeTaxRateButtons = document.querySelectorAll('#open-change-form')
    const taxInputs = document.querySelectorAll('#tax_rate')
    let lastOpenedItem

    const dateInputs = document.querySelectorAll('#commencement_date')

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

    taxInputs.forEach((input) => {
        input.addEventListener("input", (event) => {
            let value = input.value;
            const regex = /^(\d{0,2}(\.\d{0,2})?|\.\d{0,2})?$/;

            if (!regex.test(value)) {
                value = value.slice(0, -1);
                input.value = value;
            }
        })
    })

    const hideLastOpenedItem = () => {
        if (!lastOpenedItem) return
        if (lastOpenedItem === addTaxRateButton ) return hideCreateTaxForm()

        const taxId = lastOpenedItem.getAttribute("data-tax-id")
        const form = document.querySelector("[data-tax-id-form='" + taxId + "']")

        form.classList.add("hidden")
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

    changeTaxRateButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            hideLastOpenedItem()
            lastOpenedItem = button

            const taxId = button.getAttribute("data-tax-id")
            const formWrapper = document.querySelector("[data-tax-id-form='" + taxId + "']")
            const closeFormWrapperButton = formWrapper.querySelector('#close-update-form')

            formWrapper.classList.remove("hidden")

            closeFormWrapperButton.addEventListener("click", (event) => {
                formWrapper.classList.add("hidden")
                button.classList.remove("hidden")
            })
        })
    })

    if (addTaxRateButton) {
        addTaxRateButton.addEventListener("click", (event) => {
            hideLastOpenedItem()
            lastOpenedItem = addTaxRateButton

            openCreateTaxForm()
        })
    }

    closeTaxFormButton.addEventListener("click", (event) => {
        hideCreateTaxForm()
    })

    setMaxAndMinValuesToDateInput()
})