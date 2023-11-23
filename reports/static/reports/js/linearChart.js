const lineCanvas = document.getElementById("mainGraph")
const indicatorItems = document.querySelectorAll(".indicator-item")
const reportByWeeksData = JSON.parse(lineCanvas.getAttribute("data-report-by-weeks-data"))
let pastChart
let pastIndicatorItem
const chartLabels = []
const currentIndicatorTitle = document.getElementById("current-indicator-title")

reportByWeeksData.forEach((report) => {
    chartLabels.push([report.week_num, report.year])
})

const reportStaticValues = {
    revenue: {text: "Выручка", backendName: "revenue"},
    profit: {text: "Прибыль", backendName: "profit"},
    profitability: {text: "Рентабельность", backendName: "profitability"},
    marginality: {text: "Маржинальность", backendName: "marginality"},
    salesCount: {text: "Продажи", backendName: "sales_amount"},
    returnsCount: {text: "Возвраты", backendName: "returns_amount"},
    commission: {text: "Комиссия", backendName: "commission"},
    logistics: {text: "Логистика", backendName: "logistics"},
    penalty: {text: "Штрафы", backendName: "penalty"},
    additionalPayment: {text: "Доплаты", backendName: "additional_payment_sum"},
    netCost: {text: "Себестоимость", backendName: "net_costs_sum"},
    tax: {text: "Налог", backendName: "tax"},
    wbCosts: {text: "Расходы на WB", backendName: "wb_costs"},
    costsWithoutWb: {text: "Расходы вне WB", backendName: "supplier_costs"}
}


const getLineChartData = (currentLabel, labels, data) => {
    return {
        labels: labels,
        datasets: [{
            label: currentLabel,
            data: data,
            fill: false,
            pointHoverBorderColor: 'white',
            pointBackgroundColor: 'transparent',
            pointBorderColor: 'transparent',
            pointHoverBorderWidth: 2,
            pointHoverBackgroundColor: '#0175FF',
            pointHitRadius: 25,
            hitRadius: 25,
            pointHoverRadius: 6,
            borderColor: '#0079FF',
            tension: 0.4
        }]
    }
}

const getLineChartConfig = (data) => {
    const currentDataSet = data.datasets[0].data
    return {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            animation: {
                easing: 'easeInOutQuad',
                duration: 520
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            scales: {
                y: {
                    beginAtZero: true,
                    display: true,
                    grid: {
                        display: true,
                        color: "#424B80",
                    },
                    offset: true,
                    border: {
                        dash: [4, 4],
                        color: "#424B80"
                    },
                    ticks: {
                        color: "#5C659D",
                        font: {
                            size: 10,
                            family: "'Open Sans', sans-serif",
                            weight: "bold"
                        },
                    },
                    min: Math.round(Math.min(...currentDataSet)),
                    max: Math.round(Math.max(...currentDataSet))
                },
                x: {
                    beginAtZero: true,
                    grid: {
                        display: false,
                    },
                    border: {
                        color: "#424B80"
                    },
                    offset: reportByWeeksData.length !== 1,
                    ticks: {
                        color: "#5C659D",
                        font: {
                            size: 10,
                            family: "'Open Sans', sans-serif",
                            weight: "bold"
                        },
                        align: "center",
                    },
                }
            },
            plugins: {
                tooltip: {
                    backgroundColor: "#FFFFFF",
                    titleColor: "#5C659D",
                    titleFont: {
                        weight: "bold",
                        size: 14
                    },
                    bodyColor: "#5C659D",
                    bodyFont: {
                        weight: "bold",
                        size: 10
                    },
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }

                            if (context.parsed.y !== null) {
                                label += Math.round(context.parsed.y).toLocaleString('ru')
                            }
                            return label;
                        }
                    }
                },
                legend: {
                    labels: {
                        color: "#5C659D",
                        boxWidth: 7,
                        boxHeight: 7,
                        usePointStyle: true,
                        borderRadius: 50,
                        font: {
                            size: 10,
                            family: "'Open Sans', sans-serif",
                            weight: "bold"
                        }
                    },
                    display: false,
                    position: "bottom"
                }
            }
        },
        plugins: []
    }
}

const renderChart = (chartConfig) => {
    pastChart && pastChart.destroy()

    pastChart = new Chart(lineCanvas, chartConfig)
}

const getIndicatorSign = (indicatorText) => {
    if (indicatorText === reportStaticValues.profitability.text || indicatorText === reportStaticValues.marginality.text) {
        return '%'
    } else if (indicatorText === reportStaticValues.salesCount.text || indicatorText === reportStaticValues.returnsCount.text) {
        return ''
    } else {
        return ' руб.'
    }
}

const handleChartRendering = (itemDescription, indicatorItem) => {
    let currentData = []

    reportByWeeksData.forEach((report) => {
        currentData.push(report[itemDescription.backendName])
    })

    if (reportByWeeksData.length === 1) {
        currentData.push(0)
    }

    const chartData = getLineChartData(itemDescription.text, chartLabels, currentData)
    const chartConfig = getLineChartConfig(chartData)

    renderChart(chartConfig)

    const indicatorSign = getIndicatorSign(itemDescription.text)

    currentIndicatorTitle.innerText = `${itemDescription.text} (${indicatorItem.getAttribute("data-item-total")}${indicatorSign})`
    changeCurrentIndicatorStyles(indicatorItem)
}

const changeCurrentIndicatorStyles = (indicatorItem) => {
    if (pastIndicatorItem) {
        pastIndicatorItem.classList.remove("active-border")
        const pastIndicatorItemStaticWrapper = pastIndicatorItem.childNodes[1]
        const pastIndicatorItemTitle = pastIndicatorItem.getElementsByTagName('h1')[0]
        const pastIndicatorItemText = pastIndicatorItem.querySelector('.text__accent')
        const pastIndicatorItemSvg = pastIndicatorItem.getElementsByTagName("svg")[0]

        pastIndicatorItem.classList.remove("active-border")
        pastIndicatorItemTitle.classList.add("dark_h1")
        pastIndicatorItemText.classList.add("text__common-normal")
        pastIndicatorItemText.classList.remove("text__accent")
        pastIndicatorItemSvg.style.fill = "#5C659D"

        pastIndicatorItemStaticWrapper.innerHTML = `
        <div style="width: 9px; height: 45px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 36px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 29px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 22px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 27px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 32px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 29px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 36px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 22px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 29px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 36px; background-color: #5C659D;"></div>
        <div style="width: 9px; height: 45px; background-color: #5C659D;"></div>
        `
    }

    const indicatorItemTitle = indicatorItem.querySelector('.dark_h1')
    const indicatorItemText = indicatorItem.querySelector('.text__common-normal')
    const indicatorItemSvg = indicatorItem.getElementsByTagName("svg")[0]

    indicatorItem.classList.add("active-border")
    indicatorItemTitle.classList.remove("dark_h1")
    indicatorItemText.classList.remove("text__common-normal")
    indicatorItemText.classList.add("text__accent")
    indicatorItemSvg.style.fill = "#FFFFFF"
    indicatorItem.childNodes[1].innerHTML = `
                <div style="width: 9px; height: 45px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 36px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 29px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 22px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 27px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 32px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 29px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 36px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 22px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 29px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 36px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 45px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
    `
    pastIndicatorItem = indicatorItem
}

indicatorItems.forEach((item) => {
    item.addEventListener("click", (event) => {
        const itemDescription = reportStaticValues[item.getAttribute("data-item-description")]
        handleChartRendering(itemDescription, item)
    })
})

const initialRenderChart = () => {
    const indicatorItem = indicatorItems[0]
    const itemDescription = reportStaticValues[indicatorItem.getAttribute("data-item-description")]

    handleChartRendering(itemDescription, indicatorItem)
}


initialRenderChart()