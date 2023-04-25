const barcodeDetailGraphCanvas = document.getElementById('barcode-detail-graph')
const barcodeDetailWrapper = document.querySelector('.barcode__detail-wrapper')
const openBarcodeDetailWrapper = document.getElementById('barcode-detail-btn')

const labels = [12, 13, 14, 15]
const dataFirst = {
    label: "Выручка",
    data: [15, 12, 23, 32],
    fill: false,
    tension: 0.1,
    borderColor: '#DBDBDB'
};

const dataSecond = {
    label: "Итого к оплате",
    data: [15, 55, 11, 23],
    fill: false,
    tension: 0.1,
    borderColor: '#EF8061'
};

const data = {
    labels: labels,
    datasets: [dataFirst, dataSecond]
};

const config = {
    type: 'line',
    data: data,
    options: {
        responsive: true,
        elements: {
            point: {
                radius: 0
            },
        },
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                enabled: false
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

let isOpened = false
openBarcodeDetailWrapper.addEventListener('click', function(e) {
    if (!isOpened) {
        barcodeDetailWrapper.classList.add('show');
        isOpened = true
    } else {
        barcodeDetailWrapper.classList.remove('show');
        isOpened = false
    }
})
