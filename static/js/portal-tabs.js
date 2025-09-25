// Portal Tabs Navigation - No Page Reload
document.addEventListener('DOMContentLoaded', function() {
    const portalTabs = document.querySelectorAll('.portal-tab');
    const mainContent = document.querySelector('main');
    
    // Add click handler to all portal tabs
    portalTabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default link navigation
            
            const targetUrl = this.href;
            
            // Don't reload if clicking the same active tab
            if (this.classList.contains('active')) {
                return;
            }
            
            // Update active tab visual state
            portalTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show loading indicator
            showLoadingIndicator();
            
            // Update URL without page reload
            history.pushState(null, '', targetUrl);
            
            // Load content via AJAX
            loadTabContent(targetUrl);
        });
    });
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', function() {
        const currentPath = window.location.pathname;
        
        // Update active tab based on current URL
        portalTabs.forEach(tab => {
            tab.classList.remove('active');
            if (tab.getAttribute('href').includes(getTabFromPath(currentPath))) {
                tab.classList.add('active');
            }
        });
        
        // Load content for current URL
        loadTabContent(window.location.href);
    });
    
    function showLoadingIndicator() {
        mainContent.innerHTML = `
            <div class="container my-5">
                <div class="row justify-content-center">
                    <div class="col-md-6 text-center">
                        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-3 text-muted">Loading content...</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    function loadTabContent(url) {
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            // Parse the response and extract the main content
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newMainContent = doc.querySelector('main');
            
            if (newMainContent) {
                mainContent.innerHTML = newMainContent.innerHTML;
                
                // Reinitialize any JavaScript components
                reinitializeComponents();
            } else {
                // Fallback: replace entire main content
                mainContent.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Error loading tab content:', error);
            showErrorMessage();
            // Fallback to full page reload
            setTimeout(() => {
                window.location.href = url;
            }, 2000);
        });
    }
    
    function showErrorMessage() {
        mainContent.innerHTML = `
            <div class="container my-5">
                <div class="row justify-content-center">
                    <div class="col-md-6 text-center">
                        <div class="alert alert-danger" role="alert">
                            <i class="fas fa-exclamation-triangle"></i>
                            <strong>Oops!</strong> Something went wrong loading the content.
                            <br><small>Redirecting to full page...</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    function getTabFromPath(path) {
        if (path.includes('suggestions')) return 'suggestions';
        if (path.includes('complaints')) return 'complaints';
        if (path.includes('gallery')) return 'gallery';
        return '';
    }
    
    function getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            return csrfToken.value;
        }
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        return '';
    }
    
    function reinitializeComponents() {
        // Reinitialize any JavaScript components that need to be reloaded
        
        // Example: Reinitialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
        
        // Example: Reinitialize any custom components
        if (window.initComplaintComponents) {
            window.initComplaintComponents();
        }
        
        if (window.initSuggestionComponents) {
            window.initSuggestionComponents();
        }
        
        if (window.initGalleryComponents) {
            window.initGalleryComponents();
        }
        
        // Reinitialize any form validation
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            // Add any form-specific initialization here
        });
    }
});

// Add smooth scrolling for better UX
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll to top when switching tabs
    window.smoothScrollToTop = function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    };
});
