document.addEventListener("DOMContentLoaded", function() {
    const openCreateNetCostFormButton = document.getElementById('open-net-cost-form')
    const createNetCostFormWrapper = document.getElementById('create-net-cost-from-wrapper')
    const closeCreateNetCostFormButton = document.getElementById('close-net-cost-form')

    openCreateNetCostFormButton.addEventListener("click", (event) => {
        openCreateNetCostFormButton.classList.add("hidden")
        createNetCostFormWrapper.classList.remove("hidden")
    })

    closeCreateNetCostFormButton.addEventListener("click", (event) => {
        openCreateNetCostFormButton.classList.remove("hidden")
        createNetCostFormWrapper.classList.add("hidden")
    })
});