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

images.forEach(img => {
    observer.observe(img);
})

const productWrapper = document.querySelector('#products_block')

function insertAfter(elem, refElem) {
    return refElem.parentNode.insertBefore(elem, refElem.nextSibling);
}

function sortHigher(dataAttr) {
    let sorted = [...productWrapper.children].sort((a, b) => {
        return b.dataset[dataAttr] - a.dataset[dataAttr];
    });

    parent.innerHTML = '';

    sorted.forEach(child => {
        productWrapper.appendChild(child);
    });
}


function sortLower(dataAttr) {
    let sorted = [...productWrapper.children].sort((a, b) => {
        return a.dataset[dataAttr] - b.dataset[dataAttr];
    });

    parent.innerHTML = '';

    sorted.forEach(child => {
        productWrapper.appendChild(child);
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


function shareSort() {
    if (shareSorted) {
        sortLower('share')
        shareSorted = false
    } else {
        sortHigher('share')
        shareSorted = true
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