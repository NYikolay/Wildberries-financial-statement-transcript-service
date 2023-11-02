document.addEventListener("DOMContentLoaded", function() {
    const openFileLoadFormButton = document.getElementById('open-file-form')
    const closeFileLoadFormButton = document.getElementById('reports-expenses-close-form')
    const fileLoadForm = document.getElementById('reports-expenses-form')
    const fileLoadInput = document.getElementById('expenses-file')
    const fileLoadStatusContainer = document.querySelector('.expenses__load-status')

    closeFileLoadFormButton.addEventListener("click", (event) => {
        fileLoadForm.style.display = "none"
        openFileLoadFormButton.style.display = "flex"
    })

    openFileLoadFormButton.addEventListener("click", (event) => {
        event.target.style.display = "none"
        fileLoadForm.style.display = "block"
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
