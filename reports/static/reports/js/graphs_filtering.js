document.addEventListener("DOMContentLoaded", function() {
    const ara1 = document.getElementById('period-filter-wrapper')
    const ara2 = document.getElementById('category-filter-wrapper')
    const ara3 = document.getElementById('brand-filter-wrapper')
    const jsAra1 = JSON.parse(ara1.getAttribute('data-title'))
    const jsAra2 = JSON.parse(ara2.getAttribute('data-title'))
    const jsAra3 = JSON.parse(ara3.getAttribute('data-title'))
    console.log(jsAra1)
    console.log(jsAra2)
    console.log(jsAra3)
    let validPeriods = new Set()
    let validCategories = new Set()
    let validBrands = new Set()

    function formatFate(date) {
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear();
        const formattedDate = `${day}.${month}.${year}`;
        return formattedDate
    }
    function createPeriodLabelElem() {
        jsAra1.forEach((item, index) => {
            let filterLabel = document.createElement('label')
            filterLabel.className = 'graphs-filter_label'
            filterLabel.innerHTML = `
                 <input
                      type="checkbox"
                      checked
                      class="filter_checkbox"
                      id="period-checkbox"
                      data-filter-week="${item.week_num}"
                      data-filter-type="period"
                      data-filter-index="${index}"
                      data-value="${item.week_num}:${item.year}"
                      data-filter-year="${item.year}">
                    <span></span>
                    <p>${item.week_num} неделя (${formatFate(new Date(item.date_from))}-${formatFate(new Date(item.date_to))})</p>
                 </label>
        `
            ara1.appendChild(filterLabel)
        })
    }

    function createCategoryLabelElem() {
        jsAra2.forEach(item => {
            let filterLabel = document.createElement('label')
            filterLabel.className = 'graphs-filter_label'
            filterLabel.innerHTML = `
                 <input
                      type="checkbox"
                      checked
                      class="filter_checkbox"
                      data-filter-type="category"
                      id="category-filter-checkbox"
                      data-filter-category="${item.subject_name}">
                    <span></span>
                    <p>${item.subject_name}</p>
                 </label>
        `
            ara2.appendChild(filterLabel)
        })
    }

    function createBrandLabelELem() {
        jsAra3.forEach(item => {
            let filterLabel = document.createElement('label')
            filterLabel.className = 'graphs-filter_label'
            filterLabel.innerHTML = `
                 <input
                      type="checkbox"
                      checked
                      class="filter_checkbox"
                      data-filter-type="brand"
                      id="brand-filter-checkbox"
                      data-filter-brand="${item.brand_name}">
                    <span></span>
                    <p>${item.brand_name}</p>
                 </label>
        `
            ara3.appendChild(filterLabel)
        })
    }
    createPeriodLabelElem()
    createCategoryLabelElem()
    createBrandLabelELem()

    jsAra1.forEach(item => {
        validPeriods.add(`${item.week_num}:${item.year}`)
        item.subject_names.forEach(subject_name => {
            validCategories.add(subject_name)
        })
        item.brand_names.forEach(brand_name => {
            validBrands.add(brand_name)
        })
    })

    jsAra2.forEach(item => {
        item.week_nums.forEach(week_num => {
            validPeriods.add(week_num)
        })
        validCategories.add(item.subject_name)
        item.brand_names.forEach(brand_name => {
            validBrands.add(brand_name)
        })
    })

    jsAra3.forEach(item => {
        item.week_nums.forEach(week_num => {
            validPeriods.add(week_num)
        })
        item.subject_names.forEach(subject_name => {
            validCategories.add(subject_name)
        })
        validBrands.add(item.brand_name)
    })

    console.log(validPeriods)
    console.log(validCategories)
    console.log(validBrands)

    const allCategoriesCheckbox = document.getElementById('all-category-checkbox')
    const allBrandsCheckbox = document.getElementById('all-brand-checkbox')
    const allTimeCheckbox = document.getElementById('all-checkbox')

    const periodCheckboxInputs = document.querySelectorAll('#period-checkbox')
    const categoryCheckboxInputs = document.querySelectorAll('#category-filter-checkbox')
    const brandCheckboxInputs = document.querySelectorAll('#brand-filter-checkbox')

    const periodCheckboxInputsCount = periodCheckboxInputs.length
    const categoryCheckboxInputsCount = categoryCheckboxInputs.length
    const brandCheckboxInputsCount = brandCheckboxInputs.length

    const graphsWrapperBtn = document.getElementById('graphs-dropbtn')
    const dropdownContent = document.querySelector('.filter-dropdown_content')
    const closeDropDown = document.getElementById('close-dropdown-btn')

    const applyFiltersBtn = document.querySelector('.apply-graphs-filter_btn')

    let checkboxInputsCheckedCount = getCheckedInputsCount(periodCheckboxInputs)
    let categoryCheckboxInputsCheckedCount = getCheckedInputsCount(categoryCheckboxInputs)
    let brandCheckboxInputsCheckedCount = getCheckedInputsCount(brandCheckboxInputs)

    let isDropdownActive = false;

    if (periodCheckboxInputsCount !== checkboxInputsCheckedCount) {
        allTimeCheckbox.checked = false;
    }
    if (categoryCheckboxInputsCount !== categoryCheckboxInputsCheckedCount) {
        allCategoriesCheckbox.checked = false;
    }
    if (brandCheckboxInputsCount !== brandCheckboxInputsCheckedCount) {
        allBrandsCheckbox.checked = false;
    }

    function getCheckedInputsCount(inputs) {
        let inputsCheckedCounter = 0
        inputs.forEach(input => {
            if (input.checked) {
                inputsCheckedCounter += 1
            }
        })
        return inputsCheckedCounter
    }

    function generateFilterDataObject(inputs) {
        const intermediateFilterData = {}
        inputs.forEach(input => {
            if (input.checked) {
                intermediateFilterData[input.getAttribute("data-filter-year")] = []
            }
        })
        inputs.forEach(input => {
            if (input.checked) {
                intermediateFilterData[input.getAttribute("data-filter-year")].push(input.getAttribute("data-filter-week"))
            }
        })
        return intermediateFilterData
    }

    function generateFilterData(inputs, filterType) {
        let filterArray = []
        inputs.forEach((input) => {
            if (filterType === "subject_name" && input.checked) {
                filterArray.push(input.getAttribute("data-filter-category"));
            } else {
                if (input.checked) {
                    filterArray.push(input.getAttribute("data-filter-brand"));
                }
            }
        })
        if (filterArray.length > 0) {
            return `&${filterType}=${filterArray}`
        } else {
            return ''
        }
    }

    function generateFilterQueryString(filterData) {
        let queryString = '';
        for (const key in filterData) {
            queryString += `${key}=${filterData[key]}&`;
        }
        return queryString.slice(0, -1);
    }


    function makeEventListenerForInputs(inputs, checkedInputsCounterElem, inputsCountElem, allCheckboxStatusElem) {
        inputs.forEach(input => {
            input.addEventListener('change', function(e) {
                validCategories.clear()
                validBrands.clear()
                inputs.forEach(input_inner => {
                    if (input_inner.checked && input_inner.getAttribute('data-filter-type') === 'period') {
                        jsAra1[input_inner.getAttribute('data-filter-index')].subject_names.forEach(subject_name => {
                            validCategories.add(subject_name)
                        })
                        jsAra1[input_inner.getAttribute('data-filter-index')].brand_names.forEach(brand_name => {
                            validBrands.add(brand_name)
                        })
                    }
                })
                categoryCheckboxInputs.forEach(input_inner => {
                    if (input_inner.getAttribute('data-filter-type') === 'category' && !validCategories.has(input_inner.getAttribute('data-filter-category'))) {
                        console.log(input_inner.nextElementSibling.nextElementSibling)
                        input_inner.disabled = true
                        input_inner.checked = false
                        input_inner.textDecoration = 'line-through'
                    }
                })
                brandCheckboxInputs.forEach(input_inner => {
                    if (input_inner.getAttribute('data-filter-type') === 'brand' && !validBrands.has(input_inner.getAttribute('data-filter-brand'))) {
                        input_inner.disabled = true
                        input_inner.checked = false
                        input_inner.textDecoration = 'line-through'
                    }
                })
                console.log(validBrands)
                console.log(validCategories)
                if (e.target.checked) {
                    checkedInputsCounterElem += 1
                    allCheckboxStatusElem.checked = inputsCountElem === checkedInputsCounterElem
                } else {
                    checkedInputsCounterElem -= 1
                    allCheckboxStatusElem.checked = inputsCountElem === checkedInputsCounterElem
                }
            })
        })
    }

    function makeEventListenerForAllCheckboxElem(allCheckboxElem, inputs, checkboxInputsCheckedCount) {
        allCheckboxElem.addEventListener('change', function(e) {
            [...inputs].forEach(input => input.checked = e.target.checked);
            checkboxInputsCheckedCount = e.target.checked ? inputs.length : 0;
        })
    }

    graphsWrapperBtn.addEventListener('click', function() {
        dropdownContent.style.display = isDropdownActive ? '' : 'block'
        isDropdownActive = !isDropdownActive
    })

    closeDropDown.addEventListener('click', function () {
        dropdownContent.style.display = ''
        isDropdownActive = !isDropdownActive
    })

    makeEventListenerForAllCheckboxElem(allTimeCheckbox, periodCheckboxInputs, checkboxInputsCheckedCount)
    makeEventListenerForAllCheckboxElem(allCategoriesCheckbox, categoryCheckboxInputs, categoryCheckboxInputsCheckedCount)
    makeEventListenerForAllCheckboxElem(allBrandsCheckbox, brandCheckboxInputs, brandCheckboxInputsCheckedCount)
    makeEventListenerForInputs(periodCheckboxInputs, checkboxInputsCheckedCount, periodCheckboxInputsCount, allTimeCheckbox)
    makeEventListenerForInputs(categoryCheckboxInputs, categoryCheckboxInputsCheckedCount, categoryCheckboxInputsCount, allCategoriesCheckbox)
    makeEventListenerForInputs(brandCheckboxInputs, brandCheckboxInputsCheckedCount, brandCheckboxInputsCount, allBrandsCheckbox)
    generateFilterData(categoryCheckboxInputs, 'subject_name')
    generateFilterData(brandCheckboxInputs, 'brand_name')

    applyFiltersBtn.addEventListener('click', function () {
        const filterData = generateFilterDataObject(periodCheckboxInputs)
        const queryString = Object.keys(filterData).length === 0 ? '' : `${generateFilterQueryString(filterData)}`
        const queryString2 = generateFilterData(categoryCheckboxInputs, 'subject_name')
        const queryString3 = generateFilterData(brandCheckboxInputs, 'brand_name')
        window.location.href = '?' + queryString + queryString2 + queryString3
    })
})