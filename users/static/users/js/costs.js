document.addEventListener("DOMContentLoaded", function () {
    const createCostsButtons = document.querySelectorAll('#open-create-form')
    const changeCostsButtons = document.querySelectorAll('#open-change-form')
    const costsInputs = document.querySelectorAll('#supplier_costs')
    let lastOpenedItem

    costsInputs.forEach((input) => {
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

        const costsId = lastOpenedItem.getAttribute("data-item-id")
        const formWrapper = document.querySelector("[data-item-id-form='" + costsId + "']")
        const costsText = document.querySelector("[data-change-costs-id-text='" + costsId + "']")

        formWrapper.classList.add("hidden")
        lastOpenedItem.classList.remove("hidden")
        if (costsText) costsText.classList.remove("hidden")
    }

    changeCostsButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            hideLastOpenedItem()
            lastOpenedItem = button

            const costsId = button.getAttribute("data-item-id")
            const formWrapper = document.querySelector("[data-item-id-form='" + costsId + "']")
            const costsText = document.querySelector("[data-change-costs-id-text='" + costsId + "']")
            const closeFormWrapperButton = formWrapper.querySelector('#close-update-form')

            formWrapper.classList.remove("hidden")
            button.classList.add("hidden")
            costsText.classList.add("hidden")

            closeFormWrapperButton.addEventListener("click", (event) => {
                formWrapper.classList.add("hidden")
                button.classList.remove("hidden")
                costsText.classList.remove("hidden")
            })
        })
    })

    createCostsButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            hideLastOpenedItem()
            lastOpenedItem = button

            const costsId = button.getAttribute("data-item-id")
            const formWrapper = document.querySelector("[data-item-id-form='" + costsId + "']")
            const closeFormWrapperButton = formWrapper.querySelector('#close-create-form')

            formWrapper.classList.remove("hidden")
            button.classList.add("hidden")

            closeFormWrapperButton.addEventListener("click", (event) => {
                formWrapper.classList.add("hidden")
                button.classList.remove("hidden")
            })
        })
    })
})