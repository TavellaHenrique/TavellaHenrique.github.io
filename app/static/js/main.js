// Find the theme control and the document root.
const themeToggle = document.querySelector(".theme-toggle");
const languagePicker = document.querySelector(".language-picker");
const languageToggle = document.querySelector(".language-toggle");
const languageMenu = document.querySelector(".language-menu");
const languageOptions = Array.from(
    document.querySelectorAll(".language-option")
);
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

if (languagePicker && languageToggle && languageMenu) {
    const toggleLabel = languageToggle.querySelector(".language-toggle-label");

    function setLanguageSelection(languageValue) {
        const selectedOption = languageOptions.find(
            (option) => option.dataset.lang === languageValue
        );

        if (!selectedOption) {
            return;
        }

        languageOptions.forEach((option) => {
            const isSelected = option === selectedOption;
            option.classList.toggle("is-selected", isSelected);
            option.setAttribute("aria-selected", String(isSelected));
        });

        if (toggleLabel) {
            toggleLabel.textContent = selectedOption.dataset.value;
        }
    }

    function closeLanguageMenu() {
        languagePicker.classList.remove("is-open");
        languageToggle.setAttribute("aria-expanded", "false");
    }

    function openLanguageMenu() {
        languagePicker.classList.add("is-open");
        languageToggle.setAttribute("aria-expanded", "true");
    }

    const currentLanguage = document.documentElement.lang.toLowerCase();
    setLanguageSelection(currentLanguage === "pt-br" ? "pt-br" : "en");

    languageToggle.addEventListener("click", (event) => {
        event.stopPropagation();
        const shouldOpen = !languagePicker.classList.contains("is-open");

        if (shouldOpen) {
            openLanguageMenu();
            return;
        }

        closeLanguageMenu();
    });

    languageOptions.forEach((option) => {
        option.addEventListener("click", (event) => {
            event.stopPropagation();
            const selectedLanguage = option.dataset.lang;
            const currentLocation = new URL(window.location.href);
            const destination = new URL(option.dataset.url, window.location.href);
            const currentSection = getCurrentSection();

            destination.hash = currentSection.id;
            setLanguageSelection(selectedLanguage);
            closeLanguageMenu();

            if (selectedLanguage === currentLanguage) {
                return;
            }

            window.location.assign(destination.href);
        });
    });

    document.addEventListener("click", (event) => {
        if (!languagePicker.contains(event.target)) {
            closeLanguageMenu();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && languagePicker.classList.contains("is-open")) {
            closeLanguageMenu();
            languageToggle.focus();
        }
    });

    languageToggle.addEventListener("keydown", (event) => {
        if (event.key === "ArrowDown" && !languagePicker.classList.contains("is-open")) {
            event.preventDefault();
            openLanguageMenu();
            const firstOption = languageOptions[0];
            if (firstOption) {
                firstOption.focus();
            }
        }
    });

    languageMenu.addEventListener("keydown", (event) => {
        const currentIndex = languageOptions.indexOf(document.activeElement);
        if (event.key === "ArrowDown") {
            event.preventDefault();
            const nextIndex = currentIndex < languageOptions.length - 1 ? currentIndex + 1 : 0;
            languageOptions[nextIndex].focus();
        }

        if (event.key === "ArrowUp") {
            event.preventDefault();
            const nextIndex = currentIndex > 0 ? currentIndex - 1 : languageOptions.length - 1;
            languageOptions[nextIndex].focus();
        }

        if (event.key === "Home") {
            event.preventDefault();
            languageOptions[0].focus();
        }

        if (event.key === "End") {
            event.preventDefault();
            languageOptions[languageOptions.length - 1].focus();
        }
    });
}