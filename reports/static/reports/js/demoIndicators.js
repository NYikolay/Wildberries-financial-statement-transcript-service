document.addEventListener("DOMContentLoaded", function () {
    const indicatorItems = document.querySelectorAll(".indicator-item")
    let pastActiveIndicatorItem

    const changeCurrentIndicatorStyles = (indicatorItem) => {
        if (pastActiveIndicatorItem) {
            pastActiveIndicatorItem.classList.remove("active-border")
            const pastIndicatorItemStaticWrapper = pastActiveIndicatorItem.childNodes[1]
            const pastIndicatorItemTitle = pastActiveIndicatorItem.getElementsByTagName('h1')[0]
            const pastIndicatorItemText = pastActiveIndicatorItem.querySelector('.text__accent')
            const pastIndicatorItemSvg = pastActiveIndicatorItem.getElementsByTagName("svg")[0]

            pastActiveIndicatorItem.classList.remove("active-border")
            pastIndicatorItemTitle.classList.add("dark_h1")
            pastIndicatorItemText.classList.add("text__common-normal")
            pastIndicatorItemText.classList.remove("text__accent")

            if (pastIndicatorItemSvg) {
                pastIndicatorItemSvg.style.fill = "#5C659D"
            }

            pastIndicatorItemStaticWrapper.innerHTML = `
                <div style="width: 9px; height: 45px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 36px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 29px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 22px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 27px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 32px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 29px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 36px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 22px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 29px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 36px; background-color: #5C659D;"></div>
                <div style="width: 9px; height: 45px; background-color: #5C659D;"></div>
        `
        }

        const indicatorItemTitle = indicatorItem.querySelector('.dark_h1')
        const indicatorItemText = indicatorItem.querySelector('.text__common-normal')
        const indicatorItemSvg = indicatorItem.getElementsByTagName("svg")[0]

        indicatorItem.classList.add("active-border")
        indicatorItemTitle.classList.remove("dark_h1")
        indicatorItemText.classList.remove("text__common-normal")
        indicatorItemText.classList.add("text__accent")
        if (indicatorItemSvg) {
            indicatorItemSvg.style.fill = "#FFFFFF"
        }
        indicatorItem.childNodes[1].innerHTML = `
                <div style="width: 9px; height: 45px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 36px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 29px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 22px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 27px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 32px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 29px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 36px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 22px; background: linear-gradient(180deg, #00C5FF 0%, #0072FF 100%);"></div>
                <div style="width: 9px; height: 29px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 36px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
                <div style="width: 9px; height: 45px; background: linear-gradient(180deg, #FC9E36 0%, #FD6DAB 100%);"></div>
    `
        pastActiveIndicatorItem = indicatorItem
    }

    indicatorItems.forEach((item, index) => {
        const isActive = item.getAttribute("data-is-active") === "true"

        if (isActive) {
            changeCurrentIndicatorStyles(item)
        }

        item.addEventListener("click", (event) => {
            changeCurrentIndicatorStyles(item)
        })
    })

})