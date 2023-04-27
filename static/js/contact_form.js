document.addEventListener("DOMContentLoaded", function () {
    const contactBtn = document.getElementById('contact-btn')
    const contactFormWrapper = document.getElementById('contact-form_wrapper')
    const closeContactBtn = document.getElementById('close_contact-form')
    const contactBackgroundWrapper = document.querySelector('.contact-background_wrapper')
    const contactForm = document.querySelector('.contact-form')
    const message = document.querySelector(".messages-wrapper")

    function closeContactForm () {
        contactFormWrapper.style.display = 'none'
        contactBtn.style.display = 'block'
        contactBackgroundWrapper.style.width = null
        contactBackgroundWrapper.style.height = null
        contactBackgroundWrapper.style.backgroundColor = null
    }

    contactBtn.addEventListener('click', function() {
        contactFormWrapper.style.display = 'flex'
        this.style.display = 'none'
        contactBackgroundWrapper.style.width = '100%'
        contactBackgroundWrapper.style.height = '100%'
        contactBackgroundWrapper.style.backgroundColor = 'rgba(0,0,0,0.5)'
    })
    closeContactBtn.addEventListener('click', function() {
        closeContactForm()
    })

    document.addEventListener('click', function (e) {
        const target = e.target
        const itsWrapper = target === contactFormWrapper || contactFormWrapper.contains(target);
        const itsButton = target === contactBtn || contactBtn.contains(target);
        if (!itsWrapper && !itsButton) {
            closeContactForm()
        }
    })

    contactForm.addEventListener('submit', function (evt) {
        evt.preventDefault();
        const user = document.getElementById('id_user')
        const contactType = document.getElementById('id_message_type')
        const contactName = document.getElementById('id_user_name')
        const csrfInput = document.querySelector("[name='csrfmiddlewaretoken']")
        const contactMessage = document.getElementById('id_message')

        const formData = new FormData();

        formData.append('user', user.value);
        formData.append('csrfmiddlewaretoken', csrfInput.value);
        formData.append('message_type', contactType.value);
        formData.append('user_name', contactName.value);
        formData.append('message', contactMessage.value);

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
                closeContactForm()
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
                closeContactForm()
                const messageError = document.createElement('div')
                messageError.className = 'message_item-error'
                messageError.innerHTML =
                    `
                        <img class="message-img" src="/static/images/iconizer-4201973.svg" alt="">
                        <p class="message_text">${data.message}</p>
                `
                message.style.transform = "translateX(0)";
                message.style.right = "30px";
                message.appendChild(messageError)

                setTimeout(() => {
                    message.style.transform = "translateX(100%)";
                    message.style.right = "0";
                }, 10000)

                setTimeout(() => {
                    message.removeChild(messageError)
                }, 15000)
            }
        }).catch(error => {
            closeContactForm()
            const messageError = document.createElement('div')
            messageError.className = 'message_item-error'
            messageError.innerHTML =
                `
                        <img class="message-img" src="/static/images/iconizer-4201973.svg" alt="">
                        <p class="message_text">Произошла ошибка отправки сообщения. Пожалуйста, убедитесь что все поля заполнены верно.</p>
                `
            message.style.transform = "translateX(0)";
            message.style.right = "30px";
            message.appendChild(messageError)

            setTimeout(() => {
                message.style.transform = "translateX(100%)";
                message.style.right = "0";
            }, 10000)

            setTimeout(() => {
                message.removeChild(messageError)
            }, 15000)
        });
    })

})