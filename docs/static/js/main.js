// Find the theme control and the document root.
const themeToggle = document.querySelector(".theme-toggle");
const languageToggle = document.querySelector(".language-toggle");
const siteHeader = document.querySelector(".site-header");
const navigationLinks = Array.from(
    document.querySelectorAll(".main-navigation a")
);
const sections = Array.from(
    document.querySelectorAll("main section[id]")
);
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

function getCurrentSection() {
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

    return currentSection;
}

function updateActiveNavigation() {
    const currentSection = getCurrentSection();

    navigationLinks.forEach((link) => {
        const isCurrent = link.hash === `#${currentSection.id}`;
        link.classList.toggle("is-active", isCurrent);

        if (isCurrent) {
            link.setAttribute("aria-current", "location");
        } else {
            link.removeAttribute("aria-current");
        }
    });
}

updateActiveNavigation();
window.addEventListener("scroll", updateActiveNavigation, { passive: true });
window.addEventListener("resize", updateActiveNavigation);

languageToggle.addEventListener("click", (event) => {
    const currentSection = getCurrentSection();
    const destination = new URL(languageToggle.href, window.location.href);
    destination.hash = currentSection.id;

    event.preventDefault();
    window.location.assign(destination.href);
});