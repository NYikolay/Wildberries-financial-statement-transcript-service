document.addEventListener("DOMContentLoaded", function () {
    const message = document.querySelector(".messages-wrapper")

    message.style.transform = "translateX(0)";
    message.style.right = "30px";

    setTimeout(() => {
        message.style.transform = "translateX(100%)";
        message.style.right = "0";
    }, 10000);
})
