document.addEventListener("DOMContentLoaded", function () {
    const resetPasswordForm = document.getElementById('reset-password-form')
    const emailItem = document.getElementById('email-item')
    const emailInput = document.getElementById('email')

    const formIsValid = () => {
        if (!emailInput.value) {
            emailItem.classList.add("input__item-error")
            return false
        }

        return true
    }

    resetPasswordForm.addEventListener("submit", (event) => {
        event.preventDefault()

        if (formIsValid()) {
            resetPasswordForm.submit()
        }
    })
})