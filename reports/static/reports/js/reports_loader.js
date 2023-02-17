document.addEventListener("DOMContentLoaded", function () {
    const loadBtn = document.getElementById("load-btn");
    const loadReportsInfo = document.getElementById('reports_load-info')

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
            loadReportsInfo ? loadReportsInfo.innerHTML = 'Идёт загрузка отчётов. Пожалуйста, оставайтесь на странице до ее завершения' : null
            loadBtn.classList.add("loading");
        });
    }

})