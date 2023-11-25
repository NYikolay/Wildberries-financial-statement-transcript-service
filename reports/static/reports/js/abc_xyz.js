const productsWrapper = document.getElementById("products-wrapper")
const productsDataArray = JSON.parse(productsWrapper.getAttribute('data-products'))
const groupOpenButtons = document.querySelectorAll('.abc__xyz-item')
const initialGroupButton = document.querySelector('[data-group="A"]')
let lastOpenedGroupButton

const newProductsDataArray = {
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
    "None": []
}

const emptyImageHtml = `
         <div class="empty__product-image__wrapper">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="40" height="40" fill="#32396B"/>
                <path fill-rule="evenodd" clip-rule="evenodd" d="M10.591 10.2286C10.8958 9.92379 11.3901 9.92379 11.6949 10.2286L12.9415 11.4752C12.9885 11.4731 13.0358 11.472 13.0833 11.472H26.8996C28.6024 11.472 29.9829 12.8524 29.9829 14.5553V25.3663C29.9829 26.2348 29.6238 27.0194 29.046 27.5798L29.7714 28.3051C30.0762 28.61 30.0762 29.1042 29.7714 29.409C29.4665 29.7139 28.9723 29.7139 28.6675 29.409L27.6228 28.3643C27.3908 28.4201 27.1486 28.4496 26.8996 28.4496H13.0833C11.3804 28.4496 10 27.0692 10 25.3663V14.5553C10 13.5174 10.5128 12.5993 11.2989 12.0405L10.591 11.3325C10.2861 11.0277 10.2861 10.5335 10.591 10.2286ZM11.5612 14.5553C11.5612 13.9462 11.9189 13.4207 12.4358 13.1774L15.0054 15.747C14.3402 15.9837 13.8639 16.6189 13.8639 17.3654C13.8639 18.3138 14.6327 19.0827 15.5812 19.0827C16.3276 19.0827 16.9629 18.6064 17.1995 17.9411L20.2503 20.9918L18.5083 23.2978L17.2303 21.7137C16.4315 20.7238 14.952 20.6416 14.0485 21.537L11.5612 24.0024V14.5553ZM14.4994 13.0332L27.9419 26.4756C28.2372 26.198 28.4217 25.8037 28.4217 25.3663V24.9747L22.2551 18.7704L22.7235 18.5363L23.3674 18.3997L23.8943 18.3411L24.5578 18.4582L25.1237 18.7119L25.5921 19.0632L26.0604 19.5705L28.4217 22.4754V14.5553C28.4217 13.7147 27.7402 13.0332 26.8996 13.0332H14.4994Z" fill="#5C659D"/>
            </svg>
         </div>
`

for (let i = 0; i < productsDataArray.length; i++) {
    const abcGroup = productsDataArray[i].group_abc
    const abcxyzGroup = productsDataArray[i].final_group
    newProductsDataArray[abcGroup].push(productsDataArray[i])
    if (abcxyzGroup) {
        newProductsDataArray[abcxyzGroup].push(productsDataArray[i])
    }
}

const removeChildNodes = (parent) => {
    while (parent.firstElementChild) {
        parent.removeChild(parent.firstElementChild);
    }
}


const createProductItems = (productGroup) => {
    for (let i = 0; i < newProductsDataArray[productGroup].length; i++) {
        let productItem = document.createElement("div")
        productItem.classList.add("product__item")
        productItem.classList.add("product__item-width")

        const image = newProductsDataArray[productGroup][i].image

        productItem.innerHTML = `
            ${ image ? `<img class="product-image" src="${image}" alt="Артикул ${newProductsDataArray[productGroup][i].nm_id}">` : emptyImageHtml}
            <div class="product__item-description">
                <div class="product__item-description__inner">
                    <p class="text__accent-bold">${newProductsDataArray[productGroup][i].product_name}</p>
                </div>
                <div>
                    <p class="text__accent">Баркод: ${newProductsDataArray[productGroup][i].barcode}</p>
                    <p class="text__accent">Артикул: ${newProductsDataArray[productGroup][i].nm_id}</p>
                    <p class="text__accent">Размер: ${newProductsDataArray[productGroup][i].ts_name}</p>
                </div>
            </div>
        `

        productsWrapper.appendChild(productItem)
    }
}

const setGroupButtonContentActiveStyles = (button) => {
    const titles = button.getElementsByTagName("h1")
    const svg = button.getElementsByTagName("path")[0]

    svg.classList.remove("img-svg")
    svg.classList.add("active-svg")

    for (let i = 0; i < titles.length; i++) {
        titles[i].classList.remove("dark_h1")
    }
}

const removeGroupButtonContentActiveStyles = (button) => {
    const titles = button.getElementsByTagName("h1")
    const svg = button.getElementsByTagName("path")[0]

    svg.classList.remove("active-svg")
    svg.classList.add("img-svg")

    for (let i = 0; i < titles.length; i++) {
        titles[i].classList.add("dark_h1")
    }
}

const renderInitialGroup = () => {
    lastOpenedGroupButton = initialGroupButton
    const buttonGroup = initialGroupButton.getAttribute('data-group')

    initialGroupButton.classList.add("active-border")
    setGroupButtonContentActiveStyles(initialGroupButton)
    createProductItems(buttonGroup)
}

groupOpenButtons.forEach((button) => {
    const buttonGroup = button.getAttribute('data-group')

    button.addEventListener("click", event => {
        lastOpenedGroupButton.classList.remove("active-border")
        removeGroupButtonContentActiveStyles(lastOpenedGroupButton)

        lastOpenedGroupButton = button

        button.classList.add("active-border")
        setGroupButtonContentActiveStyles(button)

        removeChildNodes(productsWrapper)
        createProductItems(buttonGroup)
    })
})

renderInitialGroup()
