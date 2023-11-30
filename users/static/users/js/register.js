document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById('register-form')
    const emailItem = document.getElementById('email-item')
    const emailInput = document.getElementById('email')
    const password1Input = document.getElementById('password1')
    const password1Item = document.getElementById('password1-item')
    const password2Input = document.getElementById('password2')
    const password2Item = document.getElementById('password2-item')
    let phoneInput = document.getElementById('phone')

    const formIsValid = () => {
        if (!emailInput.value) {
            emailItem.classList.add("input__item-error")
            return false
        }

        if (!password1Input.value) {
            password1Item.classList.add("input__item-error")
            return false
        }

        if (!password2Input.value) {
            password2Item.classList.add("input__item-error")
            return false
        }

        return true
    }

    registerForm.addEventListener("submit", (event) => {
        event.preventDefault()

        if (formIsValid()) {
            registerForm.submit()
        }
    })

    let getInputNumbersValue = function (input) {
        return input.value.replace(/\D/g, '');
    }

    let onPhonePaste = function (e) {
        let input = e.target,
            inputNumbersValue = getInputNumbersValue(input);
        let pasted = e.clipboardData || window.clipboardData;
        if (pasted) {
            let pastedText = pasted.getData('Text');
            if (/\D/g.test(pastedText)) {
                input.value = inputNumbersValue;
            }
        }
    }

    let onPhoneInput = function (e) {
        let input = e.target,
            inputNumbersValue = getInputNumbersValue(input),
            selectionStart = input.selectionStart,
            formattedInputValue = "";

        if (!inputNumbersValue) {
            return input.value = "";
        }

        if (input.value.length !== selectionStart) {
            if (e.data && /\D/g.test(e.data)) {
                input.value = inputNumbersValue;
            }
            return;
        }

        if (["7", "8", "9"].indexOf(inputNumbersValue[0]) > -1) {
            if (inputNumbersValue[0] === "9") inputNumbersValue = "7" + inputNumbersValue;
            let firstSymbols = (inputNumbersValue[0] === "8") ? "+8" : "+7";
            formattedInputValue = input.value = firstSymbols + " ";
            if (inputNumbersValue.length > 1) {
                formattedInputValue += '(' + inputNumbersValue.substring(1, 4);
            }
            if (inputNumbersValue.length >= 5) {
                formattedInputValue += ') ' + inputNumbersValue.substring(4, 7);
            }
            if (inputNumbersValue.length >= 8) {
                formattedInputValue += '-' + inputNumbersValue.substring(7, 9);
            }
            if (inputNumbersValue.length >= 10) {
                formattedInputValue += '-' + inputNumbersValue.substring(9, 11);
            }
        } else {
            formattedInputValue = '+' + inputNumbersValue.substring(0, 16);
        }
        input.value = formattedInputValue;
    }
    let onPhoneKeyDown = function (e) {
        // Clear input after remove last symbol
        let inputValue = e.target.value.replace(/\D/g, '');
        if (e.keyCode === 8 && inputValue.length === 1) {
            e.target.value = "";
        }
    }

    phoneInput.addEventListener('keydown', onPhoneKeyDown);
    phoneInput.addEventListener('input', onPhoneInput, false);
    phoneInput.addEventListener('paste', onPhonePaste, false);
})