document.addEventListener("DOMContentLoaded", function() {
    const openFileLoadFormButton = document.getElementById('open-file-form')
    const isOpacityHideButton = openFileLoadFormButton.getAttribute("data-hide-type") === 'opacity'
    const closeFileLoadFormButton = document.getElementById('close-file-form')
    const fileLoadForm = document.getElementById('file-form')
    const fileLoadInput = document.getElementById('file-input')
    const fileLoadStatusContainer = document.getElementById('file-load-status')

    closeFileLoadFormButton.addEventListener("click", (event) => {
        fileLoadForm.classList.add("hidden")

        if (!isOpacityHideButton) {
            openFileLoadFormButton.classList.remove("hidden")
        } else {
            openFileLoadFormButton.style.opacity = "1"
            openFileLoadFormButton.style.cursor = "pointer"
            openFileLoadFormButton.disabled = false
        }
    })

    openFileLoadFormButton.addEventListener("click", (event) => {
        fileLoadForm.classList.remove("hidden")

        if (!isOpacityHideButton) {
            openFileLoadFormButton.classList.add("hidden")
        } else {
            event.target.style.opacity = "0"
            event.target.disabled = true
            event.target.style.cursor = "default"
        }
    })

    fileLoadInput.addEventListener("change", function (event) {
        const selectedFile = event.target.files[0];

        if (selectedFile) {
            const fileStatusIcon = fileLoadStatusContainer.querySelector('#file-load-icon')
            const fileStatusText = fileLoadStatusContainer.querySelector('#file-load-text')

            fileStatusIcon.classList.remove('error__dot-icon')
            fileStatusIcon.classList.add('success__dot-icon')
            fileStatusText.innerHTML = 'Файл выбран'

        }
    });
});
