const productsData = document.getElementById('products_block');
const productsArray = JSON.parse(productsData.getAttribute('data-title'));
const emptyImageUrl = '/static/images/empty_photo2.png'
let salesSorted = false;
let returnsSorted = false;
let revenueSorted = false;
let shareSorted = false;
let marginalitySorted = false;
for (let i = 0; i < productsArray.length; i++) {
    let productWrapper = document.createElement('div')
    productWrapper.className = 'product_wrapper'
    productWrapper.setAttribute('data-sales', productsArray[i].sales_quantity_value)
    productWrapper.setAttribute('data-returns', productsArray[i].returns_quantity_value)
    productWrapper.setAttribute('data-revenue', productsArray[i].revenue_by_article)
    productWrapper.setAttribute('data-share', productsArray[i].share_in_profits)
    productWrapper.setAttribute('data-marginality', productsArray[i].product_marginality)
    const image =  productsArray[i].image === null ? emptyImageUrl  : productsArray[i].image
    productWrapper.innerHTML =
        `                    
                    <div 
                    class="product_item"
                    >
                        <img class="product_img" data-src="${image}" alt="">
                        <div class="text-wrapper">
                            <p class="product_statistic">${Number.parseInt(productsArray[i].sales_quantity_value).toLocaleString('ru')}</p>
                        </div>
                        <div class="text-wrapper">
                            <p class="product_statistic">${Number.parseInt(productsArray[i].returns_quantity_value).toLocaleString('ru')}</p>
                        </div>
                        <div class="text-wrapper">
                            <p class="product_statistic">${Number.parseInt(productsArray[i].revenue_by_article).toLocaleString('ru')}</p>
                        </div>
                        <div class="text-wrapper">
                            <p class="product_statistic">${productsArray[i].share_in_profits}%</p>
                        </div>
                        <div class="text-wrapper">
                            <p class="product_statistic">${productsArray[i].product_marginality}%</p>
                        </div>
                    </div>
                    <p class="barcode">Артикул: ${productsArray[i].nm_id}</p>
        `
    productsData.appendChild(productWrapper)
    productsData.removeAttribute('data-title')
}

const images = document.querySelectorAll('img[data-src]')

const options = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
}

function handleImg(myImg, observer) {
    myImg.forEach(myImgSingle => {
        if (myImgSingle.intersectionRatio > 0) {
            loadImage(myImgSingle.target);
        }
    })
}

function loadImage(image) {
    image.src = image.dataset.src;
    image.removeAttribute('data-src');
    observer.unobserve(image)
}

const observer = new IntersectionObserver(handleImg, options)

images.forEach(img => {
    observer.observe(img);
})

const productWrapper = document.querySelector('#products_block')

function insertAfter(elem, refElem) {
    return refElem.parentNode.insertBefore(elem, refElem.nextSibling);
}

function descSortItemsByAttr(attr) {
    for (let i = 0; i < productWrapper.children.length; i++) {
        for (let j = i; j < productWrapper.children.length; j++) {
            if (+productWrapper.children[i].getAttribute(attr) > +productWrapper.children[j].getAttribute(attr)) {
                let replacedNode = productWrapper.replaceChild(productWrapper.children[j], productWrapper.children[i]);
                insertAfter(replacedNode, productWrapper.children[i]);
            }
        }
    }
}

function sortItemsByAttr(attr) {
    for (let i = 0; i < productWrapper.children.length; i++) {
        for (let j = i; j < productWrapper.children.length; j++) {
            if (+productWrapper.children[i].getAttribute(attr) < +productWrapper.children[j].getAttribute(attr)) {
                let replacedNode = productWrapper.replaceChild(productWrapper.children[j], productWrapper.children[i]);
                insertAfter(replacedNode, productWrapper.children[i]);
            }
        }
    }
}

function salesSort() {
    if (salesSorted) {
        descSortItemsByAttr('data-sales')
        salesSorted = false
    } else {
        sortItemsByAttr('data-sales')
        salesSorted = true
    }
}

function returnsSort() {
    if (returnsSorted) {
        descSortItemsByAttr('data-returns')
        returnsSorted = false
    } else {
        sortItemsByAttr('data-returns')
        returnsSorted = true
    }
}

function revenueSort() {
    if (revenueSorted) {
        descSortItemsByAttr('data-revenue')
        revenueSorted = false
    } else {
        sortItemsByAttr('data-revenue')
        revenueSorted = true
    }
}


function shareSort() {
    if (shareSorted) {
        descSortItemsByAttr('data-share')
        shareSorted = false
    } else {
        sortItemsByAttr('data-share')
        shareSorted = true
    }
}

function marginalitySort() {
    if (marginalitySorted) {
        descSortItemsByAttr('data-marginality')
        marginalitySorted = false
    } else {
        sortItemsByAttr('data-marginality')
        marginalitySorted = true
    }
}