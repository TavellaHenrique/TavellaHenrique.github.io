// Find the theme and language controls.
const themeToggle = document.querySelector(".theme-toggle");
const languagePicker = document.querySelector(".language-picker");
const languageToggle = document.querySelector(".language-toggle");
const languageMenu = document.querySelector(".language-menu");
const languageOptions = Array.from(
    document.querySelectorAll(".language-option")
);
const rootElement = document.documentElement;

// Restore the saved theme or use light mode by default.
const savedTheme = localStorage.getItem("portfolio-theme");
const initialTheme = savedTheme === "dark" ? "dark" : "light";

// Apply the initial theme.
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

// Switch themes when the control is clicked.
themeToggle.addEventListener("click", () => {
    const nextTheme =
        rootElement.dataset.theme === "dark" ? "light" : "dark";

    updateTheme(nextTheme);
});

// Initialize the language picker when its elements are available.
if (languagePicker && languageToggle && languageMenu) {
    const toggleLabel = languageToggle.querySelector(".language-toggle-label");

    // Close the language menu and update its accessibility state.
    function closeLanguageMenu() {
        languagePicker.classList.remove("is-open");
        languageToggle.setAttribute("aria-expanded", "false");
    }

    // Open the language menu and update its accessibility state.
    function openLanguageMenu() {
        languagePicker.classList.add("is-open");
        languageToggle.setAttribute("aria-expanded", "true");
    }

    // Set the currently active language label.
    const currentLanguage = rootElement.lang.toLowerCase();

    if (toggleLabel) {
        toggleLabel.textContent = currentLanguage === "pt-br" ? "PT-BR" : "EN";
    }

    // Toggle the language menu when its button is clicked.
    languageToggle.addEventListener("click", (event) => {
        event.stopPropagation();

        const isOpen = languagePicker.classList.contains("is-open");

        if (isOpen) {
            closeLanguageMenu();
        } else {
            openLanguageMenu();
        }
    });

    // Close the menu when a language link is selected.
    languageOptions.forEach((option) => {
        option.addEventListener("click", () => {
            closeLanguageMenu();
        });
    });

    // Close the menu when clicking outside the language picker.
    document.addEventListener("click", (event) => {
        if (!languagePicker.contains(event.target)) {
            closeLanguageMenu();
        }
    });

    // Close the menu with Escape and return focus to its button.
    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape" &&
            languagePicker.classList.contains("is-open")
        ) {
            closeLanguageMenu();
            languageToggle.focus();
        }
    });

    // Allow opening the language menu with the ArrowDown key.
    languageToggle.addEventListener("keydown", (event) => {
        if (event.key === "ArrowDown") {
            event.preventDefault();
            openLanguageMenu();

            if (languageOptions.length > 0) {
                languageOptions[0].focus();
            }
        }
    });

    // Support keyboard navigation between language options.
    languageMenu.addEventListener("keydown", (event) => {
        const currentIndex = languageOptions.indexOf(document.activeElement);

        if (event.key === "ArrowDown") {
            event.preventDefault();

            const nextIndex =
                currentIndex < languageOptions.length - 1
                    ? currentIndex + 1
                    : 0;

            languageOptions[nextIndex].focus();
        }

        if (event.key === "ArrowUp") {
            event.preventDefault();

            const previousIndex =
                currentIndex > 0
                    ? currentIndex - 1
                    : languageOptions.length - 1;

            languageOptions[previousIndex].focus();
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