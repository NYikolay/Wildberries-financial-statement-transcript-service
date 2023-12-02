document.addEventListener("DOMContentLoaded", function () {
    const indicatorItems = document.querySelectorAll(".indicator-item")
    let pastActiveIndicatorItem
    let pastActiveChart
    let pastActiveCanvas

    const lineCanvas = document.getElementById("mainGraph")
    const reportByWeeksData = JSON.parse(lineCanvas.getAttribute("data-report-by-weeks-data"))
    const initialDataWeeksLength = reportByWeeksData.length

    const chartLabels = []
    let toShowData = []

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
        costsWithoutWb: {text: "Расходы вне WB", backendName: "supplier_costs"},
        rom: {text: "ROM", backendName: "rom"},
        totalPayable: {text: "Валовая прибыль", backendName: "total_payable"}

    }

    if (initialDataWeeksLength <= 12 ) {
        reportByWeeksData.forEach((report, index) => {
            chartLabels.push([report.week_num, report.year])
            toShowData = reportByWeeksData.slice()
        })
    } else if (initialDataWeeksLength > 12) {
        reportByWeeksData.slice(-12).forEach((report, index) => {
            chartLabels.push([report.week_num, report.year])
            toShowData = reportByWeeksData.slice(-12)
        })
    }

    const defaultBackgroundChartColors = Array(toShowData.length).fill("#5C659D")

    const getBarChartDataConfig = (labels, chartData, backgroundColors) => {
        return {
            labels: labels,
            datasets: [{
                data: chartData,
                backgroundColor: backgroundColors,
                categoryPercentage: 1,
                barPercentage: 1,
                barThickness: 9.16
            }]
        }
    }

    const getBarChartConfig = (chartData) => {
        return {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                tooltips: {enabled: false},
                hover: {mode: null},
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                scales: {
                    y: {
                        display: false,
                        beginAtZero: true,
                        grid: {
                            display: false,
                            color: "#424B80",
                        },
                    },
                    x: {
                        beginAtZero: false,
                        display: false,
                        grid: {
                            display: false,
                        },
                        border: {
                            color: "#424B80"
                        },
                    }
                },
            }
        }
    }

    const generateChartBackgroundColors = (currentData, gradientOrange, gradientBlue) => {
        const chartBackgroundColors = []

        currentData.forEach((data, index) => {
            if (index === 0) {
                chartBackgroundColors.push(gradientOrange)
            } else {
                data < currentData[index - 1] ?
                    chartBackgroundColors.push(gradientBlue) :
                    chartBackgroundColors.push(gradientOrange)
            }
        })

        return chartBackgroundColors
    }

    const changeCurrentIndicatorStyles = (indicatorItem) => {
        if (pastActiveIndicatorItem) {
            pastActiveIndicatorItem.classList.remove("active-border")
            const pastIndicatorItemTitle = pastActiveIndicatorItem.getElementsByTagName('h1')[0]
            const pastIndicatorItemText = pastActiveIndicatorItem.querySelector('.text__accent')
            const pastIndicatorItemSvg = pastActiveIndicatorItem.getElementsByTagName("svg")[0]

            pastActiveIndicatorItem.classList.remove("active-border")
            pastIndicatorItemTitle.classList.add("dark_h1")
            pastIndicatorItemText.classList.add("text__common-normal")
            pastIndicatorItemText.classList.remove("text__accent")

            if (pastIndicatorItemSvg) {
                pastIndicatorItemSvg.style.fill = "#5C659D"
            }
        }

        const indicatorItemTitle = indicatorItem.querySelector('.dark_h1')
        const indicatorItemText = indicatorItem.querySelector('.text__common-normal')
        const indicatorItemSvg = indicatorItem.getElementsByTagName("svg")[0]

        indicatorItem.classList.add("active-border")
        indicatorItemTitle.classList.remove("dark_h1")
        indicatorItemText.classList.remove("text__common-normal")
        indicatorItemText.classList.add("text__accent")

        if (indicatorItemSvg) {
            indicatorItemSvg.style.fill = "#FFFFFF"
        }
    }

    const getCurrentCanvasGradient = (canvas) => {
        const context = canvas.getContext('2d')

        const gradientOrange = context.createLinearGradient(0, 0, 0, canvas.height)
        gradientOrange.addColorStop(0, '#FC9E36')
        gradientOrange.addColorStop(0.5, '#FC9E36')
        gradientOrange.addColorStop(1, '#FD6DAB')

        const gradientBlue = context.createLinearGradient(0, 0, 0, canvas.height)
        gradientBlue.addColorStop(0, '#00C5FF')
        gradientBlue.addColorStop(0.3, '#00C5FF')
        gradientBlue.addColorStop(1, '#0072FF')

        return {gradientBlue, gradientOrange}
    }

    const changeChartBackgroundColor = (chart, colors) => {
        chart.data.datasets[0].backgroundColor = colors
        chart.update()
    }

    function createBarChartForIndicator(canvas, isActiveIndicator, chartData) {
        let chartBackgroundColors

        const canvasGradients = getCurrentCanvasGradient(canvas)

        if (isActiveIndicator) {
            chartBackgroundColors = generateChartBackgroundColors(
                chartData, canvasGradients.gradientOrange, canvasGradients.gradientBlue
            )
        } else {
            chartBackgroundColors = defaultBackgroundChartColors
        }

        const currentChartDataConfig = getBarChartDataConfig(
            chartLabels, chartData, chartBackgroundColors
        )

        const currentChartConfig= getBarChartConfig(currentChartDataConfig)

        return new Chart(canvas, currentChartConfig)
    }

    const getChartData = (currentCanvas) => {
        const currentData = []
        const canvasDescription = currentCanvas.getAttribute("data-chart-description")
        const itemDescription = reportStaticValues[canvasDescription]

        toShowData.forEach((report) => {
            currentData.push(report[itemDescription.backendName])
        })

        if (toShowData.length === 1) {
            currentData.push(0)
        }

        return currentData
    }

    const updateActiveChart = (currentCanvas, currentChart, currentIndicatorItem, currentChartData) => {
        const canvasGradients = getCurrentCanvasGradient(currentCanvas)
        const chartBackgroundColors = generateChartBackgroundColors(
            currentChartData, canvasGradients.gradientOrange, canvasGradients.gradientBlue
        )

        changeCurrentIndicatorStyles(currentIndicatorItem)
        changeChartBackgroundColor(pastActiveChart, defaultBackgroundChartColors)
        changeChartBackgroundColor(currentChart, chartBackgroundColors)

        pastActiveIndicatorItem = currentIndicatorItem
        pastActiveChart = currentChart
        pastActiveCanvas = currentCanvas
    }

    indicatorItems.forEach((item, index) => {
        const canvas = item.querySelector(".indicator-chart")
        const isActive = item.getAttribute("data-is-active") === "true"
        const chartData = getChartData(canvas)

        const currentChart = createBarChartForIndicator(canvas, isActive, chartData)

        if (isActive) {
            changeCurrentIndicatorStyles(item)
            pastActiveIndicatorItem = item
            pastActiveChart = currentChart
            pastActiveCanvas = canvas
        }

        item.addEventListener("click", (event) => {
            updateActiveChart(canvas, currentChart, item, chartData)
        })
    })
})