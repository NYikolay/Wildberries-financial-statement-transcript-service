const productsData = document.getElementById('products-block');
const productsArray = JSON.parse(productsData.getAttribute('data-products'));

const newProductsArray = {
    "A": [],
    "B": [],
    "C": [],
    "AX": [],
    "AY": [],
    "BX": [],
    "AZ": [],
    "BY": [],
    "CX": [],
    "BZ": [],
    "CY": [],
    "CZ": [],
}

for (let i = 0; i < productsArray.length; i++) {
    const abcGroup = productsArray[i].group_abc
    const abcxyzGroup = productsArray[i].final_group
    newProductsArray[abcGroup].push(productsArray[i])
    if (abcxyzGroup) {
        newProductsArray[abcxyzGroup].push(productsArray[i])
    }
}

const emptyImageUrl = '/static/images/empty_photo2.png'

const filterButtons = document.querySelectorAll('.abc-xyz__filter__item')
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

function insertAfter(elem, refElem) {
    return refElem.parentNode.insertBefore(elem, refElem.nextSibling);
}

createProductBlocks('A')

function setActiveButton(button) {
    button.classList.add('abc-xyz__filter__item-active');
}

function resetInactiveButtons(buttons, activeButton) {
    for (const button of buttons) {
        if (button !== activeButton) {
            button.classList.remove('abc-xyz__filter__item-active');
        }
    }
}

function removeChildNodes(parent) {
    while (parent.firstElementChild) {
        parent.removeChild(parent.firstElementChild);
    }
}

function createProductBlocks(condition) {
    let counter = 0
    for (let i = 0; i < newProductsArray[condition].length; i++) {
        counter += 1
        let productWrapper = document.createElement('div')
        productWrapper.className = 'product_item'
        productWrapper.setAttribute('data-abc-group', newProductsArray[condition][i].group_abc)
        productWrapper.setAttribute('data-abx-xyz-group', newProductsArray[condition][i].final_group)
        const image =  newProductsArray[condition][i].image === null ? emptyImageUrl  : newProductsArray[condition][i].image
        productWrapper.innerHTML =
            `                   
                        <img class="product_img" data-src="${image}" alt="">
                        <div class="product-info__wrapper">
                            <p class="product__name">${newProductsArray[condition][i].product_name}</p>
                            <p class="product__barcode">Артикул: ${newProductsArray[condition][i].nm_id}</p>
                            <p class="product__barcode">Баркод: ${newProductsArray[condition][i].barcode}</p>
                        </div> 
                    `
        productsData.appendChild(productWrapper)
        productsData.removeAttribute('data-products')
    }
    if (!counter) {
        productsData.innerHTML =
            `<h3 style="font-size: 8px; color: #9c9a9a; text-transform:uppercase;">в выбранной группе отсутствуют товары</h3>`
    }
    images = document.querySelectorAll('img[data-src]')
    images.forEach(img => {
        observer.observe(img);
    })
}

for (const button of filterButtons) {
    const buttonGroup = button.getAttribute('data-group');
    if (newProductsArray[buttonGroup].length > 0) {
        button.classList.add('abc-xyz__filter__item-fill');
    }
    button.addEventListener('click', function (event) {
        setActiveButton(button);
        resetInactiveButtons(filterButtons, button);
        removeChildNodes(productsData);
        createProductBlocks(buttonGroup);
    });
}
