function changeTheme(event) {
    const colorTheme = event.checked ? "light" : "dark";
    const themeLabel = document.querySelector('#theme-label');

    localStorage.setItem("color-theme", colorTheme);

    if (colorTheme === "light") {
         document.body.setAttribute('data-color-theme', colorTheme);
        event.checked = true;
    } else {
        document.body.setAttribute('data-color-theme', colorTheme);
        event.checked = false;
    }

    themeLabel.innerHTML = colorTheme === "light" ? "Тёмная тема" : "Светлая тема";
}

const setColorTheme = () => {
    const changeThemeInput = document.querySelector('#theme-checkbox');
    const themeLabel = document.querySelector('#theme-label');
    const currentTheme = localStorage.getItem("color-theme");

    if (!currentTheme || currentTheme === "dark") {
        document.body.setAttribute('data-color-theme', 'dark');
        changeThemeInput.checked = false;
        themeLabel.innerHTML = "Светлая тема";
    } else {
        document.body.setAttribute('data-color-theme', 'light');
        changeThemeInput.checked = true;
        themeLabel.innerHTML = "Тёмная тема";
    }
}

setColorTheme();