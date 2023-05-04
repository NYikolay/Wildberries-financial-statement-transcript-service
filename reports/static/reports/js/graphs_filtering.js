document.addEventListener("DOMContentLoaded", function() {
    const graphsWrapperBtn = document.getElementById('graphs-dropbtn')
    const dropdownContent = document.querySelector('.filter-dropdown_content')
    const closeDropDown = document.getElementById('close-dropdown-btn')

    const periodCheckboxInputs = document.querySelectorAll('#period-checkbox')
    const applyFiltersBtn = document.querySelector('.apply-graphs-filter_btn')

    const allPeriodFilterCheckbox = document.getElementById('all-checkbox')
    const periodCheckboxInputsCount = periodCheckboxInputs.length
    let periodCheckboxInputsCheckedCount = getCheckedInputsCount(periodCheckboxInputs)

    const changeReportInput = document.getElementById('change-report')

    let isDropdownActive = false


    changeReportInput.addEventListener('change', function () {
        window.location.href = changeReportInput.getAttribute('data-target-url')
    })

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

    function getCheckedInputsCount(inputs) {
        return [...inputs].filter(input => input.checked).length;
    }

    let incrementCheckedCounter = (counterType) => {
        if (counterType === 'period') {
            periodCheckboxInputsCheckedCount++
            allPeriodFilterCheckbox.checked = periodCheckboxInputsCount === periodCheckboxInputsCheckedCount
        }
    }
    let decreaseCheckedCounter = (counterType) => {
        if (counterType === 'period') {
            periodCheckboxInputsCheckedCount--
            allPeriodFilterCheckbox.checked = periodCheckboxInputsCount === periodCheckboxInputsCheckedCount
        }
    }

    let setCheckedCounterToZero = (counterType) => {
        if (counterType === 'period') {periodCheckboxInputsCheckedCount = 0}
    }

    let setCheckedCounter = (counterType) => {
        if (counterType === 'period') {periodCheckboxInputsCheckedCount = periodCheckboxInputsCount}
    }


    function addEventListenerToInput(input) {
        input.addEventListener('change', function(event) {
            if (input.getAttribute('data-filter-type') === 'period') {
                input.checked ? incrementCheckedCounter('period') : decreaseCheckedCounter('period')
            }
        })
    }

    function addEventListenerForAllCheckboxInput(allCheckboxElem, inputs, filterType) {
        allCheckboxElem.addEventListener('change', function(e) {

            [...inputs].forEach(input => { input.checked = e.target.checked});

            if (filterType === 'period') {
                e.target.checked ? setCheckedCounter('period') : setCheckedCounterToZero('period')
            }
        })
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

    handleInputs(periodCheckboxInputs)
    addEventListenerForAllCheckboxInput(allPeriodFilterCheckbox, periodCheckboxInputs, 'period', periodCheckboxInputsCheckedCount)

    applyFiltersBtn.addEventListener('click', function () {
        let periodQueryString = periodCheckboxInputsCheckedCount ? generatePeriodQueryString(generatePeriodFilterDataObject(periodCheckboxInputs)) : ''

        window.location.href = `?${periodQueryString}`
    })

})