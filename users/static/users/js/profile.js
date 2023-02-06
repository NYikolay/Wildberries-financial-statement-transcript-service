document.addEventListener("DOMContentLoaded", function () {
    let taxRates = document.querySelectorAll("[id='tax_rate']");
    let commencementDates = document.querySelectorAll("[id='commencement_date']")
    let deleteTaxObjButton = document.querySelector('.delete_tax-input')
    const addTaxButton = document.getElementById('add_tax')
    const parentTaxFooter = document.querySelector('.company_edit-footer')
    let taxInputsItems = document.querySelectorAll('.tax_inputs-item')
    let inputsValidationMap = new Map()

    for (let i = 0; i < taxRates.length; i++) {
        if (taxRates[i].value) {
            inputsValidationMap.set(`percentInput${i}`, 1)
        }
    }

    for (let i = 0; i < commencementDates.length; i++) {
        if (commencementDates[i].value) {
            inputsValidationMap.set(`dateInput${i}`, 1)
        }
    }

    function setMaxAndMinValuesToDateInput() {
        for (let i = 0; i < commencementDates.length; i++) {
            if (i === 0 && commencementDates.length === 1) {
                commencementDates[i].max = new Date().toLocaleDateString('en-ca')
            }
            if (i !== 0) {
                commencementDates[i].max = new Date().toLocaleDateString('en-ca')
                const pastDateValue = commencementDates[i - 1].valueAsDate
                pastDateValue.setDate(pastDateValue.getDate() + 1)
                commencementDates[i].min = pastDateValue.toLocaleDateString('en-ca')

            }
        }
    }

    function generateValidationForInput() {
        for (let i = 0; i < taxRates.length; i++) {
            taxRates[i].addEventListener('input', function (event) {
                if (event.target.value >= 100) {
                    event.target.value = 100;
                }
            });
            taxRates[i].addEventListener('change', function () {
                if (this.value !== '') {
                    this.style.border = '1px solid #dbdbdb'
                    if (inputsValidationMap.has(`percentInput${i}`) === false) {
                        inputsValidationMap.set(`percentInput${i}`, 1)
                    }

                } else if (this.value === '') {
                    if (inputsValidationMap.has(`percentInput${i}`) === true) {
                        inputsValidationMap.delete(`percentInput${i}`)
                    }
                }
            }, false)
        }
    }

    function changeBorderForDateInput() {
        for (let i = 0; i < commencementDates.length; i++) {
            commencementDates[i].addEventListener('change', function () {
                if (this.value !== '') {
                    this.style.border = '1px solid #dbdbdb'
                    if (inputsValidationMap.has(`dateInput${i}`) === false) {
                        inputsValidationMap.set(`dateInput${i}`, 1)
                    }
                    if (i < commencementDates.length - 1) {
                        const currentDate = this.valueAsDate
                        currentDate.setDate(currentDate.getDate() + 1)
                        commencementDates[i + 1].min = currentDate.toLocaleDateString('en-ca')
                    }
                    if (i !== 0) {
                        const currentMinDate = this.valueAsDate
                        currentMinDate.setDate(currentMinDate.getDate() - 1)
                        commencementDates[i - 1].max = currentMinDate.toLocaleDateString('en-ca')
                    }

                } else if (this.value === '') {
                    if (inputsValidationMap.has(`dateInput${i}`) === true) {
                        inputsValidationMap.delete(`dateInput${i}`)
                    }
                    commencementDates[i].max = new Date().toLocaleDateString('en-ca')
                }
            }, false)
        }
    }


    function isAvailableButton(fn) {
        return function (...args) {
            if ((taxInputsItems.length * 2) === inputsValidationMap.size) {
                return fn(...args)
            } else {
                for (let i = 0; i < taxInputsItems.length; i++) {
                    if (inputsValidationMap.has(`percentInput${i}`) === false) {
                        taxRates[i].style.border = '1px solid #EF8061'
                    }
                    if (inputsValidationMap.has(`dateInput${i}`) === false) {
                        commencementDates[i].style.border = '1px solid #EF8061'
                    }
                }
            }
        }
    }


    function createTaxItem() {
        let inputItem = document.createElement('div');
        inputItem.className = 'tax_inputs-item'
        inputItem.id = 'tax_input'
        inputItem.innerHTML = `
                <div class="input-item">
                    <input type="number" id="tax_rate" placeholder="%" min="0" name="tax_rate" style="width: 90px;">
                    <label for="tax_rate">Ставка налога</label>
                </div>
                <div class="input-item">
                     <input type="date" value="" id="commencement_date" name="commencement_date">
                     <label for="commencement_date">Дата начала действия</label>
                </div>
            `
        parentTaxFooter.appendChild(inputItem)

        taxRates = document.querySelectorAll("[id='tax_rate']");
        commencementDates = document.querySelectorAll("[id='commencement_date']")
        taxInputsItems = document.querySelectorAll('.tax_inputs-item')

        if (taxInputsItems.length === 3) {
            this.removeEventListener('click', createTaxItem)
            addTaxButton.style.display = 'none'
        }

        generateValidationForInput()
        changeBorderForDateInput()
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

        if (taxInputsItems.length !== 1) {
            const lastInputItem = taxInputsItems[taxInputsItems.length - 1]
            let deleteInputItemButton = document.createElement('button')
            deleteInputItemButton.className = 'delete_tax-input'
            deleteInputItemButton.innerHTML = 'удалить'
            deleteInputItemButton.type = 'button'
            deleteInputItemButton.style.color = '#ff8364'

            lastInputItem.appendChild(deleteInputItemButton)

            PenultimateDeleteButtons = document.querySelectorAll('.delete_tax-input')

            deletePenultimateButton(PenultimateDeleteButtons)

            deleteTaxObjButton = document.querySelector('.delete_tax-input')
            deleteTaxObjButton.addEventListener('click', function () {
                this.parentElement.remove()

                taxInputsItems = document.querySelectorAll('.tax_inputs-item')

                if ((taxInputsItems.length * 2) !== inputsValidationMap.size) {
                    if (inputsValidationMap.has(`percentInput${taxInputsItems.length}`) === true) {
                        inputsValidationMap.delete(`percentInput${taxInputsItems.length}`)
                    }
                    if (inputsValidationMap.has(`dateInput${taxInputsItems.length}`) === true) {
                        inputsValidationMap.delete(`dateInput${taxInputsItems.length}`)
                    }
                }

                if (taxInputsItems.length < 3 && addTaxButton.style.display === 'none') {
                    addTaxButton.style.display = 'inline-block'
                }
                addDeleteButtonForInputItem()
            })
        }
    }

    addDeleteButtonForInputItem()
    generateValidationForInput()
    changeBorderForDateInput()
    setMaxAndMinValuesToDateInput()

    addTaxButton.addEventListener('click', isAvailableButton(createTaxItem))


    const createApiKeyForm = document.querySelector('.company_edit-form')
    createApiKeyForm.addEventListener('submit', function (evt) {
        const taxInputs = document.querySelectorAll('.tax_inputs-item')
        let isValidationError = false

        evt.preventDefault();

        taxInputs.forEach(function (item, i, arr) {

            taxInputPercent = item.children[0].children[0]
            taxInputDate = item.children[1].children[0]

            if (taxInputPercent.value && !taxInputDate.value) {
                isValidationError = true
                taxInputDate.style.border = '1px solid #EF8061'
            } else if (taxInputDate.value && !taxInputPercent.value) {
                isValidationError = true
                taxInputPercent.style.border = '1px solid #EF8061'
            }


        })

        if (!isValidationError) {
            this.submit();
        }
    })
})