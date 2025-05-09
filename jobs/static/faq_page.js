document.addEventListener('DOMContentLoaded', function () {
    const faqItems = document.querySelectorAll('.cphr-faq-item');
    const faqCategories = document.querySelectorAll('.cphr-faq-category');
    const faqSearch = document.getElementById('faqSearch');
    const noResults = document.querySelector('.cphr-faq-no-results');

    // Toggle FAQ item
    faqItems.forEach(item => {
        const question = item.querySelector('.cphr-faq-question');
        question.addEventListener('click', () => {
            item.classList.toggle('active');
        });
    });

    // Filter FAQ by category
    faqCategories.forEach(category => {
        category.addEventListener('click', () => {
            faqCategories.forEach(c => c.classList.remove('active'));
            category.classList.add('active');
            const selectedCategory = category.dataset.category;

            let found = false;
            faqItems.forEach(item => {
                if (selectedCategory === 'all' || item.dataset.category === selectedCategory) {
                    item.style.display = 'block';
                    found = true;
                } else {
                    item.style.display = 'none';
                }
            });

            noResults.style.display = found ? 'none' : 'block';
        });
    });

    // Search FAQ
    faqSearch.addEventListener('input', () => {
        const searchTerm = faqSearch.value.toLowerCase();
        let found = false;
        faqItems.forEach(item => {
            const question = item.querySelector('.cphr-faq-question').textContent.toLowerCase();
            const answer = item.querySelector('.cphr-faq-answer').textContent.toLowerCase();
            if (question.includes(searchTerm) || answer.includes(searchTerm)) {
                item.style.display = 'block';
                found = true;
            } else {
                item.style.display = 'none';
            }
        });
        noResults.style.display = found ? 'none' : 'block';
    });
});