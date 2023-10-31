document.addEventListener("DOMContentLoaded", function () {
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
})