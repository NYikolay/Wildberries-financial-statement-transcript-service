document.addEventListener("DOMContentLoaded", function () {
    const passwordChangeWrapper = document.getElementById('password_change-wrapper')
    const changePasswordForm = document.querySelector('.change_password-form')
    const changePasswordButton = document.querySelector('.change_password-link')
    const changePasswordContainer = document.querySelector('.password_change-container')
    const changePasswordCancelBtn = document.querySelector('.change_password-cancel')
    const csrfInput = document.querySelector("[name='csrfmiddlewaretoken']")
    const message = document.querySelector(".messages-wrapper")

    changePasswordButton.addEventListener('click', function (e) {

        passwordChangeWrapper.style.display = 'block';
    })

    changePasswordCancelBtn.addEventListener('click', function () {
        passwordChangeWrapper.style.display = 'none';
    })

    document.addEventListener('click', function (e) {
        const target = e.target
        const itsWrapper = target === changePasswordContainer || changePasswordContainer.contains(target);
        const itsButton = target === changePasswordButton || changePasswordButton.contains(target);
        if (!itsWrapper && !itsButton) {
            passwordChangeWrapper.style.display = 'none';
        }
    })

    changePasswordForm.addEventListener('submit', function (evt) {
        evt.preventDefault();
        const oldPassword = document.getElementById('id_old_password')
        const newPassword = document.getElementById('id_new_password')
        const reenteredPassword = document.getElementById('id_reenter_password')
        const changePasswordErrorsText = document.querySelector('.change_password-errors')

        const formData = new FormData();

        formData.append('csrfmiddlewaretoken', csrfInput.value);
        formData.append('old_password', oldPassword.value);
        formData.append('new_password', newPassword.value);
        formData.append('reenter_password', reenteredPassword.value);

        const request = new Request(evt.target.action,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfInput.value,
                    "X-Requested-With": "XMLHttpRequest"
                },
                mode: 'same-origin',
                body: formData
            }
        );

        fetch(request).then(response => response.json()).then(data => {
            if (data.status === true) {
                passwordChangeWrapper.style.display = 'none';
                const messageSuccess = document.createElement('div')
                messageSuccess.className = 'message_item-success'
                messageSuccess.innerHTML =
                    `
                        <img class="message-img" src="/static/images/check (1).svg" alt="">
                        <p class="message_text">${data.message}</p>
                    `
                message.style.transform = "translateX(0)";
                message.style.right = "30px";
                message.appendChild(messageSuccess)

                setTimeout(() => {
                    message.style.transform = "translateX(100%)";
                    message.style.right = "0";
                }, 10000)

                setTimeout(() => {
                    message.removeChild(messageSuccess)
                }, 15000)
            } else {
                changePasswordErrorsText.innerHTML = data.message
            }
        }).catch(error => {
            changePasswordErrorsText.innerHTML = 'Произошла ошибка во время отправки формы.'
        });
    })
})