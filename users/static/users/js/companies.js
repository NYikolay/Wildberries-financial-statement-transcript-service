document.addEventListener("DOMContentLoaded", function () {
    const deleteCompanyButtons = document.querySelectorAll("#delete-company")

    for (let i = 0; i < deleteCompanyButtons.length; i++) {
        const currentButton = deleteCompanyButtons[i]
        const deleteCompanyModalContainer = currentButton.querySelector(".delete__company-modal__container")
        const cancelDeleteButton = deleteCompanyModalContainer.querySelector("#cancel-company-delete")

        currentButton.addEventListener("click", (event) => {
            deleteCompanyModalContainer.style.visibility = "visible"
            currentButton.style.cursor = "default"
        })

        cancelDeleteButton.addEventListener("click", (event) => {
            event.stopPropagation();
            deleteCompanyModalContainer.style.visibility = "hidden"
        })

        document.addEventListener('click', function(event) {
            if (!deleteCompanyModalContainer.contains(event.target) && !currentButton.contains(event.target)) {
                deleteCompanyModalContainer.style.visibility = 'hidden'
            }
        });
    }
})