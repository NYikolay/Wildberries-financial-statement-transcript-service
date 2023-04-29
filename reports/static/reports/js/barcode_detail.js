const barcodeDetailContainer = document.querySelector('.barcode__detail-container')
const barcodeDetailWrapper = document.querySelector('.barcode__detail-wrapper')
const currentFilterData = document.querySelector('.graphs-bar-filter_wrapper').getAttribute('data-current-filters')
let barcodeDetailForm = document.querySelectorAll('#barcode-detail-form')
const barcodeDetailUrl = barcodeDetailContainer.getAttribute('data-url')
const changeBarcodeFormsBtns = document.querySelectorAll('.abc-xyz__filter__item')
let isOpened = false


barcodeDetailWrapper.addEventListener('click', function (e) {
    const target = e.target
    const itsWrapper = target === barcodeDetailContainer || barcodeDetailContainer.contains(target)
    if (!itsWrapper) {
        isOpened = false
        hideBarcodeDetail()
    }
})

changeBarcodeFormsBtns.forEach(button => {
    button.addEventListener('click', function (e) {
        barcodeDetailForm = document.querySelectorAll('#barcode-detail-form')
        generateBarcodeDetailFormEventListener()
    })
})

function createBarcodeDetailGraph (barcodeDetailGraphCanvas, graph_data) {
    const weekLabels = graph_data['week_nums']
    const dataRevenue = {
        label: "Выручка",
        data: graph_data['revenues'],
        fill: false,
        tension: 0.1,
        borderColor: '#DBDBDB',
        backgroundColor: '#DBDBDB'
    };
    const dataToPay = {
        label: "Итого к оплате",
        data: graph_data['total_payable'],
        fill: false,
        tension: 0.1,
        borderColor: '#EF8061',
        backgroundColor: '#EF8061'
    };

    const data = {
        labels: weekLabels,
        datasets: [dataRevenue, dataToPay]
    };

    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    titleFont: {
                        size: 8
                    },
                    bodyFont: {
                        size: 8
                    },
                    callbacks: {
                        title: function(tooltipItems, data) {
                            return 'Неделя ' + tooltipItems[0].label;
                        },
                        label: function(tooltipItems, data) {
                            return `${tooltipItems.dataset.label}: ` + `${Math.round(tooltipItems.raw).toLocaleString('ru')}`
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    grid: {
                        display: false,
                    }
                },
            }
        }
    };

    new Chart(barcodeDetailGraphCanvas, config)
}


function hideBarcodeDetail() {
    barcodeDetailContainer.classList.remove('show')
    barcodeDetailWrapper.classList.remove('show')
    setTimeout(function () {
            barcodeDetailContainer.innerHTML = `
        <div class="loader__wrapper">
            <div class="loader">loading</div>
        </div>
        <h3 style="text-align: center">Данные загружаются. Пожалуйста, подождите</h3>
    `
    }, 300)
}

function showBarcodeDetail() {
    barcodeDetailWrapper.classList.add('show')
    barcodeDetailContainer.classList.add('show')
}

function deleteBarcodeDetailChildrens() {
    while (barcodeDetailContainer.firstChild) {
        barcodeDetailContainer.removeChild(barcodeDetailContainer.firstChild)
    }
}

function generateBarcodeDetailHtml(barcode_data) {

    deleteBarcodeDetailChildrens()

    const cleanHtml = DOMPurify.sanitize(`
        <div class="barcode__detail-header">
            <img src="${barcode_data['image']}" alt="" class="barcode__detail-image">
            <div class="barcode__detail-info__wrapper">
                <p class="barcode__product-name">${barcode_data['product_name']}</p>
                <div class="barcode__product-info">
                    <p>Артикул: ${barcode_data['nm_id']}</p>
                    <p>Баркод: ${barcode_data['barcode']}</p>
                </div>
            </div>
        </div>
        <div class="barcode__detail-content">
            <div class="barcode__detail-graph__wrapper">
                <canvas id="barcode-detail-graph"></canvas>
                <div class="graph__description-wrapper">
                    <div class="barcode__detail-description__item">
                       <div style="background-color: #DBDBDB"></div>
                       <p>Выручка</p>
                </div>
            <div class="barcode__detail-description__item">
                <div style="background-color: #EF8061"></div>
                    <p>Итого к оплате</p>
            </div>
            </div>
        </div>
        <div class="barcode__report-wrapper">
            <div class="barcode__report-left">
                <div class="barcode__report-left__item">
                    <h3>${Math.round(barcode_data['revenue_total']).toLocaleString('ru')}</h3>
                    <p>Выручка</p>
                </div>
                <div class="barcode__report-left__item">
                    <h3 style="color: #ff8364">${barcode_data['total_payable'].toLocaleString('ru')}</h3>
                    <p>Итого к оплате</p>
            </div>
        </div>
        <div class="barcode__report-right">
            <div class="barcode__report-right__item">
                <h3>${barcode_data['marginality_total']}%</h3>
                <p>Маржинальность</p>
            </div>
            <div class="barcode__report-right__item">
                <h3>${barcode_data['commission_total'].toLocaleString('ru')}</h3>
                <p>Комиссия</p>
            </div>
            <div class="barcode__report-right__item">
                <h3>${barcode_data['xyz_group']}</h3>
                <p>Группа ABC-XYZ</p>
            </div>
            <div class="barcode__report-right__item">
                <h3>${barcode_data['logistics_total'].toLocaleString('ru')}</h3>
                <p>Логистика</p>
            </div>
            <div class="barcode__report-right__item">
                <h3>${barcode_data['sales_amount_total'].toLocaleString('ru')}</h3>
                <p>Продажи</p>
            </div>
            <div class="barcode__report-right__item">
                <h3>${barcode_data['penalty_total'].toLocaleString('ru')}</h3>
                <p>Штрафы</p>
            </div>
            <div class="barcode__report-right__item">
                <h3>${barcode_data['returns_amount_total'].toLocaleString('ru')}</h3>
                <p>Возвраты</p>
            </div>
            <div class="barcode__report-right__item">
                <h3>${barcode_data['additional_payment_sum_total'].toLocaleString('ru')}</h3>
                <p>Доплаты</p>
            </div>
        </div>
    </div>
    </div>
    `)

    const content = document.createRange().createContextualFragment(cleanHtml)
    barcodeDetailContainer.appendChild(content)

    const barcodeDetailGraphCanvas = document.getElementById('barcode-detail-graph')
    createBarcodeDetailGraph(barcodeDetailGraphCanvas, JSON.parse(barcode_data['reports_by_week']))
}


function generateBarcodeDetailFormEventListener(form) {
    barcodeDetailForm.forEach(form => {
        form.addEventListener('submit', function (event) {
            if (!isOpened) {
                showBarcodeDetail()
                isOpened = true
            }

            event.preventDefault()
            const abc_group = form.elements['abc_group'].value;
            const barcode = form.elements['barcode'].value;
            const csrfmiddlewaretoken = form.elements['csrfmiddlewaretoken'].value;
            const share_in_revenue = form.elements['share_in_revenue'].value;
            const xyz_group = form.elements['xyz_group'].value === 'null' ? '-' : form.elements['xyz_group'].value;
            const nm_id = form.elements['nm_id'].value;
            const image = form.elements['image'].value;
            const product_name = form.elements['product_name'].value;

            const formData = new FormData()
            formData.append('csrfmiddlewaretoken', csrfmiddlewaretoken);
            formData.append('abc_group', abc_group);
            formData.append('barcode', barcode);
            formData.append('share_in_revenue', share_in_revenue);
            formData.append('xyz_group', xyz_group);
            formData.append('nm_id', nm_id);
            formData.append('image', image);
            formData.append('product_name', product_name)
            formData.append('period_filters', currentFilterData)
            sendFetchFroBarcodeDetail(barcodeDetailUrl, csrfmiddlewaretoken, formData)

        })
    })
}

function sendFetchFroBarcodeDetail(url, csrfToken, formData) {
    const request = new Request(url,
        {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                "X-Requested-With": "XMLHttpRequest"
            },
            mode: 'same-origin',
            body: formData
        }
    );
    fetch(request).then(response => response.json()).then(data => {
        if (data.status) {
            generateBarcodeDetailHtml(data)
        } else {
            deleteBarcodeDetailChildrens()
            barcodeDetailContainer.innerHTML = `
                <img src="/static/images/iconizer-4201973.svg" alt="" style="height: 50px; width: 50px; align-self: center">
                <h3 style="text-align: center">Произошла ошибка во время формирования данных о баркоде. Пожалуйста, обновите страницу, если ошибка повторяется обратитесь в службу поддержки</h3>
            `
        }
    })
}

generateBarcodeDetailFormEventListener()


