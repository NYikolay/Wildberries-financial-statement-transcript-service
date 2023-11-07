document.addEventListener("DOMContentLoaded", function() {
    const openFileLoadFormButton = document.getElementById('open-file-form')
    const closeFileLoadFormButton = document.getElementById('net-costs-close-form')
    const fileLoadForm = document.getElementById('net-costs-form')
    const fileLoadInput = document.getElementById('net-costs-file')
    const fileLoadStatusContainer = document.querySelector('.common__load-status')

    closeFileLoadFormButton.addEventListener("click", (event) => {
        fileLoadForm.classList.add("hidden")
        openFileLoadFormButton.style.opacity = "1"
        openFileLoadFormButton.style.cursor = "pointer"
        openFileLoadFormButton.disabled = false
    })

    openFileLoadFormButton.addEventListener("click", (event) => {
        event.target.style.opacity = "0"
        event.target.disabled = true
        event.target.style.cursor = "default"

        fileLoadForm.classList.remove("hidden")
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