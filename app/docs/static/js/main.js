// Find the theme control and the document root.
const themeToggle = document.querySelector(".theme-toggle");
const rootElement = document.documentElement;

// Restore the saved theme or use light mode by default.
const savedTheme = localStorage.getItem("portfolio-theme");
const initialTheme = savedTheme === "dark" ? "dark" : "light";

rootElement.dataset.theme = initialTheme;

// Update the theme and its accessibility state.
function updateTheme(theme) {
    rootElement.dataset.theme = theme;

    const isDark = theme === "dark";

    themeToggle.setAttribute("aria-pressed", String(isDark));
    localStorage.setItem("portfolio-theme", theme);
}

// Initialize the theme control.
updateTheme(initialTheme);

// Switch between light and dark themes when clicked.
themeToggle.addEventListener("click", () => {
    const nextTheme =
        rootElement.dataset.theme === "dark" ? "light" : "dark";

    updateTheme(nextTheme);
});