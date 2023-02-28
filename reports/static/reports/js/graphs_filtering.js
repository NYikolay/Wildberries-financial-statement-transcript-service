document.addEventListener("DOMContentLoaded", function() {
    const checkboxInputs = document.querySelectorAll('#period-checkbox')
    const graphsWrapperBtn = document.getElementById('graphs-dropbtn')
    const dropdownContent = document.querySelector('.filter-dropdown_content')
    const applyFiltersBtn = document.querySelector('.apply-graphs-filter_btn')
    const allTimeCheckbox = document.getElementById('all-checkbox')
    const checkboxInputsCount = checkboxInputs.length
    let checkboxInputsCheckedCount = getCheckedInputsCount(checkboxInputs)
    let isDropdownActive = false;

    if (checkboxInputsCount !== checkboxInputsCheckedCount) {
        allTimeCheckbox.checked = false;
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

    function generateFilterQueryString(filterData) {
        let queryString = '';
        for (const key in filterData) {
            queryString += `${key}=${filterData[key]}&`;
        }
        return queryString.slice(0, -1);
    }


    graphsWrapperBtn.addEventListener('click', function() {
        dropdownContent.style.display = isDropdownActive ? '' : 'block'
        isDropdownActive = !isDropdownActive
    })

    allTimeCheckbox.addEventListener('change', function(e) {
        [...checkboxInputs].forEach(input => input.checked = e.target.checked);
        checkboxInputsCheckedCount = e.target.checked ? checkboxInputs.length : 0;
    })

    checkboxInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            if (e.target.checked) {
                checkboxInputsCheckedCount += 1
                allTimeCheckbox.checked = checkboxInputsCount === checkboxInputsCheckedCount
            } else {
                checkboxInputsCheckedCount -= 1
                allTimeCheckbox.checked = checkboxInputsCount === checkboxInputsCheckedCount
            }
        })
    })

    applyFiltersBtn.addEventListener('click', function () {
        const filterData = generateFilterDataObject(checkboxInputs)
        const queryString = Object.keys(filterData).length === 0 ? '' : `?${generateFilterQueryString(filterData)}`
        window.location.href = '/' + queryString
    })
})