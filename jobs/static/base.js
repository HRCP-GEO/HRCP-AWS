// ==== Mobile Menu Toggle Functionality ====

const mobileMenuBtn = document.querySelector(".base-mobile-menu-btn"); // Updated selector
const mobileMenu = document.querySelector(".base-mobile-menu");   // Updated selector

// Check if elements exist before adding listeners
if (mobileMenuBtn && mobileMenu) {
  mobileMenuBtn.addEventListener("click", function () {
    // Toggle the display style
    const isMenuOpen = mobileMenu.style.display === "block";
    mobileMenu.style.display = isMenuOpen ? "none" : "block";

    // Change icon based on state
    const icon = this.querySelector("i");
    if (!isMenuOpen) {
      // Menu is now open
      icon.classList.remove("fa-bars");
      icon.classList.add("fa-times");
    } else {
      // Menu is now closed
      icon.classList.remove("fa-times");
      icon.classList.add("fa-bars");
    }
  });

  // Close mobile menu when clicking outside of it
  document.addEventListener("click", (e) => {
    const isClickInsideMenu = mobileMenu.contains(e.target);
    const isClickOnButton = mobileMenuBtn.contains(e.target);
    const isMenuVisible = mobileMenu.style.display === "block";

    if (!isClickInsideMenu && !isClickOnButton && isMenuVisible) {
      mobileMenu.style.display = "none"; // Close the menu
      // Reset the icon
      const icon = mobileMenuBtn.querySelector("i");
      icon.classList.remove("fa-times");
      icon.classList.add("fa-bars");
    }
  });
} else {
    console.warn("Mobile menu button or mobile menu container not found. Navbar toggle might not work.");
}

// ==== End Mobile Menu Toggle ====


// ==== Newsletter JS (If you re-enable it) ====
// Needs to select .base-newsletter-form and .base-subscribe-btn if prefixed
/*
document.addEventListener('DOMContentLoaded', function() {
  const newsletterForm = document.querySelector('.base-newsletter-form'); // Updated selector

  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function(e) {
      // ... rest of newsletter JS ...
    });
  }
});
*/