document.addEventListener('DOMContentLoaded', function() {
    const galleryTab = document.querySelector('.portal-tab[href*="gallery"]');
    
    if (galleryTab) {
        galleryTab.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default link behavior
            
            // Update active tab
            document.querySelectorAll('.portal-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            this.classList.add('active');
            
            // Update URL without reloading
            history.pushState(null, '', this.href);
            
            // Load gallery content via AJAX
            fetch(this.href, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                // Find the main content area and update it
                const temp = document.createElement('div');
                temp.innerHTML = html;
                const newContent = temp.querySelector('#gallery-content');
                
                if (newContent) {
                    document.querySelector('#gallery-content').innerHTML = newContent.innerHTML;
                    // Reinitialize any gallery-specific JavaScript
                    if (window.initGallery) {
                        window.initGallery();
                    }
                }
            })
            .catch(error => {
                console.error('Error loading gallery:', error);
                // Fallback to regular navigation if AJAX fails
                window.location.href = this.href;
            });
        });
    }
});
