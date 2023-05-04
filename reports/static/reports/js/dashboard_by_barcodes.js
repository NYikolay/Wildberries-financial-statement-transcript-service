const barcodesItemsWrapper = document.querySelector('.barcodes__items-wrapper')
const reportByBarcodesData = JSON.parse(barcodesItemsWrapper.getAttribute('data-report'))
const emptyImageUrl = '/static/images/empty_photo2.png'

let salesSorted = false
let returnsSorted = false
let revenueSorted = false
let marginalitySorted = false
let groupSorted = false
let commissionSorted = false
let logisticSorted = false
let penaltySorted = false
let additionalPaymentSorted = false
let totalPayableSorted = false
let barcodeSorted = false

let images = document.querySelectorAll('img[data-src]')

const options = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
}

const handleImg = (myImg, observer) => {
    myImg.forEach(myImgSingle => {
        if (myImgSingle.intersectionRatio > 0) {
            loadImage(myImgSingle.target);
        }
    })
};

const loadImage = image => {
    image.src = image.dataset.src
    image.removeAttribute('data-src');
    observer.unobserve(image);

};
const observer = new IntersectionObserver(handleImg, options)


function createBarcodesItems() {
    for (let i = 0; i < reportByBarcodesData.length; i++) {
        let barcodeItemWrapper = document.createElement('div')
        barcodeItemWrapper.className = 'barcode__item'
        barcodeItemWrapper.setAttribute('data-barcode', reportByBarcodesData[i].barcode)
        barcodeItemWrapper.setAttribute('data-marginality', reportByBarcodesData[i].product_marginality)
        barcodeItemWrapper.setAttribute('data-group', reportByBarcodesData[i].final_group)
        barcodeItemWrapper.setAttribute('data-revenue', reportByBarcodesData[i].revenue_by_article)
        barcodeItemWrapper.setAttribute('data-sales', reportByBarcodesData[i].sales_quantity)
        barcodeItemWrapper.setAttribute('data-returns', reportByBarcodesData[i].returns_quantity)
        barcodeItemWrapper.setAttribute('data-commission', reportByBarcodesData[i].commission)
        barcodeItemWrapper.setAttribute('data-logistic', reportByBarcodesData[i].logistic_sum)
        barcodeItemWrapper.setAttribute('data-penalty', reportByBarcodesData[i].penalty_sum)
        barcodeItemWrapper.setAttribute('data-addpay', reportByBarcodesData[i].additional_payment_sum)
        barcodeItemWrapper.setAttribute('data-totalpay', reportByBarcodesData[i].total_payable)

        const image =  reportByBarcodesData[i].image === null ? emptyImageUrl  : reportByBarcodesData[i].image
        barcodeItemWrapper.innerHTML = `
                <img data-src="${image}" alt="" class="barcode__img">
                <div class="barcode__item-data-wrapper">
                    <div class="barcode__item-data__value">
                        <p>${reportByBarcodesData[i].barcode}</p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p>${Math.round(reportByBarcodesData[i].product_marginality)}%</p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p style="background-color: #ffd8cc; border-radius: 50%; padding: 9px">
                            ${reportByBarcodesData[i].final_group === null ? '-' : reportByBarcodesData[i].final_group}
                        </p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p>${Math.round(reportByBarcodesData[i].revenue_by_article).toLocaleString('ru')}</p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p>${Math.round(reportByBarcodesData[i].sales_quantity).toLocaleString('ru')}</p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p>${Math.round(reportByBarcodesData[i].returns_quantity).toLocaleString('ru')}</p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p>${Math.round(reportByBarcodesData[i].commission).toLocaleString('ru')}</p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p>${Math.round(reportByBarcodesData[i].logistic_sum).toLocaleString('ru')}</p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p>${Math.round(reportByBarcodesData[i].penalty_sum).toLocaleString('ru')}</p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p>${Math.round(reportByBarcodesData[i].additional_payment_sum).toLocaleString('ru')}</p>
                    </div>
                    <div class="barcode__item-data__value">
                        <p style="color: #ff8364">${Math.round(reportByBarcodesData[i].total_payable).toLocaleString('ru')}</p>
                    </div>
                </div>
    `
        barcodesItemsWrapper.appendChild(barcodeItemWrapper)
        barcodesItemsWrapper.removeAttribute('data-report')
    }
    images = document.querySelectorAll('img[data-src]')
    images.forEach(img => {
        observer.observe(img);
    })
}

createBarcodesItems()

const barcodesWrapper = document.querySelector('#barcodes-block')

function insertAfter(elem, refElem) {
    return refElem.parentNode.insertBefore(elem, refElem.nextSibling);
}

function sortHigher(dataAttr) {
    let sorted = [...barcodesWrapper.children].sort((a, b) => {
        return b.dataset[dataAttr] - a.dataset[dataAttr];
    });

    parent.innerHTML = '';

    sorted.forEach(child => {
        barcodesWrapper.appendChild(child);
    });
}


function sortLower(dataAttr) {
    let sorted = [...barcodesWrapper.children].sort((a, b) => {
        return a.dataset[dataAttr] - b.dataset[dataAttr];
    });

    parent.innerHTML = '';

    sorted.forEach(child => {
        barcodesWrapper.appendChild(child);
    });
}


function sortStrHigher(dataAttr) {
    let sorted = [...barcodesWrapper.children].sort((a, b) => {
        return b.dataset['group'].localeCompare(a.dataset['group']);
    });

    parent.innerHTML = '';

    sorted.forEach(child => {
        barcodesWrapper.appendChild(child);
    });
}


function sortStrLower(dataAttr) {
    let sorted = [...barcodesWrapper.children].sort((a, b) => {
        return a.dataset['group'].localeCompare(b.dataset['group']);
    });

    parent.innerHTML = '';

    sorted.forEach(child => {
        barcodesWrapper.appendChild(child);
    });
}


function salesSort() {
    if (salesSorted) {
        sortLower('sales')
        salesSorted = false
    } else {
        sortHigher('sales')
        salesSorted = true
    }
}

function barcodeSort() {
    if (barcodeSorted) {
        sortLower('barcode')
        barcodeSorted = false
    } else {
        sortHigher('barcode')
        barcodeSorted = true
    }
}

function returnsSort() {
    if (returnsSorted) {
        sortLower('returns')
        returnsSorted = false
    } else {
        sortHigher('returns')
        returnsSorted = true
    }
}

function revenueSort() {
    if (revenueSorted) {
        sortLower('revenue')
        revenueSorted = false
    } else {
        sortHigher('revenue')
        revenueSorted = true
    }
}

function marginalitySort() {
    if (marginalitySorted) {
        sortLower('marginality')
        marginalitySorted = false
    } else {
        sortHigher('marginality')
        marginalitySorted = true
    }
}

function groupSort() {
    if (groupSorted) {
        sortStrLower('group')
        groupSorted = false
    } else {
        sortStrHigher('group')
        groupSorted = true
    }
}

function commissionSort() {
    if (commissionSorted) {
        sortLower('commission')
        commissionSorted = false
    } else {
        sortHigher('commission')
        commissionSorted = true
    }
}

function logisticSort() {
    if (logisticSorted) {
        sortLower('logistic')
        logisticSorted = false
    } else {
        sortHigher('logistic')
        logisticSorted = true
    }
}

function penaltySort() {
    if (penaltySorted) {
        sortLower('penalty')
        penaltySorted = false
    } else {
        sortHigher('penalty')
        penaltySorted = true
    }
}


function additionalPaymentSort() {
    if (additionalPaymentSorted) {
        sortLower('addpay')
        additionalPaymentSorted = false
    } else {
        sortHigher('addpay')
        additionalPaymentSorted = true
    }
}

function totalPayableSort() {
    if (totalPayableSorted) {
        sortLower('totalpay')
        totalPayableSorted = false
    } else {
        sortHigher('totalpay')
        totalPayableSorted = true
    }
}
