document.addEventListener("DOMContentLoaded", function() {
    const openCreateNetCostFormButton = document.getElementById('open-net-cost-form')
    const openUpdateNetCostFormButtons = document.querySelectorAll('#open-update-net-cost-button')
    const createNetCostFormWrapper = document.getElementById('create-net-cost-from-wrapper')
    const closeCreateNetCostFormButton = document.getElementById('close-net-cost-form')
    const updateNetCostFormWrapper = document.querySelectorAll('#update-net-cost-from-wrapper')
    const dateInputs = document.querySelectorAll('#cost_date')

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

    const closeAllUpdateFormsExceptCurrent = (currentCostId) => {
        updateNetCostFormWrapper.forEach((wrapper) => {
            const wrapperCostId = wrapper.getAttribute("data-net-cost-id-form")

            if (wrapperCostId !== currentCostId) {
                wrapper.classList.add("hidden")
            }
        })
    }

    openCreateNetCostFormButton.addEventListener("click", (event) => {
        openCreateNetCostFormButton.classList.add("hidden")
        createNetCostFormWrapper.classList.remove("hidden")

        // Close all tax change forms
        updateNetCostFormWrapper.forEach((wrapper) => {
            wrapper.classList.add("hidden")
        })
    })

    closeCreateNetCostFormButton.addEventListener("click", (event) => {
        openCreateNetCostFormButton.classList.remove("hidden")
        createNetCostFormWrapper.classList.add("hidden")
    })

    openUpdateNetCostFormButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            const netCostId = button.getAttribute("data-net-cost-id")
            const form = document.querySelector("[data-net-cost-id-form='" + netCostId + "']")

            closeAllUpdateFormsExceptCurrent(netCostId)

            if (form.classList.contains("hidden")) {
                form.classList.remove("hidden")
            } else if (!form.classList.contains("hidden")) {
                form.classList.add("hidden")
            }
        })
    })

    setMaxAndMinValuesToDateInput()
});