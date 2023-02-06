document.addEventListener("DOMContentLoaded", function () {
    const deleteCompanyForm = document.querySelector('.delete_company-form')
    const deleteWarningCompanyWrapper = document.getElementById('warning_wrapper')
    const deleteWarningContainer = document.querySelector('.delete_warning-container')

    deleteCompanyForm.addEventListener('submit', function (evt) {
        evt.preventDefault();
        deleteWarningCompanyWrapper.style.display = 'block';
        const cancelBtn = document.getElementById('cancel_btn')
        const acceptBtn = document.getElementById('accept_btn')

        cancelBtn.addEventListener('click', function () {
            deleteWarningCompanyWrapper.style.display = 'none';
        })
        acceptBtn.addEventListener('click', function () {
            deleteWarningCompanyWrapper.style.display = 'none';
            deleteCompanyForm.submit();
        })
    })

    document.addEventListener('click', function (e) {
        const target = e.target
        const itsWrapper = target == deleteWarningContainer || deleteWarningContainer.contains(target);
        const itsButton = target == deleteCompanyForm || deleteCompanyForm.contains(target);
        if (!itsWrapper && !itsButton) {
            deleteWarningCompanyWrapper.style.display = 'none';
        }
    })
})