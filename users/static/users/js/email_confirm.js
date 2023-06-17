document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("resend_email_form_id")
    const message = document.querySelector(".messages-wrapper")
    const csrfInput = document.querySelector("[name='csrfmiddlewaretoken']")
    let counter = document.querySelector(".counter")
    const resendButton = document.getElementById("resend_email-btn")
    const resendEmailCounterText = document.querySelector('.resend_email-counter')
    let jsCounter = 60

    function countdownTimer() {
        if (counter.innerText === '0') {
            clearInterval(timerId);
        } else {
            counter.innerText = jsCounter
        }
        jsCounter -= 1
    }

    function restartCounter() {
        counter.innerText = '60'
        jsCounter = 60
        resendButton.disabled = true;
        resendButton.style.opacity = '.7'
        countdownTimer();

        setTimeout(function () {
            resendButton.disabled = false;
            resendButton.style.opacity = '1'
            resendEmailCounterText.classList.add('hidden')
        }, 60000);

        timerId = setInterval(countdownTimer, 1000);
    }

    restartCounter()

    form.addEventListener("submit", function(e){
        e.preventDefault();
        const formData = new FormData();

        formData.append('csrfmiddlewaretoken', csrfInput.value);

        const request = new Request(e.target.action,
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
        resendEmailCounterText.classList.remove('hidden')
        fetch(request).then(response => response.json()).then(data => {
            if (data.status === true) {
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
                restartCounter()
            } else {
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
                restartCounter()
            }
        }).catch(error => {
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
            restartCounter()
        })
    });

})