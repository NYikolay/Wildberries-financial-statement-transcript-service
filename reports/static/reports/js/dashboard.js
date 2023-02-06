document.addEventListener("DOMContentLoaded", function () {
    const mainChartData = {
        labels: ["44", "45", "46", "44", "45", "46", "44", "45", "46", "44", "45", "46"],
        datasets: [
            {
                label: 'Прибыль',
                backgroundColor: "#EF8061",
                data: [200, 500, 100, 200, 500, 100, 200, 500, 100, 200, 500, 100],
                borderRadius: 5
            },
            {
                label: 'Выручка',
                backgroundColor: "#DBDBDB",
                data: [-300, 200, -100, 200, 500, 100, -300, 200, -100, 200, 500, 100],
                borderRadius: 5
            },
        ],
    };

    const doughnutBrandData = {
        labels: [
            "КОЛЕДИНО",
            "КАЗАНЬ",
            "ШУШАРЫ",
            "ШУШАРЫ",
            "Новосибирск",
            "Санкт-Петербург Ш блок 1"
        ],
        datasets: [
            {
                data: [3200, 50, 100, 1233, 5.640040478121926, 5.571520576438181],
                backgroundColor: [
                    "#f65731",
                    "#fc805e",
                    "#fda58b",
                    "#ebebeb",
                    "#f65731",
                    "#fc805e",
                    "#fda58b",
                    "#ebebeb"
                ],
                hoverBackgroundColor: [
                    "#f65731",
                    "#fc805e",
                    "#fda58b",
                    "#ebebeb",
                    "#f65731",
                    "#fc805e",
                    "#fda58b",
                    "#ebebeb"
                ]


            }]
    }

    const doughnutStockData = {
        labels: [
            "КОЛЕДИНО",
            "КАЗАНЬ",
            "ШУШАРЫ",
            "ШУШАРЫ",
            "Новосибирск",
            "Санкт-Петербург Ш блок 1"
        ],
        datasets: [
            {
                data: [3200, 50, 100, 1233, 5.640040478121926, 5.571520576438181],
                backgroundColor: [
                    "#f65731",
                    "#fc805e",
                    "#fda58b",
                    "#ebebeb",
                    "#f65731",
                    "#fc805e",
                    "#fda58b",
                    "#ebebeb"
                ],
                hoverBackgroundColor: [
                    "#f65731",
                    "#fc805e",
                    "#fda58b",
                    "#ebebeb",
                    "#f65731",
                    "#fc805e",
                    "#fda58b",
                    "#ebebeb"
                ]


            }]
    }

    const doughnutStockDataOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    padding: 20,
                    font: {
                        size: 8,
                        weight: 'bold'
                    }
                }
            }
        }
    };

    const doughnutBrandDataOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    padding: 20,
                    font: {
                        size: 8,
                        weight: 'bold'
                    }
                }
            }
        }
    };


    const ctx = document.getElementById("main_chart").getContext("2d");
    const mainChart = new Chart(ctx, {
        type: 'bar',
        data: mainChartData,
        options: {
            plugins: {
                legend: {
                    display: false,
                    position: 'bottom',
                },
                tooltip: {
                    yAlign: 'bottom',
                    mode: 'index',
                    callbacks: {},
                    titleFont: {
                        size: 8
                    },
                    titleAlign: 'center',
                    padding: 10
                }
            },
            responsive: true,
            interaction: {
                intersect: false,
            },
            scales: {
                x: {
                    stacked: true,
                    display: true,
                    border: {
                        display: true
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        display: true,
                        color: 'black',
                        padding: 10
                    }
                },
                y: {
                    stacked: false,
                    ticks: {},
                    beginAtZero: true,
                    display: false,
                    grid: {
                        drawBorder: false,
                        drawOnChartArea: false,
                        color: (context) => {
                            const zeroLine = context.tick.value;
                            const gridColor = zeroLine === 0 ? '#666' : '#ccc';
                            return gridColor
                        }
                    },
                },
            },
        },
    })
    const doughnutBrand = document.getElementById("doughnut_brand").getContext("2d")
    const DoughnutChart = new Chart(doughnutBrand, {
        type: 'doughnut',
        data: doughnutBrandData,
        options: doughnutBrandDataOptions
    });
    const doughnutStock = document.getElementById("doughnut_stock").getContext("2d")
    const stockChart = new Chart(doughnutStock, {
        type: 'doughnut',
        data: doughnutStockData,
        options: doughnutStockDataOptions
    });
})

