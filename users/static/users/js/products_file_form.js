document.addEventListener("DOMContentLoaded", function () {
    const fileLoadWrapper = document.querySelector('.file_load_form-wrapper')
    const fileLoadContainer = document.querySelector('.file_load_form-container')
    const openFileFormPopup = document.querySelector('.file-info-popup_btn')
    const changePasswordCancelBtn = document.querySelector('.file_load_cancel-btn')
    const fileLoadInput = document.querySelector('.file-load_input')
    const fileInputStatusText = document.querySelector('.file_status-text')
    const fileFormSendBtn = document.querySelector('.file_load_send-btn')
    const fileLoadInputLabel = document.querySelector('.input-file_button')


    fileLoadInput.addEventListener('change', function (e) {
        let countFiles = '';
        if (this.files && this.files.length >= 1)
            countFiles = this.files.length;

        if (countFiles) {
            fileInputStatusText.innerText = 'Файл выбран';
            fileInputStatusText.style.color = '#000000';
            fileLoadInputLabel.style.border = '1px solid #dbdbdb'
        } else {
            fileInputStatusText.innerText = 'Файл не выбран';
            fileInputStatusText.style.color = '#ff8364';
        }
    });

    fileFormSendBtn.addEventListener('click', function (e) {
        if (fileLoadInput.files.length === 0) {
            fileLoadInputLabel.style.border = '1px solid #ff8364'
        }
    })

    openFileFormPopup.addEventListener('click', function (e) {

        fileLoadWrapper.style.display = 'block';
    })

    changePasswordCancelBtn.addEventListener('click', function () {
        fileLoadWrapper.style.display = 'none';
    })

    document.addEventListener('click', function (e) {
        const target = e.target
        const itsWrapper = target === fileLoadContainer || fileLoadContainer.contains(target);
        const itsButton = target === openFileFormPopup || openFileFormPopup.contains(target);
        if (!itsWrapper && !itsButton) {
            fileLoadWrapper.style.display = 'none';
        }
    })
})