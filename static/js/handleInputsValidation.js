document.addEventListener("DOMContentLoaded", function () {
    const invalidInputs = document.querySelectorAll('.input__item-error')

    for (let i = 0; i < invalidInputs.length; i++) {
        let currentInput = invalidInputs[i].getElementsByTagName('input')[0]

        if (!currentInput) {
            currentInput = invalidInputs[i].getElementsByTagName('textarea')[0]
        }

        currentInput.addEventListener('input', (e) => {
            if (e.target.value !== '') {
                invalidInputs[i].classList.remove('input__item-error')

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