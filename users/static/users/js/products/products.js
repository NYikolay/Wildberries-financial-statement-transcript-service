document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById("productChart")
    const paginatorInput = document.getElementsByClassName('paginator_input')


    const generateInputValidationForPaginator = () => {

        paginatorInput[0].addEventListener('input', function () {

            if (this.value > parseInt(this.attributes[2].value)) {
                this.value = parseInt(this.attributes[2].value)
            }
            if (this.value < 0) {
                this.value = parseInt(this.attributes[2].value)
            }
        })

        paginatorInput[0].addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                window.location = window.location.origin + window.location.pathname + `?page=${this.value}`
            }
        })
    }


    const defaultLabels = ['']
    const defaultRom = [0]
    const defaultProfitability = [0]

    const data = {
        labels: defaultLabels,
        datasets: [
            {
                label: 'Рентабельность',
                data: defaultProfitability,
                borderWidth: 0,
                borderRadius: 4,
                backgroundColor: (context) => {
                    if (!context.chart.chartArea) {
                        return
                    }

                    const { ctx, data, chartArea: { top, bottom } } = context.chart
                    const gradientBg = ctx.createLinearGradient(0, top, 0, bottom)
                    gradientBg.addColorStop(0, "#FC9E36")
                    gradientBg.addColorStop(0.5, "#FC9E36")
                    gradientBg.addColorStop(1, "#FD6DAB")

                    return gradientBg
                },
                barThickness: 25,
                maxBarThickness: 25,
                stack: 'Stack 0',
            },
            {
                label: 'ROM',
                data: defaultRom,
                borderWidth: 0,
                borderRadius: 4,
                barThickness: 25,
                maxBarThickness: 25,
                backgroundColor: (context) => {
                    if (!context.chart.chartArea) {
                        return
                    }

                    const { ctx, data, chartArea: { top, bottom } } = context.chart
                    const gradientBg = ctx.createLinearGradient(0, top, 0, bottom)
                    gradientBg.addColorStop(0, "#00C5FF")
                    gradientBg.addColorStop(0.5, "#00C5FF")
                    gradientBg.addColorStop(1, "#0072FF")

                    return gradientBg
                },
                stack: 'Stack 1',
            }
        ]
    }

    const config = {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    display: false,
                    grid: {
                        display: false,
                    },
                },
                x: {
                    beginAtZero: true,
                    grid: {
                        display: false,
                    },
                    ticks: {
                        color: "#5C659D"
                    },
                    border: {
                        color: "#424B80"
                    },
                    stacked: true
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: "#5C659D",
                        boxWidth: 7,
                        boxHeight: 7,
                        usePointStyle: true,
                        borderRadius: 50,
                        font: {
                            size: 10,
                            family: "'Open Sans', sans-serif"
                        }
                    },
                    display: true,
                    position: "bottom"
                }
            }
        },
        plugins: []
    }

    new Chart(ctx, config)
});