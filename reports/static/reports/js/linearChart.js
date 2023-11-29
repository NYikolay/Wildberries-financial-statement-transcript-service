document.addEventListener("DOMContentLoaded", function () {
    const lineCanvas = document.getElementById("mainGraph")
    const indicatorItems = document.querySelectorAll(".indicator-item")
    const reportByWeeksData = JSON.parse(lineCanvas.getAttribute("data-report-by-weeks-data"))
    let pastChart
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
        costsWithoutWb: {text: "Расходы вне WB", backendName: "supplier_costs"},
        rom: {text: "ROM", backendName: "rom"},
        totalPayable: {text: "Валовая прибыль", backendName: "total_payable"}

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
                        titleAlign: 'center',
                        bodyAlign: 'center',
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
                            label: function (context) {
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
        if (indicatorText === reportStaticValues.profitability.text || indicatorText === reportStaticValues.marginality.text || indicatorText === reportStaticValues.rom.text) {
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
    }

    indicatorItems.forEach((item) => {
        const itemDescription = reportStaticValues[item.getAttribute("data-item-description")]
        const isActive = item.getAttribute("data-is-active") === "true"

        // initial chart render
        isActive && handleChartRendering(itemDescription, item)

        item.addEventListener("click", (event) => {
            handleChartRendering(itemDescription, item)
        })
    })
})
