// Toggle dropdowns
document.querySelectorAll(".dropdown-select").forEach((select) => {
  select.addEventListener("click", function () {
    this.classList.toggle("active");
    const menu = this.nextElementSibling;
    menu.classList.toggle("show");

    // Close other dropdowns
    document.querySelectorAll(".dropdown-menu").forEach((otherMenu) => {
      if (otherMenu !== menu && otherMenu.classList.contains("show")) {
        otherMenu.classList.remove("show");
        otherMenu.previousElementSibling.classList.remove("active");
      }
    });
  });
});

// Close dropdowns when clicking outside
document.addEventListener("click", (e) => {
  if (!e.target.closest(".filter-dropdown")) {
    document.querySelectorAll(".dropdown-menu").forEach((menu) => {
      menu.classList.remove("show");
      if (menu.previousElementSibling) {
        menu.previousElementSibling.classList.remove("active");
      }
    });
  }
});

// Toast notification function
function showToast(type, message) {
  const toastContainer = document.querySelector(".toast-container");

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  const icon = type === "success" ? "check-circle" : "times-circle";

  toast.innerHTML = `
    <div class="toast-icon">
      <i class="fas fa-${icon}"></i>
    </div>
    <div class="toast-content">${message}</div>
  `;

  toastContainer.appendChild(toast);

  // Animate in
  setTimeout(() => {
    toast.classList.add("show");
  }, 10);

  // Remove after 3 seconds
  setTimeout(() => {
    toast.classList.remove("show");

    setTimeout(() => {
      toastContainer.removeChild(toast);
    }, 300);
  }, 3000);
}

// footer

// Newsletter form submission
document.addEventListener('DOMContentLoaded', function() {
  const newsletterForm = document.querySelector('.newsletter-form');

  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function(e) {
      e.preventDefault();

      const emailInput = this.querySelector('input[type="email"]');
      const email = emailInput.value.trim();

      if (email) {
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.className = 'newsletter-success';
        successMessage.textContent = 'გმადლობთ გამოწერისთვის!';
        successMessage.style.color = '#4CAF50';
        successMessage.style.marginTop = '10px';
        successMessage.style.fontWeight = '500';

        // Remove any existing success message
        const existingMessage = newsletterForm.querySelector('.newsletter-success');
        if (existingMessage) {
          existingMessage.remove();
        }

        // Add the success message
        newsletterForm.appendChild(successMessage);

        // Reset the form
        emailInput.value = '';

        // In a real implementation, you would send this to your backend
        console.log('Newsletter subscription:', email);

        // Remove the success message after 3 seconds
        setTimeout(() => {
          successMessage.remove();
        }, 3000);
      }
    });
  }
});

function clearAllFilters() {
    window.location.search = ""; // Clear the entire query string
  }

  function toggleJobTimeType(timeType) {
    let urlParams = new URLSearchParams(window.location.search);
    let selectedTypes = urlParams.getAll('job_time_types');

    if (selectedTypes.includes(timeType)) {
      selectedTypes = selectedTypes.filter(type => type !== timeType);
    } else {
      selectedTypes.push(timeType);
    }

    urlParams.delete('job_time_types');
    if (selectedTypes.length > 0) {
      selectedTypes.forEach(type => urlParams.append('job_time_types', type));
    }

    window.location.search = urlParams.toString();
  }

  function updateJobTimeTypeFilter(selectedTimeType) {
      const url = new URL(window.location.href);
      const params = url.searchParams;
      let currentSelections = params.getAll('job_time_types'); // Get all current selections

      // Handle 'all' case - remove all job_time_types params
      if (selectedTimeType === 'all') {
        params.delete('job_time_types');
      } else {
        // If 'all' was previously selected (or no selection), remove it
         if (currentSelections.includes('all') || currentSelections.length === 0) {
             params.delete('job_time_types'); // Clear existing before adding specific
             currentSelections = []; // Reset local array
         }

        // Toggle the selected time type
        if (currentSelections.includes(selectedTimeType)) {
          // Remove it - filter preserves others
          const newSelections = currentSelections.filter(item => item !== selectedTimeType);
          params.delete('job_time_types'); // Clear all first
          newSelections.forEach(sel => params.append('job_time_types', sel)); // Add back the remaining ones
        } else {
          // Add it
          params.append('job_time_types', selectedTimeType);
        }

        // If after changes, no specific types are selected, default to 'all' (optional, depends on desired behavior)
        // Or maybe just leave it empty to show all implicitly? Let's leave empty for now.
         if (params.getAll('job_time_types').length === 0) {
            // If you want clicking the last active one to show all:
            // params.delete('job_time_types'); // Ensure it's clean
            // Or just let it be empty, which the view treats as 'show all'
         }

      }
      // Go to the new URL
      window.location.href = url.toString();
    }

// Your existing dropdown code
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dropdowns
    const dropdowns = document.querySelectorAll('.filter-dropdown');

    dropdowns.forEach(dropdown => {
        const select = dropdown.querySelector('.dropdown-select');
        const menu = dropdown.querySelector('.dropdown-menu');
        const items = dropdown.querySelectorAll('.dropdown-item');

        select.addEventListener('click', () => {
            dropdowns.forEach(other => {
                if (other !== dropdown) {
                    other.querySelector('.dropdown-menu').classList.remove('active');
                }
            });
            menu.classList.toggle('active');
        });

        items.forEach(item => {
            item.addEventListener('click', () => {
                select.querySelector('span').textContent = item.textContent;
                menu.classList.remove('active');
            });
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.filter-dropdown')) {
            dropdowns.forEach(dropdown => {
                dropdown.querySelector('.dropdown-menu').classList.remove('active');
            });
        }
    });

    // Job Time Type Filter handling
    window.updateJobTimeTypeFilter = function(filter) {
        // Get current URL and parameters
        const url = new URL(window.location.href);
        const params = url.searchParams;

        // Clear existing job_time_types parameters
        params.delete('job_time_types');

        // Add the new filter (unless it's 'all')
        if (filter !== 'all') {
            params.append('job_time_types', filter);
        }

        // Navigate to the new URL
        window.location.href = url.toString();
    };
});


document.addEventListener('DOMContentLoaded', function () {
  const searchIcon = document.getElementById('search-submit-icon');
  const searchForm = document.querySelector('.search-box');

  if (searchIcon && searchForm) {
    searchIcon.addEventListener('click', function () {
      searchForm.submit();  // 👈 this triggers form submission
    });
  }
});