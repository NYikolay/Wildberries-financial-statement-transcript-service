document.addEventListener("DOMContentLoaded", function() {
    const openCreateNetCostFormButton = document.getElementById('open-create-form')
    const openUpdateNetCostFormButtons = document.querySelectorAll('#open-update-form')

    const createNetCostFormWrapper = document.getElementById('create-net-cost-from-wrapper')
    const closeCreateNetCostFormButton = document.getElementById('close-net-cost-form')
    const amountInputs = document.querySelectorAll('#amount')

    const dateInputs = document.querySelectorAll('#cost_date')

    let lastOpenedItem

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

    amountInputs.forEach((input) => {
        input.addEventListener("input", () => {
            let value = input.value;
            const regex = /^(\d{0,11}(\.\d{0,2})?|\.\d{0,2})?$/;

            if (!regex.test(value)) {
                value = value.slice(0, -1);
                input.value = value;
            }
        })
    })

    const hideLastOpenedItem = () => {
        if (!lastOpenedItem) return
        if (lastOpenedItem === openCreateNetCostFormButton ) {
            openCreateNetCostFormButton.classList.remove("hidden")
            createNetCostFormWrapper.classList.add("hidden")
            return;
        }

        const netCostId = lastOpenedItem.getAttribute("data-net-cost-id")
        const form = document.querySelector("[data-net-cost-id-form='" + netCostId + "']")

        form.classList.add("hidden")
    }

    openCreateNetCostFormButton.addEventListener("click", (event) => {
        hideLastOpenedItem()
        lastOpenedItem = openCreateNetCostFormButton

        openCreateNetCostFormButton.classList.add("hidden")
        createNetCostFormWrapper.classList.remove("hidden")
    })

    closeCreateNetCostFormButton.addEventListener("click", (event) => {
        openCreateNetCostFormButton.classList.remove("hidden")
        createNetCostFormWrapper.classList.add("hidden")
    })

    openUpdateNetCostFormButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            hideLastOpenedItem()
            lastOpenedItem = button

            const netCostId = button.getAttribute("data-net-cost-id")
            const formWrapper = document.querySelector("[data-net-cost-id-form='" + netCostId + "']")
            const closeFormWrapperButton = formWrapper.querySelector('#close-update-form')

            formWrapper.classList.remove("hidden")

            closeFormWrapperButton.addEventListener("click", (event) => {
                formWrapper.classList.add("hidden")
            })
        })
    })

    setMaxAndMinValuesToDateInput()
});