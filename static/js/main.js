document.addEventListener('DOMContentLoaded', function() {
    // Lightbox functionality
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <span class="lightbox-close">&times;</span>
        <img src="" alt="">
    `;
    document.body.appendChild(lightbox);
    
    // Click on post images to open lightbox
    document.querySelectorAll('.post-image').forEach(img => {
        img.addEventListener('click', function() {
            const fullSizeUrl = this.parentElement.querySelector('img').dataset.full;
            const lightboxImg = lightbox.querySelector('img');
            lightboxImg.src = fullSizeUrl;
            lightbox.style.display = 'flex';
        });
    });
    
    // Close lightbox
    lightbox.querySelector('.lightbox-close').addEventListener('click', function() {
        lightbox.style.display = 'none';
    });
    
    // Close when clicking outside image
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            lightbox.style.display = 'none';
        }
    });
    
    // Confirm before deleting posts
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this post?')) {
                e.preventDefault();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Lightbox functionality
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <span class="lightbox-close">&times;</span>
        <img src="" alt="">
    `;
    document.body.appendChild(lightbox);
    
    // Click on post images to open lightbox (works for both grid and single view)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('post-image')) {
            const fullSizeUrl = e.target.dataset.full || e.target.src;
            const lightboxImg = lightbox.querySelector('img');
            lightboxImg.src = fullSizeUrl;
            lightbox.style.display = 'flex';
        }
    });
    
    // Close lightbox
    lightbox.querySelector('.lightbox-close').addEventListener('click', function() {
        lightbox.style.display = 'none';
    });
    
    // Close when clicking outside image
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            lightbox.style.display = 'none';
        }
    });
    
    // Confirm before deleting posts
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this post?')) {
                e.preventDefault();
            }
        });
    });
});