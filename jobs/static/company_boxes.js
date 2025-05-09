   document.addEventListener('DOMContentLoaded', function() {
  // Staggered animation for cards
  const cards = document.querySelectorAll('.partners-showcase__card');

  cards.forEach((card, index) => {
    // Set delay based on index for staggered animation
    card.style.animationDelay = `${index * 0.05}s`;

    // Add click event
    card.addEventListener('click', function() {
      // You could add navigation here
      console.log(`Partner card clicked: ${card.querySelector('img').alt}`);
    });

    // Add hover effect for logo
    const logo = card.querySelector('.partners-showcase__logo-placeholder');

    // Create a pulsing effect on hover
    card.addEventListener('mouseenter', function() {
      logo.style.transform = 'scale(1.05)';

      // Add subtle rotation animation
      setTimeout(() => {
        logo.style.transition = 'transform 0.5s ease';
        logo.style.transform = 'scale(1.05) rotate(2deg)';
      }, 150);

      setTimeout(() => {
        logo.style.transform = 'scale(1.05) rotate(-2deg)';
      }, 300);

      setTimeout(() => {
        logo.style.transform = 'scale(1.05) rotate(0deg)';
      }, 450);
    });

    card.addEventListener('mouseleave', function() {
      logo.style.transition = 'transform 0.3s ease';
      logo.style.transform = 'scale(1)';
    });
  });

  // Create a search/filter functionality
  const createSearchFilter = () => {
    const searchContainer = document.createElement('div');
    searchContainer.className = 'partners-showcase__search-container';

    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search partners...';
    searchInput.className = 'partners-showcase__search-input';

    searchContainer.appendChild(searchInput);

    const container = document.querySelector('.partners-showcase__container');
    container.insertBefore(searchContainer, document.querySelector('.partners-showcase__grid'));

    // Style the search input
    const style = document.createElement('style');
    style.textContent = `
      .partners-showcase__search-container {
        margin-bottom: 30px;
        display: flex;
        justify-content: center;
      }

      .partners-showcase__search-input {
        padding: 12px 20px;
        width: 100%;
        max-width: 400px;
        border: 1px solid #e0e0e0;
        border-radius: 30px;
        font-size: 16px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        background-color: white;
      }

      .partners-showcase__search-input:focus {
        outline: none;
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.2);
        border-color: #3498db;
      }
    `;

    document.head.appendChild(style);

    // Add search functionality
    searchInput.addEventListener('input', function(e) {
      const searchTerm = e.target.value.toLowerCase();

      cards.forEach(card => {
        const partnerName = card.querySelector('img').alt.toLowerCase();

        if (partnerName.includes(searchTerm)) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  };

  // Uncomment to add search functionality
  // createSearchFilter();

  // Add intersection observer for scroll animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('partners-showcase__card--visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe each card for scroll animations
  cards.forEach(card => {
    observer.observe(card);
  });
});
