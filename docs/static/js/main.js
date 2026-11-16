// Find the theme control and the document root.
const themeToggle = document.querySelector(".theme-toggle");
const languageToggle = document.querySelector(".language-toggle");
const siteHeader = document.querySelector(".site-header");
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

languageToggle.addEventListener("click", (event) => {
    const sections = Array.from(
        document.querySelectorAll("main section[id]")
    );
    const headerHeight = siteHeader.getBoundingClientRect().height;
    const isAtPageBottom =
        window.scrollY + window.innerHeight >=
        document.documentElement.scrollHeight - 2;
    let currentSection = isAtPageBottom
        ? sections[sections.length - 1]
        : sections[0];

    if (!isAtPageBottom) {
        sections.forEach((section) => {
            if (section.getBoundingClientRect().top <= headerHeight + 48) {
                currentSection = section;
            }
        });
    }

    const destination = new URL(languageToggle.href, window.location.href);
    destination.hash = currentSection.id;

    event.preventDefault();
    window.location.assign(destination.href);
});