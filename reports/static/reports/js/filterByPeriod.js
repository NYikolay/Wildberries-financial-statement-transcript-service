document.addEventListener("DOMContentLoaded", function () {
    const openFiltersContentButton = document.getElementById("filter-button")
    const filtersContentWrapper = document.getElementById("filter-content-wrapper")
    const closeFilterContentButton = document.getElementById("close-filters")
    const allPeriodFilterCheckbox = document.getElementById("filter-all-checkbox")
    const applyFiltersBtn = document.getElementById("apply-filters")

    const periodCheckboxInputs = document.querySelectorAll('[name="filter_checkbox"]')
    const periodCheckboxInputsCount = periodCheckboxInputs.length
    let periodCheckboxInputsCheckedCount = getCheckedInputsCount(periodCheckboxInputs)

    function getCheckedInputsCount (inputs) {
        return [...inputs].filter(input => input.checked).length
    }

    openFiltersContentButton.addEventListener("click", (event) => {
        if (filtersContentWrapper.classList.contains("hidden")) {
            filtersContentWrapper.classList.remove("hidden")
        } else {
            filtersContentWrapper.classList.add("hidden")
        }
    })

    closeFilterContentButton.addEventListener("click", (event) => {
        filtersContentWrapper.classList.add("hidden")
    })

    document.addEventListener('click', function(event) {
        if (!filtersContentWrapper.contains(event.target) && !openFiltersContentButton.contains(event.target)) {
            filtersContentWrapper.classList.add('hidden')
        }
    });

    if (periodCheckboxInputsCount !== periodCheckboxInputsCheckedCount) {
        allPeriodFilterCheckbox.checked = false;
    }

    const incrementCheckedCounter = (counterType) => {
        if (counterType === 'period') {
            periodCheckboxInputsCheckedCount++
            allPeriodFilterCheckbox.checked = periodCheckboxInputsCount === periodCheckboxInputsCheckedCount
        }
    }
    const decreaseCheckedCounter = (counterType) => {
        if (counterType === 'period') {
            periodCheckboxInputsCheckedCount--
            allPeriodFilterCheckbox.checked = periodCheckboxInputsCount === periodCheckboxInputsCheckedCount
        }
    }

    const setCheckedCounterToZero = (counterType) => {
        if (counterType === 'period') {periodCheckboxInputsCheckedCount = 0}
    }

    const setCheckedCounter = (counterType) => {
        if (counterType === 'period') {periodCheckboxInputsCheckedCount = periodCheckboxInputsCount}
    }

    periodCheckboxInputs.forEach(input => {
        input.addEventListener("change", (event) => {
            if (input.getAttribute('data-filter-type') === 'period') {
                input.checked ? incrementCheckedCounter('period') : decreaseCheckedCounter('period')
            }
        })
    })

    allPeriodFilterCheckbox.addEventListener('change', function(event) {

        [...periodCheckboxInputs].forEach(input => { input.checked = event.target.checked});

        event.target.checked ? setCheckedCounter('period') : setCheckedCounterToZero('period')
    })

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

    applyFiltersBtn.addEventListener('click', function () {
        let periodQueryString = periodCheckboxInputsCheckedCount ? generatePeriodQueryString(generatePeriodFilterDataObject(periodCheckboxInputs)) : ''

        window.location.href = `?${periodQueryString}`
    })

})