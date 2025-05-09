document.addEventListener('DOMContentLoaded', function() {
    // Animated counter function
    function animateCounter(elementId, target, duration = 2000) {
      const element = document.getElementById(elementId);
      if (!element) return;

      let start = 0;
      const increment = Math.ceil(target / (duration / 16));

      const timer = setInterval(() => {
        start += increment;
        if (start > target) {
          element.textContent = target;
          clearInterval(timer);
        } else {
          element.textContent = start;
        }
      }, 16);
    }

    // Intersection Observer for counter animation
    const observerOptions = {
      threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          if (entry.target.id === 'stat-years') {
            animateCounter('stat-years', 10);
          } else if (entry.target.id === 'stat-clients') {
            animateCounter('stat-clients', 5000);
          } else if (entry.target.id === 'stat-companies') {
            animateCounter('stat-companies', 500);
          }
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);

    // Observe counter elements
    document.querySelectorAll('[id^="stat-"]').forEach(counter => {
      observer.observe(counter);
    });
  });