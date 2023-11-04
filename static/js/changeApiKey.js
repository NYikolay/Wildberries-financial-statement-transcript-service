document.addEventListener("DOMContentLoaded", function () {
    const currentKeysContainer = document.getElementById('current-keys-container')
    const openChangeKeyModelButton = document.getElementById('open-change-key-modal')
    const cancelChangeKeyButton = document.getElementById('cancel-key-change')
    const changeKeyCheckboxInputs = document.querySelectorAll('.change__key-checkbox__input')

    const handleCheckboxChange = (event) =>  {
        const clickedCheckbox = event.target;

        if (clickedCheckbox.checked) {
            changeKeyCheckboxInputs.forEach((checkbox) => {
                if (checkbox !== clickedCheckbox) {
                    checkbox.checked = false;
                }
            });
        }
    }

    changeKeyCheckboxInputs.forEach((checkbox) => {
        checkbox.addEventListener('change', handleCheckboxChange);
    });

    openChangeKeyModelButton.addEventListener("click", () => {
        currentKeysContainer.classList.remove('hidden')
    })

    cancelChangeKeyButton.addEventListener("click", () => {
        currentKeysContainer.classList.add('hidden')
    })

    document.addEventListener('click', function(event) {
        if (!currentKeysContainer.contains(event.target) && !openChangeKeyModelButton.contains(event.target)) {
            currentKeysContainer.classList.add('hidden')
        }
    });
})