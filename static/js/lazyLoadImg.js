document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll('img[data-src]')

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    }

    const handleImg = (smImage, observer) => {
        smImage.forEach(smImgSingle => {
            if (smImgSingle.intersectionRatio > 0) {
                loadImage(smImgSingle.target)
            }
        })
    }

    const loadImage = image => {
        image.src = image.dataset.src
        image.removeAttribute('data-src')
        observer.unobserve(image)

    }

    const observer = new IntersectionObserver(handleImg, observerOptions)

    images.forEach(img => {
        observer.observe(img)
    })
})