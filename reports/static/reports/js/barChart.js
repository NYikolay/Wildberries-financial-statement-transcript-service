document.addEventListener("DOMContentLoaded", function () {
    const barChartCanvas = document.getElementById("shareShipmentGraph")
    const stockShareData = JSON.parse(barChartCanvas.getAttribute('data-stock-canvas'))

    const stockShareDataSetArraysObject = {
        labels: [],
        data: []
    }

    for (let [key, value] of Object.entries(stockShareData)) {
        stockShareDataSetArraysObject.labels.push(key)
        stockShareDataSetArraysObject.data.push(Math.round(value))
    }

    const barChartData = {
        labels: stockShareDataSetArraysObject.labels,
        datasets: [
            {
                label: 'Процент в выручке',
                data: stockShareDataSetArraysObject.data,
                borderColor: "transparent",
                barThickness: 25,
                borderRadius: 5,
                backgroundColor: (context) => {
                    if (!context.chart.chartArea) {
                        return
                    }

                    const {ctx, data, chartArea: {top, bottom, left, right}} = context.chart
                    const gradientBg = ctx.createLinearGradient(left, 0, right, 0)
                    gradientBg.addColorStop(0, "#FC9E36")
                    gradientBg.addColorStop(1, "#FD6DAB")

                    return gradientBg
                },
            },
        ]
    };

    const barChartConfig = {
        type: 'bar',
        data: barChartData,
        options: {
            responsive: true,
            indexAxis: 'y',
            elements: {
                bar: {
                    borderWidth: 6,
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        display: false,
                    },
                    display: false,
                },
                y: {
                    grid: {
                        display: false,
                    },
                    ticks: {
                        color: "#FFFFFF",
                        font: {
                            size: 10,
                            family: "'Open Sans', sans-serif",
                            weight: "normal"
                        },
                    },
                }
            },
            plugins: {
                legend: {
                    display: false,
                    position: 'right',
                },
            }
        },
    }

    new Chart(barChartCanvas, barChartConfig)

})