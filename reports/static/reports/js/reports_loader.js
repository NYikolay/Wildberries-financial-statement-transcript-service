document.addEventListener("DOMContentLoaded", function () {
    const loadBtn = document.getElementById("load-btn");
    const loadReportsInfo = document.getElementById('reports_load-info')

    loadBtn.addEventListener('click', () => {
        loadReportsInfo.innerHTML = 'Идёт загрузка отчётов. Пожалуйста, подождите.'
        loadBtn.classList.add("loading");
    });
})