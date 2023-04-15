document.addEventListener("DOMContentLoaded", function() {
    const graphsWrapperBtn = document.getElementById('graphs-dropbtn')
    const dropdownContent = document.querySelector('.filter-dropdown_content')
    const closeDropDown = document.getElementById('close-dropdown-btn')

    const periodCheckboxInputs = document.querySelectorAll('#period-checkbox')
    const categoryCheckboxInputs = document.querySelectorAll('#category-filter-checkbox')
    const brandCheckboxInputs = document.querySelectorAll('#brand-filter-checkbox')
    const applyFiltersBtn = document.querySelector('.apply-graphs-filter_btn')
    const resetFiltersBtn = document.querySelector('.reset-graphs-filter_btn')

    const allCategoriesFilterCheckbox = document.getElementById('all-category-checkbox')
    const allBrandsFilterCheckbox = document.getElementById('all-brand-checkbox')
    const allPeriodFilterCheckbox = document.getElementById('all-checkbox')

    const periodCheckboxInputsCount = periodCheckboxInputs.length
    const categoryCheckboxInputsCount = categoryCheckboxInputs.length
    const brandCheckboxInputsCount = brandCheckboxInputs.length

    let periodCheckboxInputsCheckedCount = getCheckedInputsCount(periodCheckboxInputs)
    let categoryCheckboxInputsCheckedCount = getCheckedInputsCount(categoryCheckboxInputs)
    let brandCheckboxInputsCheckedCount = getCheckedInputsCount(brandCheckboxInputs)

    let validPeriodFilters = new Set()
    let validCategoryFilters = new Set()
    let validBrandFilters = new Set()
    let isDropdownActive = false

    let inputsBlockedByPeriodFilter = new Set()
    let inputsBlockedByCategoryFilter = new Set()
    let inputsBlockedByBrandFilter = new Set()


    graphsWrapperBtn.addEventListener('click', function() {
        dropdownContent.style.display = isDropdownActive ? '' : 'block'
        isDropdownActive = !isDropdownActive
    })

    closeDropDown.addEventListener('click', function () {
        dropdownContent.style.display = ''
        isDropdownActive = !isDropdownActive
    })

    if (periodCheckboxInputsCount !== periodCheckboxInputsCheckedCount) {
        allPeriodFilterCheckbox.checked = false;
    }

    if (categoryCheckboxInputsCheckedCount !== categoryCheckboxInputsCount) {
        allCategoriesFilterCheckbox.checked = false;
    }

    if (brandCheckboxInputsCheckedCount !== brandCheckboxInputsCount) {
        allBrandsFilterCheckbox.checked = false;
    }

    function getCheckedInputsCount(inputs) {
        return [...inputs].filter(input => input.checked).length;
    }

    function setValidPeriodFilters(inputs) {
        inputs.forEach(input => {
            if (input.checked && !input.disabled) {
                const subjectNames = JSON.parse(input.getAttribute('data-subject-names'))
                const brandNames = JSON.parse(input.getAttribute('data-brand-names'))

                subjectNames.forEach(subjectName => {
                    validCategoryFilters.add(subjectName)
                })
                brandNames.forEach(brandName => {
                    validBrandFilters.add(brandName)
                })
            }
        })
    }

    function setValidBrandFilters(inputs) {
        inputs.forEach(input => {
            if (input.checked || (input.disabled && inputsBlockedByCategoryFilter.has(input))) {
                const brandNames = JSON.parse(input.getAttribute('data-brand-names'))
                brandNames.forEach(brandName => {
                    validBrandFilters.add(brandName)
                })
            }
        })
    }

    function setValidCategoryFilters(inputs) {
        inputs.forEach(input => {
            if (input.checked || (input.disabled && inputsBlockedByBrandFilter.has(input))) {
                const subjectNames = JSON.parse(input.getAttribute('data-subject-names'))

                subjectNames.forEach(subjectName => {
                    validCategoryFilters.add(subjectName)
                })
            }
        })
    }

    function setStylesForBlockedInput(input) {
        input.disabled = true
        input.nextElementSibling.nextElementSibling.style.color = '#9c9a9a'
        input.nextElementSibling.nextElementSibling.style.textDecoration = 'line-through'
    }

    function setStylesForValidInput(input) {
        input.disabled = false
        input.nextElementSibling.nextElementSibling.style.color = 'black'
        input.nextElementSibling.nextElementSibling.style.textDecoration = ''
    }

    function clearValidFiltersSet() {
        validCategoryFilters.clear()
        validBrandFilters.clear()
    }


    function validateByPeriodFilterInputs(inputs) {
        inputs.forEach(input => {
            const filterType = input.getAttribute('data-filter-type')
            if (
                (
                    (filterType === 'category' && !validCategoryFilters.has(input.getAttribute('data-filter-category')))
                    || (filterType === 'brand' && !validBrandFilters.has(input.getAttribute('data-filter-brand')))
                ) && !inputsBlockedByCategoryFilter.has(input) && !inputsBlockedByBrandFilter.has(input)
            ) {
                inputsBlockedByPeriodFilter.add(input)
                setStylesForBlockedInput(input)

            } else if (input.disabled && inputsBlockedByPeriodFilter.has(input)) {
                inputsBlockedByPeriodFilter.delete(input)
                setStylesForValidInput(input)

            }
        })
    }

    function validateBrandFilterInputs(inputs) {
        inputs.forEach(input => {
            const filterBrand = input.getAttribute('data-filter-brand');

            if (!validBrandFilters.has(filterBrand) && !inputsBlockedByPeriodFilter.has(input) && !inputsBlockedByBrandFilter.has(input)) {
                inputsBlockedByCategoryFilter.add(input)
                setStylesForBlockedInput(input)

            } else if (input.disabled && inputsBlockedByCategoryFilter.has(input)) {
                inputsBlockedByCategoryFilter.delete(input)
                setStylesForValidInput(input)

            }
        })
    }

    function validateCategoryFilterInputs(inputs) {
        inputs.forEach(input => {
            const filterCategory = input.getAttribute('data-filter-category')
            if (!validCategoryFilters.has(filterCategory) && !inputsBlockedByPeriodFilter.has(input) && !inputsBlockedByCategoryFilter.has(input)) {
                inputsBlockedByBrandFilter.add(input)
                setStylesForBlockedInput(input)

            } else if (input.disabled && inputsBlockedByBrandFilter.has(input)) {
                inputsBlockedByBrandFilter.delete(input)
                setStylesForValidInput(input)
            }
        })
    }

    let incrementCheckedCounter = (counterType) => {
        if (counterType === 'period') {
            periodCheckboxInputsCheckedCount++
            allPeriodFilterCheckbox.checked = periodCheckboxInputsCount === periodCheckboxInputsCheckedCount
        } else if (counterType === 'category') {
            categoryCheckboxInputsCheckedCount++
            allCategoriesFilterCheckbox.checked = categoryCheckboxInputsCount === categoryCheckboxInputsCheckedCount
        } else {
            brandCheckboxInputsCheckedCount++
            allBrandsFilterCheckbox.checked = brandCheckboxInputsCount === brandCheckboxInputsCheckedCount
        }
    }
    let decreaseCheckedCounter = (counterType) => {
        if (counterType === 'period') {
            periodCheckboxInputsCheckedCount--
            allPeriodFilterCheckbox.checked = periodCheckboxInputsCount === periodCheckboxInputsCheckedCount
        } else if (counterType === 'category') {
            categoryCheckboxInputsCheckedCount--
            allCategoriesFilterCheckbox.checked = categoryCheckboxInputsCount === categoryCheckboxInputsCheckedCount
        } else {
            brandCheckboxInputsCheckedCount--
            allBrandsFilterCheckbox.checked = brandCheckboxInputsCount === brandCheckboxInputsCheckedCount
        }
    }

    let setCheckedCounterToZero = (counterType) => {
        if (counterType === 'period') {
            periodCheckboxInputsCheckedCount = 0
        } else if (counterType === 'category') {
            categoryCheckboxInputsCheckedCount = 0
        } else {
            brandCheckboxInputsCheckedCount = 0
        }
    }

    let setCheckedCounter = (counterType) => {
        if (counterType === 'period') {
            periodCheckboxInputsCheckedCount = periodCheckboxInputsCount
        } else if (counterType === 'category') {
            categoryCheckboxInputsCheckedCount = categoryCheckboxInputsCount
        } else {
            brandCheckboxInputsCheckedCount = brandCheckboxInputsCount
        }
    }


    function addEventListenerToInput(input) {
        input.addEventListener('change', function(event) {
            clearValidFiltersSet()

            if (input.getAttribute('data-filter-type') === 'period') {
                input.checked ? incrementCheckedCounter('period') : decreaseCheckedCounter('period')

                setValidPeriodFilters(periodCheckboxInputs)
                validateByPeriodFilterInputs(Array.prototype.concat.call(...categoryCheckboxInputs , ...brandCheckboxInputs))

            } else if (input.getAttribute('data-filter-type') === 'category') {
                input.checked ? incrementCheckedCounter('category') : decreaseCheckedCounter('category')

                setValidBrandFilters(categoryCheckboxInputs)
                validateBrandFilterInputs(brandCheckboxInputs)

            } else {
                input.checked ? incrementCheckedCounter('brand') : decreaseCheckedCounter('brand')

                setValidCategoryFilters(brandCheckboxInputs)
                validateCategoryFilterInputs(categoryCheckboxInputs)

            }
        })
    }

    function addEventListenerForAllCheckboxInput(allCheckboxElem, inputs, filterType) {
        allCheckboxElem.addEventListener('change', function(e) {

            [...inputs].forEach(input => {
                if (!input.disabled) {
                    input.checked = e.target.checked
                }
            });

            clearValidFiltersSet()
            if (filterType === 'period') {
                e.target.checked ? setCheckedCounter('period') : setCheckedCounterToZero('period')
                setValidPeriodFilters(periodCheckboxInputs)
                validateByPeriodFilterInputs(Array.prototype.concat.call(...categoryCheckboxInputs , ...brandCheckboxInputs))

            } else if (filterType === 'category' && inputsBlockedByBrandFilter.size === 0) {
                e.target.checked ? setCheckedCounter('category') : setCheckedCounterToZero('category')
                setValidBrandFilters(categoryCheckboxInputs)
                validateBrandFilterInputs(brandCheckboxInputs)

            } else if (filterType === 'brand' && inputsBlockedByCategoryFilter.size === 0) {
                e.target.checked ? setCheckedCounter('brand') : setCheckedCounterToZero('brand')
                setValidCategoryFilters(brandCheckboxInputs)
                validateCategoryFilterInputs(categoryCheckboxInputs)

            }
        })
    }

    function resetFilters() {
        [inputsBlockedByPeriodFilter,
            inputsBlockedByCategoryFilter,
            inputsBlockedByBrandFilter,
            validBrandFilters,
            validCategoryFilters,
            validPeriodFilters].forEach(collection => collection.clear());

        [allCategoriesFilterCheckbox,
            allBrandsFilterCheckbox,
            allPeriodFilterCheckbox,
            ...categoryCheckboxInputs,
            ...brandCheckboxInputs,
            ...periodCheckboxInputs].forEach(input => {
            input.checked = true;
            setStylesForValidInput(input);
        });

        [periodCheckboxInputsCheckedCount,
            categoryCheckboxInputsCheckedCount,
            brandCheckboxInputsCheckedCount] = [0, 0, 0];
    }

    function handleInputs(inputs) {
        inputs.forEach(input => {
            addEventListenerToInput(input)
        })
    }

    function generatePeriodFilterDataObject(inputs) {
        const intermediateFilterData = {};
        inputs.forEach((input) => {
            if (input.checked && !input.disabled) {
                const filterYear = input.getAttribute("data-filter-year");
                const filterWeek = input.getAttribute("data-filter-week");
                if (!intermediateFilterData[filterYear]) {
                    intermediateFilterData[filterYear] = [filterWeek];
                } else {
                    intermediateFilterData[filterYear].push(filterWeek);
                }
            }
        });
        return intermediateFilterData;
    }


    function generatePeriodQueryString(filterData) {
        let queryString = '';
        for (const key in filterData) {
            queryString += `${key}=${filterData[key]}&`;
        }
        return queryString.slice(0, -1);
    }

    function generateQueryString(inputs, filterType) {
        let filterArray= []
        inputs.forEach((input) => {
            if (filterType === "subject_name" && input.checked && !input.disabled) {
                filterArray.push(input.getAttribute("data-filter-category"));
            } else if (input.checked && !input.disabled) {
                filterArray.push(input.getAttribute("data-filter-brand"));
            }
        })
        if (filterArray.length > 0) {
            return `&${filterType}=${filterArray}`
        } else {
            return ''
        }
    }

    setValidPeriodFilters(periodCheckboxInputs)
    validateByPeriodFilterInputs(Array.prototype.concat.call(...categoryCheckboxInputs , ...brandCheckboxInputs))
    setValidCategoryFilters(brandCheckboxInputs)
    validateCategoryFilterInputs(categoryCheckboxInputs)
    setValidBrandFilters(categoryCheckboxInputs)
    validateBrandFilterInputs(brandCheckboxInputs)

    handleInputs(periodCheckboxInputs)
    handleInputs(categoryCheckboxInputs)
    handleInputs(brandCheckboxInputs)
    addEventListenerForAllCheckboxInput(allCategoriesFilterCheckbox, categoryCheckboxInputs, 'category', categoryCheckboxInputsCheckedCount)
    addEventListenerForAllCheckboxInput(allBrandsFilterCheckbox, brandCheckboxInputs, 'brand', brandCheckboxInputsCheckedCount)
    addEventListenerForAllCheckboxInput(allPeriodFilterCheckbox, periodCheckboxInputs, 'period', periodCheckboxInputsCheckedCount)

    applyFiltersBtn.addEventListener('click', function () {
        let periodQueryString = periodCheckboxInputsCheckedCount ? generatePeriodQueryString(generatePeriodFilterDataObject(periodCheckboxInputs)) : ''
        const categoryQueryString = categoryCheckboxInputsCheckedCount ? generateQueryString(categoryCheckboxInputs, 'subject_name') : ''
        const brandQueryString = brandCheckboxInputsCheckedCount ? generateQueryString(brandCheckboxInputs, 'brand_name') : ''
        if (periodCheckboxInputsCheckedCount === periodCheckboxInputsCount) {
            periodQueryString = ''
        }
        // const url = '/check_filters/'
        // fetch(url, {
        //     method: "GET",
        //     headers: {
        //         "X-Requested-With": "XMLHttpRequest",
        //     }
        // })
        //     .then(response => response.json())
        //     .then(data => {
        //         console.log(data);
        //     });
        if (
            periodCheckboxInputsCheckedCount === periodCheckboxInputsCount
            && categoryCheckboxInputsCheckedCount === categoryCheckboxInputsCount
            && brandCheckboxInputsCheckedCount === brandCheckboxInputsCount
        ) {
            window.location.href = `?`
        } else {
            window.location.href = `?${periodQueryString}${categoryQueryString}${brandQueryString}`
        }
    })

})