document.addEventListener("DOMContentLoaded", function () {
    let costInputs = document.querySelectorAll("[id='cost_input']");
    let productCostDates = document.querySelectorAll("[id='product_cost_date']")
    let deleteCostObjButton = document.querySelector('.delete_cost-input')
    const addCostButton = document.getElementById('add_cost')
    const parentCostFooter = document.querySelector('.product_inputs-wrapper')
    let costInputsItems = document.querySelectorAll('.product_cost-item')
    let inputsValidationMap = new Map()

    for (let i = 0; i < costInputs.length; i++) {
        if (costInputs[i].value) {
            inputsValidationMap.set(`costInput${i}`, 1)
        }
    }

    for (let i = 0; i < productCostDates.length; i++) {
        if (productCostDates[i].value) {
            inputsValidationMap.set(`dateInput${i}`, 1)
        }
    }

    function setMaxAndMinValuesToDateInput() {
        for (let i = 0; i < productCostDates.length; i++) {
            if (i === 0 && productCostDates.length === 1) {
                productCostDates[i].max = new Date().toLocaleDateString('en-ca')
            }
            if (i !== 0) {
                productCostDates[i].max = new Date().toLocaleDateString('en-ca')
                const pastDateValue = productCostDates[i - 1].valueAsDate
                pastDateValue.setDate(pastDateValue.getDate() + 1)
                productCostDates[i].min = pastDateValue.toLocaleDateString('en-ca')

            }
        }
    }

    function generateValidationForInput() {
        for (let i = 0; i < costInputs.length; i++) {
            // costInputs[i].addEventListener('input', function(event){
            // });
            costInputs[i].addEventListener('change', function () {
                if (this.value !== '') {
                    this.style.border = '1px solid #dbdbdb'
                    if (inputsValidationMap.has(`costInput${i}`) === false) {
                        inputsValidationMap.set(`costInput${i}`, 1)
                    }

                } else if (this.value === '') {
                    if (inputsValidationMap.has(`costInput${i}`) === true) {
                        inputsValidationMap.delete(`costInput${i}`)
                    }
                }
            }, false)
        }
    }

    function changeValuesForDateInput() {
        for (let i = 0; i < productCostDates.length; i++) {
            productCostDates[i].addEventListener('change', function () {
                if (this.value !== '') {
                    this.style.border = '1px solid #dbdbdb'
                    if (inputsValidationMap.has(`dateInput${i}`) === false) {
                        inputsValidationMap.set(`dateInput${i}`, 1)
                    }
                    if (i < productCostDates.length - 1) {
                        const currentDate = this.valueAsDate
                        currentDate.setDate(currentDate.getDate() + 1)
                        productCostDates[i + 1].min = currentDate.toLocaleDateString('en-ca')
                    }
                    if (i !== 0) {
                        const currentMinDate = this.valueAsDate
                        currentMinDate.setDate(currentMinDate.getDate() - 1)
                        productCostDates[i - 1].max = currentMinDate.toLocaleDateString('en-ca')
                    }

                } else if (this.value === '') {
                    if (inputsValidationMap.has(`dateInput${i}`) === true) {
                        inputsValidationMap.delete(`dateInput${i}`)
                    }
                    productCostDates[i].max = new Date().toLocaleDateString('en-ca')
                }
            }, false)
        }
    }


    function isAvailableButton(fn) {
        return function (...args) {
            if ((costInputsItems.length * 2) === inputsValidationMap.size) {
                return fn(...args)
            } else {
                for (let i = 0; i < costInputsItems.length; i++) {
                    if (inputsValidationMap.has(`costInput${i}`) === false) {
                        costInputs[i].style.border = '1px solid #EF8061'
                    }
                    if (inputsValidationMap.has(`dateInput${i}`) === false) {
                        productCostDates[i].style.border = '1px solid #EF8061'
                    }
                }
            }
        }
    }


    function createCostItem() {
        let inputItem = document.createElement('div');
        inputItem.className = 'product_cost-item'
        inputItem.innerHTML = `
                            <div class="product_input-wrapper">
                                <input type="number" class="cost_input" min="0" name="cost_input" step="0.01" id="cost_input">
                                <p>Себестоимость</p>
                            </div>
                            <div class="product_input-wrapper">
                                <input class="date_input" name="product_cost_date" id="product_cost_date" type="date">
                                <p>Дата начала действия</p>
                            </div>
            `
        parentCostFooter.appendChild(inputItem)

        costInputs = document.querySelectorAll("[id='cost_input']");
        productCostDates = document.querySelectorAll("[id='product_cost_date']")
        costInputsItems = document.querySelectorAll('.product_cost-item')

        generateValidationForInput()
        changeValuesForDateInput()
        addDeleteButtonForInputItem()
        setMaxAndMinValuesToDateInput()
    }

    function deletePenultimateButton(btn) {
        for (let i = 0; i < btn.length; i++) {
            if (i !== btn.length - 1) {
                btn[i].remove()
            }
        }

    }

    function addDeleteButtonForInputItem() {

        if (costInputsItems.length !== 1) {
            const lastInputItem = costInputsItems[costInputsItems.length - 1]
            let deleteInputItemButton = document.createElement('button')
            deleteInputItemButton.className = 'delete_cost-input'
            deleteInputItemButton.innerHTML = 'удалить'
            deleteInputItemButton.type = 'button'
            deleteInputItemButton.style.color = '#ff8364'

            lastInputItem.appendChild(deleteInputItemButton)

            penultimateDeleteButtons = document.querySelectorAll('.delete_cost-input')

            deletePenultimateButton(penultimateDeleteButtons)

            deleteCostObjButton = document.querySelector('.delete_cost-input')
            deleteCostObjButton.addEventListener('click', function () {
                this.parentElement.remove()

                costInputsItems = document.querySelectorAll('.product_cost-item')

                if ((costInputsItems.length * 2) !== inputsValidationMap.size) {
                    if (inputsValidationMap.has(`costInput${costInputsItems.length}`) === true) {
                        inputsValidationMap.delete(`costInput${costInputsItems.length}`)
                    }
                    if (inputsValidationMap.has(`dateInput${costInputsItems.length}`) === true) {
                        inputsValidationMap.delete(`dateInput${costInputsItems.length}`)
                    }
                }

                if (costInputsItems.length < 3 && addCostButton.style.display === 'none') {
                    addCostButton.style.display = 'inline-block'
                }
                addDeleteButtonForInputItem()
            })
        }
    }

    addDeleteButtonForInputItem()
    generateValidationForInput()
    changeValuesForDateInput()
    setMaxAndMinValuesToDateInput()

    addCostButton.addEventListener('click', isAvailableButton(createCostItem))


    const createNetCostForm = document.querySelector('.product_edit-form')

    createNetCostForm.addEventListener('submit', function (evt) {
        let costInputsItems = document.querySelectorAll('.product_cost-item')

        let isValidationError = false

        evt.preventDefault();

        costInputsItems.forEach(function (item, i, arr) {

            costInputValue = item.children[0].children[0]
            costInputDate = item.children[1].children[0]


            if (costInputValue.value && !costInputDate.value) {
                isValidationError = true
                costInputDate.style.border = '1px solid #EF8061'
            } else if (costInputDate.value && !costInputValue.value) {
                isValidationError = true
                costInputValue.style.border = '1px solid #EF8061'
            }


        })

        if (!isValidationError) {
            this.submit();
        }
    })
})