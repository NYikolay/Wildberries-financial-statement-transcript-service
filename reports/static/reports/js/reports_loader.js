document.addEventListener("DOMContentLoaded", function () {
    const loadBtn = document.getElementById("load-btn");
    const loadReportsInfo = document.getElementById('reports_load-info')

    function setIntervalForLoadBtn(lastClickTime) {
        const clickLoadBtnInterval = setInterval(function () {
            if (new Date() <= lastClickTime) {
                loadBtn.innerHTML = `Обновить список (${(Math.floor((lastClickTime.getTime() - new Date().getTime()) / 1000))})`
            } else {
                localStorage.removeItem("lastClickTime");
                clearInterval(clickLoadBtnInterval)
                loadBtn.disabled = false;
                loadBtn.innerHTML = "Обновить список"
            }
        }, 1000)
    }

    if (localStorage.getItem("lastClickTime")) {
        const lastClickTime = new Date(Number(localStorage.getItem("lastClickTime")))
        loadBtn.innerHTML = `Обновить список (${Math.floor((lastClickTime.getTime() - new Date().getTime()) / 1000)})`
        loadBtn.disabled = true;
        setIntervalForLoadBtn(lastClickTime)
    }

    const sendFetchForStatus = (url) => {
        fetch(url, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                if (data.status.is_active_import === false) {
                    location. reload()
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
            loadReportsInfo ? loadReportsInfo.innerHTML = 'Идёт загрузка отчётов. Пожалуйста, оставайтесь на странице до ее завершения.' : null
            loadBtn.classList.add("loading");

            const currentTimePlusTwoMin = new Date()
            currentTimePlusTwoMin.setMinutes(currentTimePlusTwoMin.getMinutes() + 1);
            localStorage.setItem("lastClickTime", String(currentTimePlusTwoMin.getTime()));

        });
    }

})