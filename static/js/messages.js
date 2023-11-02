document.addEventListener("DOMContentLoaded", function () {
    const message = document.querySelector(".messages-wrapper")
    const closeMessageButton = document.getElementById("close-message")

    setTimeout(() => {
        message.style.top = "3%"
    }, 200)

    setTimeout(function() {
        message.style.top = "-100%"
        setTimeout(function() {
            message.classList.add("hide-message")
        }, 5000)
    }, 3000)

    message.addEventListener("click", () => {
        message.style.top = "-100%"
    })
})
