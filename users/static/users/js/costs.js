document.addEventListener("DOMContentLoaded", function () {
    const createCostsButtons = document.querySelectorAll('#add-costs-button')
    const changeCostsButtons = document.querySelectorAll('#change-costs-button')

    changeCostsButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            const costsId = button.getAttribute("data-costs-id")
            const form = document.querySelector("[data-change-costs-id-form='" + costsId + "']")
            const costsText = document.querySelector("[data-change-costs-id-text='" + costsId + "']")

            form.classList.remove("hidden")
            button.classList.add("hidden")
            costsText.classList.add("hidden")
        })
    })

    createCostsButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            const costsId = button.getAttribute("data-costs-id")
            const form = document.querySelector("[data-costs-id-form='" + costsId + "']")

            form.classList.remove("hidden")
            button.classList.add("hidden")
        })
    })
})