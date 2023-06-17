document.addEventListener("DOMContentLoaded", function () {
    const invalidInputs = document.querySelectorAll('.input_error')

    for (let i = 0; i < invalidInputs.length; i++) {
        invalidInputs[i].addEventListener('input', (e) => {
            if (e.target.value !== '') {
                e.target.classList.remove('input_error')
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