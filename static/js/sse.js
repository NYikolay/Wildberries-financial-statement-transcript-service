document.addEventListener("DOMContentLoaded", function () {
    const toastDataWrapper = document.getElementById('toast-data-wrapper')
    const userId = toastDataWrapper.getAttribute('data-user-id')
    const dashboardUrl = toastDataWrapper.getAttribute("dashboard-url")
    const reportUrl = toastDataWrapper.getAttribute("reports-url")
    const isIncorrectReportsExist = toastDataWrapper.getAttribute('incorrect-reports-exists')

    if (userId) {
        let eventSource = new ReconnectingEventSource(`${window.location.origin}/events/user/${userId}/`)

        eventSource.addEventListener("message", (event) => {
            const data = event.data
            const parsedData = JSON.parse(data)
            const status = parsedData.status

            localStorage.setItem("notificationStatus", data)

            if (status === "error" || isIncorrectReportsExist === "True") {
                window.location.replace(reportUrl)
            } else {
                window.location.replace(dashboardUrl)
            }
        }, false)
    }
})