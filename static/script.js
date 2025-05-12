document.addEventListener('DOMContentLoaded', function() {
    // Toggle review form visibility when edit button is clicked
    const editReviewBtn = document.querySelector('.edit-review-btn');
    if (editReviewBtn) {
        editReviewBtn.addEventListener('click', function() {
            const reviewDisplay = document.querySelector('.review-display');
            const reviewForm = document.querySelector('.review-form');
            
            reviewDisplay.classList.add('hidden');
            reviewForm.classList.remove('hidden');
        });
    }
});