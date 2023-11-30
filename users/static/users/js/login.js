document.addEventListener("DOMContentLoaded", function () {
    const emailItem = document.getElementById('email-item')
    const emailInput = document.getElementById('email')
    const passwordInput = document.getElementById('password')
    const passwordItem = document.getElementById('password-item')
    const loginForm = document.getElementById('login-form')

    const formIsValid = () => {
        if (!emailInput.value) {
            emailItem.classList.add("input__item-error")
            return false
        }

        if (!passwordInput.value) {
            passwordItem.classList.add("input__item-error")
            return false
        }

        return true
    }

    loginForm.addEventListener("submit", (event) => {
        event.preventDefault()

        if (formIsValid()) {
            loginForm.submit()
        }
    })
})