document.addEventListener("DOMContentLoaded", function () {
    const loadBtn = document.getElementById("load-btn");

    function setIntervalForLoadBtn(lastClickTime) {
        const clickLoadBtnInterval = setInterval(function () {
            if (new Date() <= lastClickTime) {
                loadBtn.innerHTML = `${loadBtn.getAttribute('data-process-type')} (${(Math.floor((lastClickTime.getTime() - new Date().getTime()) / 1000))})`
            } else {
                localStorage.removeItem("lastClickTime");
                clearInterval(clickLoadBtnInterval)
                loadBtn.disabled = false;
                loadBtn.innerHTML = `${loadBtn.getAttribute('data-process-type')}`
            }
        }, 1000)
    }

    if (localStorage.getItem("lastClickTime")) {
        const lastClickTime = new Date(Number(localStorage.getItem("lastClickTime")))
        if (new Date() <= lastClickTime) {
            loadBtn.innerHTML = `${loadBtn.getAttribute('data-process-type')} (${Math.floor((lastClickTime.getTime() - new Date().getTime()) / 1000)})`
            loadBtn.disabled = true;
            setIntervalForLoadBtn(lastClickTime)
        } else {
            localStorage.removeItem("lastClickTime");
        }
    }

    const sendFetchForStatus = (url) => {
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                if (data.status.is_active_import === false) {
                    window.location.replace(`${loadBtn.getAttribute('data-redirect-url')}`);
                }
            })
            .catch(error => {
            });
    }

    if (loadBtn.getAttribute("data-check") === 'true') {
        const requestUrl = loadBtn.getAttribute("data-url")
        setInterval(function(){sendFetchForStatus(requestUrl)}, 1000);
    } else {
        loadBtn.addEventListener('click', () => {
            loadBtn.classList.add("loading");

            const currentTimePlusTwoMin = new Date()
            currentTimePlusTwoMin.setMinutes(currentTimePlusTwoMin.getMinutes() + 1);
            localStorage.setItem("lastClickTime", String(currentTimePlusTwoMin.getTime()));

        });
    }

})