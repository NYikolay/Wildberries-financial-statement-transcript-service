document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("resend_email_form_id")
    const message = document.querySelector(".messages-wrapper")
    const csrfInput = document.querySelector("[name='csrfmiddlewaretoken']")
    let counter = document.querySelector(".counter")
    const resendButton = document.querySelector(".resend_email-btn")
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
        }, 60000);

        timerId = setInterval(countdownTimer, 1000);
    }

    restartCounter()

    form.addEventListener("submit", function(e){
        e.preventDefault();
        const formData = new FormData();

        formData.append('csrfmiddlewaretoken', csrfInput.value);

        fetch(e.target.action, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                const messageSuccess = document.createElement('div')
                data.status === true ? messageSuccess.className = 'message_item-success' : messageSuccess.className = 'message_item-error'
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
            })
            .catch(error => {
                const messageError = document.createElement('div')
                messageError.className = 'message_item-error'
                messageError.innerHTML =
                    `
                        <img class="message-img" src="/static/images/check (1).svg" alt="">
                        <p class="message_text">Произошла ошибка во время повторной отправки сообщения. Пожалуйста, попробуйте ещё раз или обратитесь в службу поддержки</p>
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
            });

    });

})