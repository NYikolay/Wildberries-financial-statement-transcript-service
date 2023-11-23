const shareInBrandCanvas = document.getElementById("shareInBrandGraph")
const shareInBrandWrapper = document.getElementById("current-share-brand")
const shareInBrandText = shareInBrandWrapper.getElementsByTagName("p")[0]
const shareInBrandDataObject = JSON.parse(shareInBrandCanvas.getAttribute('data-brands-canvas'))

const shareInCategoryCanvas = document.getElementById("shareInCategoryGraph")
const shareInCategoryWrapper = document.getElementById("current-share-category")
const shareInCategoryText = shareInCategoryWrapper.getElementsByTagName("p")[0]
const shareInCategoryDataObject = JSON.parse(shareInCategoryCanvas.getAttribute('data-category-canvas'))

const shareInStockCanvas = document.getElementById("shareShipmentGraph")
const shareInStockWrapper = document.getElementById("current-share-stock")
const shareInStockText = shareInStockWrapper.getElementsByTagName("p")[0]
const shareInStockDataObject = JSON.parse(shareInStockCanvas.getAttribute('data-stock-canvas'))

let currentShareInBrandSelectedElementIndex
let currentShareInCategorySelectedElementIndex
let currentShareInStockSelectedElementIndex

const shareInBrandDataSetArraysObject = {
    labels: [],
    data: []
}

const shareInCategoryDataSetArraysObject = {
    labels: [],
    data: []
}

const shareInStockDataSetArraysObject = {
    labels: [],
    data: []
}

for (let [key, value] of Object.entries(shareInBrandDataObject)) {
    shareInBrandDataSetArraysObject.labels.push(key)
    shareInBrandDataSetArraysObject.data.push(Math.round(value))
}

for (let [key, value] of Object.entries(shareInCategoryDataObject)) {
    shareInCategoryDataSetArraysObject.labels.push(key)
    shareInCategoryDataSetArraysObject.data.push(Math.round(value))
}

for (let [key, value] of Object.entries(shareInStockDataObject)) {
    shareInStockDataSetArraysObject.labels.push(key)
    shareInStockDataSetArraysObject.data.push(Math.round(value))
}

const updateSelectedChartItem = (chart, elementIndex) => {
    const { ctx, data, chartArea: { top, bottom, left, right } } = chart

    const gradientBg = ctx.createLinearGradient(0, top, 0, bottom)
    gradientBg.addColorStop(0, "#FC9E36")
    gradientBg.addColorStop(1, "#FD6DAB")

    chart._metasets[0]._dataset.backgroundColor.forEach((color, index) => {
        if (index === elementIndex) {
            chart._metasets[0]._dataset.backgroundColor[index] = gradientBg
        } else {
            chart._metasets[0]._dataset.backgroundColor[index] = "#373E70"
        }
    })

    chart.update()
}

const showCurrentItemText = (element, text) => {
    element.innerText = text
}

const setInitialChartActivePiece = (chart, values, isCategory, isBrand) => {
    const maxValue = Math.max(...values)
    const maxIndex = values.indexOf(maxValue)

    if (isCategory) {
        currentShareInCategorySelectedElementIndex = maxIndex
        shareInCategoryText.innerText = shareInCategoryDataSetArraysObject.labels[maxIndex]
        showCurrentItemText(shareInCategoryText, shareInCategoryDataSetArraysObject.labels[maxIndex])
    } else if (isBrand) {
        currentShareInBrandSelectedElementIndex = maxIndex
        shareInCategoryText.innerText = shareInBrandDataSetArraysObject.labels[maxIndex]
        showCurrentItemText(shareInBrandText, shareInBrandDataSetArraysObject.labels[maxIndex])
    } else {
        currentShareInStockSelectedElementIndex = maxIndex
        shareInStockText.innerText = shareInStockDataSetArraysObject.labels[maxIndex]
        showCurrentItemText(shareInStockText, shareInStockDataSetArraysObject.labels[maxIndex])
    }

    updateSelectedChartItem(chart, maxIndex)
}


const getCanvasData = (labelText, labels, data, shareItemsCount) => {
    return {
        labels: labels,
        datasets: [{
            label: labelText,
            data: data,
            backgroundColor: Array.from({length: shareItemsCount}, () => "#373E70"),
            borderColor: "transparent",
            hoverBackgroundColor: (context) => {
                if (!context.chart.chartArea) {
                    return
                }

                const {ctx, data, chartArea: {top, bottom, left, right}} = context.chart
                const gradientBg = ctx.createLinearGradient(0, top, 0, bottom)
                gradientBg.addColorStop(0, "#FC9E36")
                gradientBg.addColorStop(1, "#FD6DAB")

                return gradientBg
            },
            spacing: shareItemsCount > 1 ? 6 : 0,
            cutout: '40%'
        }]
    }
}

const shareBrandsData = getCanvasData(
    "Доля бренда в выручке", shareInBrandDataSetArraysObject.labels,
    shareInBrandDataSetArraysObject.data, shareInBrandDataSetArraysObject.data.length
)
const shareCategoryData = getCanvasData(
    "Доля категории в выручке", shareInCategoryDataSetArraysObject.labels,
    shareInCategoryDataSetArraysObject.data, shareInCategoryDataSetArraysObject.data.length
)

const shareStockData = getCanvasData(
    "Доля отгрузок в выручке", shareInStockDataSetArraysObject.labels,
    shareInStockDataSetArraysObject.data, shareInStockDataSetArraysObject.data.length
)

const shareBrandsConfig = {
    type: 'doughnut',
    data: shareBrandsData,
    options: {
        onClick: (click, element, chart) => {
            const currentElementIndex = element[0].index
            currentShareInBrandSelectedElementIndex = currentElementIndex

            updateSelectedChartItem(chart, currentElementIndex)
            showCurrentItemText(shareInBrandText, shareInBrandDataSetArraysObject.labels[currentElementIndex])
        },
        responsive: true,
        tooltips: {
            enabled: false
        },
        plugins: {
            tooltip: {
                enabled: false
            },
            legend: {
                display: false,
            },
            datalabels: {
                formatter: (value, categories) => value > 8 ? `${value}%` : '',
                listeners: {
                    enter: function(context, event) {
                        context.hovered = true;
                        return true;
                    },
                    leave: function(context, event) {
                        context.hovered = false;
                        return true;
                    }
                },
                color: function(context) {
                    return context.active || currentShareInBrandSelectedElementIndex === context.dataIndex ? "#FFFFFF" : "#5C659D";
                },
                font: {
                    family: "'Open Sans', sans-serif",
                    size: 14,
                    weight: "bold"
                }
            }
        }
    },
    plugins: [ChartDataLabels]
}

const shareCategoryConfig = {
    type: 'doughnut',
    data: shareCategoryData,
    options: {
        onClick: (click, element, chart) => {
            const currentElementIndex = element[0].index
            currentShareInCategorySelectedElementIndex = currentElementIndex

            updateSelectedChartItem(chart, currentElementIndex)
            showCurrentItemText(shareInCategoryText, shareInCategoryDataSetArraysObject.labels[currentElementIndex])
        },
        responsive: true,
        tooltips: {
            enabled: false
        },
        plugins: {
            emptyDoughnut: {
                color: 'rgba(255, 128, 0, 0.5)',
                width: 2,
                radiusDecrease: 20
            },
            tooltip: {
                enabled: false
            },
            legend: {
                display: false,
            },
            datalabels: {
                formatter: (value, categories) => value > 8 ? `${value}%` : '',
                color: function(context) {
                    return context.active || currentShareInCategorySelectedElementIndex === context.dataIndex ? "#FFFFFF" : "#5C659D";
                },
                font: {
                    family: "'Open Sans', sans-serif",
                    size: 14,
                    weight: "bold"
                }
            }
        }
    },
    plugins: [ChartDataLabels]
}

const shareStockConfig = {
    type: 'doughnut',
    data: shareStockData,
    options: {
        onClick: (click, element, chart) => {
            const currentElementIndex = element[0].index
            currentShareInStockSelectedElementIndex = currentElementIndex

            updateSelectedChartItem(chart, currentElementIndex)
            showCurrentItemText(shareInStockText, shareInStockDataSetArraysObject.labels[currentElementIndex])
        },
        responsive: true,
        tooltips: {
            enabled: false
        },
        plugins: {
            emptyDoughnut: {
                color: 'rgba(255, 128, 0, 0.5)',
                width: 2,
                radiusDecrease: 20
            },
            tooltip: {
                enabled: false
            },
            legend: {
                display: false,
            },
            datalabels: {
                formatter: (value, categories) => value > 8 ? `${value}%` : '',
                color: function(context) {
                    return context.active || currentShareInStockSelectedElementIndex === context.dataIndex ? "#FFFFFF" : "#5C659D";
                },
                font: {
                    family: "'Open Sans', sans-serif",
                    size: 14,
                    weight: "bold"
                }
            }
        }
    },
    plugins: [ChartDataLabels]
}

const shareInBrandChart = new Chart(shareInBrandCanvas, shareBrandsConfig)
const shareInCategoryChart = new Chart(shareInCategoryCanvas, shareCategoryConfig)
const shareInStockChart = new Chart(shareInStockCanvas, shareStockConfig)

setInitialChartActivePiece(shareInBrandChart, shareInBrandDataSetArraysObject.data, false, true)
setInitialChartActivePiece(shareInCategoryChart, shareInCategoryDataSetArraysObject.data, true, false)
setInitialChartActivePiece(shareInStockChart, shareInCategoryDataSetArraysObject.data, false, false)