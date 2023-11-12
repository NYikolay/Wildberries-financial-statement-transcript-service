document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll('.form__item')

    for (let i = 0; i < inputs.length; i++) {
        let currentInput = inputs[i].getElementsByTagName('input')[0]

        if (!currentInput) {
            currentInput = inputs[i].getElementsByTagName('textarea')[0]
        }

        currentInput.addEventListener('input', (e) => {
            if (e.target.value !== '' && inputs[i].classList.contains("input__item-error")) {
                inputs[i].classList.remove('input__item-error')

                const divError = document.querySelector(`[data-id-error=${e.target.getAttribute('data-id')}]`)

                if (divError) {
                    divError.classList.add('hidden');

                    divError.addEventListener('transitionend', function() {
                        this.remove();
                    });
                }
            }
        })
    }
})