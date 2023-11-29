document.addEventListener("DOMContentLoaded", function () {
    const toastError = document.getElementById('toast-error')
    const toastSuccess = document.getElementById('toast-success')
    const toastDataWrapper = document.getElementById('toast-data-wrapper')
    const userId = toastDataWrapper.getAttribute('data-user-id')
    const dashboardUrl = toastDataWrapper.getAttribute("dashboard-url")
    const reportUrl = toastDataWrapper.getAttribute("reports-url")
    const isIncorrectReportsExist = toastDataWrapper.getAttribute('incorrect-reports-exists')

    let toastContainer

    (function initToast(){
        document.body.insertAdjacentHTML('afterbegin', `<div class="toast-container"></div>`);
        toastContainer = document.querySelector('.toast-container');
    })()

    function generateToast({message, background = '#00214d', length = '3000ms'}){
        toastContainer.insertAdjacentHTML('beforeend',
            `<p class="toast" 
                    style="background-color: ${background};
                    cursor: pointer;
                    animation-duration: ${length}">
                    ${message}
            </p>`
        )

        const toast = toastContainer.lastElementChild;
        toast.addEventListener('animationend', () => toast.remove())
        toast.addEventListener("click", () => toast.remove())
    }

    if (toastError) {
        generateToast({
            background: "#EC496B",
            message: toastError.innerHTML,
            length: "5000ms",
        })
    } else if (toastSuccess) {
        generateToast({
            background: "#36D04F",
            message: toastSuccess.innerHTML,
            length: "5000ms",
        })
    }

    if (localStorage.getItem("notificationStatus")) {
        const notificationData = JSON.parse(localStorage.getItem("notificationStatus"))
        const messageText = decodeURIComponent(notificationData.message)
        const status = notificationData.status
        localStorage.removeItem("notificationStatus")

        if (status === "error") {
            generateToast({
                background: "#EC496B",
                message: messageText,
                length: "5000ms",
            })
        } else {
            generateToast({
                background: "#36D04F",
                message: messageText,
                length: "5000ms",
            })
        }

    }

    if (userId) {
        let eventSource = new EventSource(`${window.location.origin}/user/${userId}/events/`)

        eventSource.onmessage = (event) => {
            const data = event.data
            const parsedData = JSON.parse(data)
            const status = parsedData.status

            localStorage.setItem("notificationStatus", data)

            if (status === "error" || isIncorrectReportsExist === "True") {
                window.location.replace(reportUrl)
            } else {
                window.location.replace(dashboardUrl)
            }

        }
    }
})