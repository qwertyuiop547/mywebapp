/* ========================================
   RESPONSIVE ENHANCEMENTS JAVASCRIPT
   Barangay Complaint & Feedback Portal
   ======================================== */

document.addEventListener('DOMContentLoaded', function() {
    
    /* ========================================
       1. MOBILE NAVIGATION ENHANCEMENTS
       ======================================== */
    
    // Toggle mobile menu
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
            document.body.classList.toggle('menu-open');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                navbarCollapse.classList.remove('show');
                document.body.classList.remove('menu-open');
            }
        });
        
        // Close menu when selecting a link
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                    document.body.classList.remove('menu-open');
                }
            });
        });
    }
    
    /* ========================================
       2. RESPONSIVE TABLES
       ======================================== */
    
    // Convert tables to mobile cards on small screens
    function makeTablesResponsive() {
        const tables = document.querySelectorAll('.table');
        
        tables.forEach(table => {
            if (window.innerWidth <= 576 && !table.classList.contains('table-mobile-card')) {
                table.classList.add('table-mobile-card');
                
                // Add data-label attributes to cells
                const headers = table.querySelectorAll('thead th');
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    cells.forEach((cell, index) => {
                        if (headers[index]) {
                            cell.setAttribute('data-label', headers[index].textContent);
                        }
                    });
                });
            } else if (window.innerWidth > 576) {
                table.classList.remove('table-mobile-card');
            }
        });
    }
    
    makeTablesResponsive();
    window.addEventListener('resize', makeTablesResponsive);
    
    /* ========================================
       3. TOUCH SWIPE SUPPORT
       ======================================== */
    
    // Add swipe support for carousels and galleries
    let touchStartX = 0;
    let touchEndX = 0;
    
    function handleSwipe(element, leftCallback, rightCallback) {
        element.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, false);
        
        element.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipeGesture(leftCallback, rightCallback);
        }, false);
    }
    
    function handleSwipeGesture(leftCallback, rightCallback) {
        if (touchEndX < touchStartX - 50 && leftCallback) {
            leftCallback();
        }
        if (touchEndX > touchStartX + 50 && rightCallback) {
            rightCallback();
        }
    }
    
    // Apply to image galleries
    const galleries = document.querySelectorAll('.gallery-container');
    galleries.forEach(gallery => {
        handleSwipe(gallery, 
            () => { /* next image */ },
            () => { /* previous image */ }
        );
    });
    
    /* ========================================
       4. FORM ENHANCEMENTS
       ======================================== */
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // Prevent zoom on input focus (iOS)
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="password"], textarea, select');
    inputs.forEach(input => {
        input.style.fontSize = '16px';
    });
    
    /* ========================================
       5. SIDEBAR TOGGLE
       ======================================== */
    
    // Create sidebar toggle for mobile
    const sidebar = document.querySelector('.sidebar');
    if (sidebar && window.innerWidth < 992) {
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'sidebar-toggle btn btn-primary';
        toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
        toggleBtn.style.cssText = 'position: fixed; top: 70px; left: 15px; z-index: 1051;';
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        
        document.body.appendChild(toggleBtn);
        document.body.appendChild(overlay);
        
        // Toggle sidebar
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
        });
        
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }
    
    /* ========================================
       6. MODAL IMPROVEMENTS
       ======================================== */
    
    // Make modals fullscreen on mobile
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            if (window.innerWidth <= 576) {
                const modalDialog = this.querySelector('.modal-dialog');
                modalDialog.classList.add('modal-fullscreen-sm-down');
            }
        });
    });
    
    /* ========================================
       7. DROPDOWN IMPROVEMENTS
       ======================================== */
    
    // Convert dropdowns to full-width on mobile
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const menu = dropdown.querySelector('.dropdown-menu');
        if (menu && window.innerWidth <= 768) {
            menu.style.width = '100%';
        }
    });
    
    /* ========================================
       8. IMAGE LAZY LOADING
       ======================================== */
    
    // Implement lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });
        
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
    
    /* ========================================
       9. SCROLL TO TOP
       ======================================== */
    
    // Enhanced scroll to top for mobile
    const backToTop = document.querySelector('.back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        });
        
        backToTop.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    /* ========================================
       10. ORIENTATION CHANGE HANDLER
       ======================================== */
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        // Recalculate layouts
        setTimeout(() => {
            makeTablesResponsive();
            adjustModalSizes();
            updateChartSizes();
        }, 300);
    });
    
    /* ========================================
       11. CHART RESPONSIVENESS
       ======================================== */
    
    // Update chart sizes on resize
    function updateChartSizes() {
        if (typeof Chart !== 'undefined') {
            Chart.helpers.each(Chart.instances, function(instance) {
                instance.resize();
            });
        }
    }
    
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(updateChartSizes, 250);
    });
    
    /* ========================================
       12. ACCORDION ENHANCEMENTS
       ======================================== */
    
    // Auto-collapse other accordions on mobile
    const accordions = document.querySelectorAll('.accordion');
    accordions.forEach(accordion => {
        const buttons = accordion.querySelectorAll('.accordion-button');
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    const otherButtons = accordion.querySelectorAll('.accordion-button:not(.collapsed)');
                    otherButtons.forEach(otherBtn => {
                        if (otherBtn !== button) {
                            otherBtn.click();
                        }
                    });
                }
            });
        });
    });
    
    /* ========================================
       13. TAB SCROLL
       ======================================== */
    
    // Make tabs scrollable on mobile
    const tabContainers = document.querySelectorAll('.nav-tabs');
    tabContainers.forEach(container => {
        if (window.innerWidth <= 768) {
            // Add scroll buttons
            const scrollLeft = document.createElement('button');
            scrollLeft.className = 'tab-scroll-btn tab-scroll-left';
            scrollLeft.innerHTML = '<i class="fas fa-chevron-left"></i>';
            
            const scrollRight = document.createElement('button');
            scrollRight.className = 'tab-scroll-btn tab-scroll-right';
            scrollRight.innerHTML = '<i class="fas fa-chevron-right"></i>';
            
            container.parentElement.style.position = 'relative';
            container.parentElement.appendChild(scrollLeft);
            container.parentElement.appendChild(scrollRight);
            
            scrollLeft.addEventListener('click', () => {
                container.scrollBy({ left: -200, behavior: 'smooth' });
            });
            
            scrollRight.addEventListener('click', () => {
                container.scrollBy({ left: 200, behavior: 'smooth' });
            });
        }
    });
    
    /* ========================================
       14. FILE UPLOAD ENHANCEMENTS
       ======================================== */
    
    // Drag and drop for mobile
    const uploadAreas = document.querySelectorAll('.file-upload-area');
    uploadAreas.forEach(area => {
        // Touch support for file selection
        area.addEventListener('click', function() {
            const input = this.querySelector('input[type="file"]');
            if (input) input.click();
        });
    });
    
    /* ========================================
       16. AUTO-DISMISS ALERTS & NOTIFICATIONS
       ======================================== */
    
    // Auto-dismiss alerts after 2 seconds
    function autoDismissAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent):not(.alert-danger)');
        alerts.forEach(alert => {
            // Check if it's a success, info, or warning message
            if (alert.classList.contains('alert-success') || 
                alert.classList.contains('alert-info') || 
                alert.classList.contains('alert-warning')) {
                
                // Add auto-dismiss class for styling
                alert.classList.add('auto-dismiss');
                
                // Add fade-out animation after 2 seconds
                setTimeout(() => {
                    alert.classList.add('dismissing');
                    
                    // Remove element after animation completes
                    setTimeout(() => {
                        if (alert.parentNode) {
                            alert.parentNode.removeChild(alert);
                        }
                    }, 500);
                }, 2000);
            }
        });
    }
    
    // Auto-dismiss toasts
    function autoDismissToasts() {
        const toasts = document.querySelectorAll('.toast');
        toasts.forEach(toast => {
            setTimeout(() => {
                const bsToast = new bootstrap.Toast(toast);
                bsToast.hide();
            }, 3000);
        });
    }
    
    // Auto-dismiss messages on page load
    autoDismissAlerts();
    autoDismissToasts();
    
    // Also run when new content is loaded dynamically
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        if (node.classList && node.classList.contains('alert') && 
                            !node.classList.contains('alert-permanent') && 
                            !node.classList.contains('alert-danger')) {
                            // Single alert added
                            if (node.classList.contains('alert-success') || 
                                node.classList.contains('alert-info') || 
                                node.classList.contains('alert-warning')) {
                                
                                // Add auto-dismiss class for styling
                                node.classList.add('auto-dismiss');
                                
                                setTimeout(() => {
                                    node.classList.add('dismissing');
                                    setTimeout(() => {
                                        if (node.parentNode) {
                                            node.parentNode.removeChild(node);
                                        }
                                    }, 500);
                                }, 2000);
                            }
                        } else {
                            // Check for alerts within added content
                            const newAlerts = node.querySelectorAll && node.querySelectorAll('.alert:not(.alert-permanent):not(.alert-danger)');
                            if (newAlerts) {
                                newAlerts.forEach(alert => {
                                    if (alert.classList.contains('alert-success') || 
                                        alert.classList.contains('alert-info') || 
                                        alert.classList.contains('alert-warning')) {
                                        
                                        // Add auto-dismiss class for styling
                                        alert.classList.add('auto-dismiss');
                                        
                                        setTimeout(() => {
                                            alert.classList.add('dismissing');
                                            setTimeout(() => {
                                                if (alert.parentNode) {
                                                    alert.parentNode.removeChild(alert);
                                                }
                                            }, 500);
                                        }, 2000);
                                    }
                                });
                            }
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    /* ========================================
       17. NOTIFICATION BADGE UPDATE
       ======================================== */
    
    // Auto-update notification badges
    function updateNotificationBadges() {
        const badges = document.querySelectorAll('.notification-badge');
        badges.forEach(badge => {
            const count = parseInt(badge.textContent);
            if (count > 99) {
                badge.textContent = '99+';
            }
        });
    }
    
    updateNotificationBadges();
    
    /* ========================================
       16. SEARCH OPTIMIZATION
       ======================================== */
    
    // Debounce search input for mobile
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        const debouncedSearch = debounce((value) => {
            // Perform search
            console.log('Searching for:', value);
        }, 500);
        
        input.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });
    });
    
    /* ========================================
       17. TOOLTIP MOBILE SUPPORT
       ======================================== */
    
    // Convert tooltips to click on mobile
    if ('ontouchstart' in window) {
        const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggers.forEach(trigger => {
            trigger.setAttribute('data-bs-trigger', 'click');
        });
    }
    
    /* ========================================
       18. RESPONSIVE VIDEOS
       ======================================== */
    
    // Make videos responsive
    const videos = document.querySelectorAll('video, iframe');
    videos.forEach(video => {
        if (!video.parentElement.classList.contains('video-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'video-wrapper';
            wrapper.style.cssText = 'position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;';
            video.parentNode.insertBefore(wrapper, video);
            wrapper.appendChild(video);
            video.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%;';
        }
    });
    
    /* ========================================
       19. PRINT OPTIMIZATION
       ======================================== */
    
    // Optimize for printing
    window.addEventListener('beforeprint', function() {
        // Expand all collapsed elements
        const collapsedElements = document.querySelectorAll('.collapse:not(.show)');
        collapsedElements.forEach(el => {
            el.classList.add('show', 'print-expanded');
        });
        
        // Remove pagination
        const paginationElements = document.querySelectorAll('.pagination');
        paginationElements.forEach(el => {
            el.style.display = 'none';
        });
    });
    
    window.addEventListener('afterprint', function() {
        // Restore collapsed state
        const printExpanded = document.querySelectorAll('.print-expanded');
        printExpanded.forEach(el => {
            el.classList.remove('show', 'print-expanded');
        });
        
        // Restore pagination
        const paginationElements = document.querySelectorAll('.pagination');
        paginationElements.forEach(el => {
            el.style.display = '';
        });
    });
    
    /* ========================================
       20. PERFORMANCE MONITORING
       ======================================== */
    
    // Monitor and log performance
    if ('performance' in window && 'PerformanceObserver' in window) {
        const perfObserver = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'largest-contentful-paint') {
                    console.log('LCP:', entry.startTime);
                }
            }
        });
        
        perfObserver.observe({ entryTypes: ['largest-contentful-paint'] });
    }
    
    /* ========================================
       21. ACCESSIBILITY ENHANCEMENTS
       ======================================== */
    
    // Skip to content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link';
    skipLink.textContent = 'Skip to main content';
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Ensure main content has id
    const mainContent = document.querySelector('main') || document.querySelector('.main-content');
    if (mainContent && !mainContent.id) {
        mainContent.id = 'main-content';
    }
    
    // Focus management for modals
    const modalElements = document.querySelectorAll('.modal');
    modalElements.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input, textarea, select');
            if (firstInput) firstInput.focus();
        });
    });
    
    /* ========================================
       22. OFFLINE SUPPORT
       ======================================== */
    
    // Check online status
    function updateOnlineStatus() {
        if (navigator.onLine) {
            document.body.classList.remove('offline');
            const offlineMsg = document.querySelector('.offline-message');
            if (offlineMsg) offlineMsg.remove();
        } else {
            document.body.classList.add('offline');
            const message = document.createElement('div');
            message.className = 'offline-message alert alert-warning';
            message.textContent = 'You are currently offline. Some features may not be available.';
            document.body.appendChild(message);
        }
    }
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
});

/* ========================================
   UTILITY FUNCTIONS
   ======================================== */

// Check if device is mobile
function isMobile() {
    return window.innerWidth <= 768 || 
           /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Check if device supports touch
function isTouchDevice() {
    return 'ontouchstart' in window || 
           navigator.maxTouchPoints > 0 || 
           navigator.msMaxTouchPoints > 0;
}

// Get viewport dimensions
function getViewport() {
    return {
        width: Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0),
        height: Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)
    };
}

// Smooth scroll to element
function scrollToElement(element, offset = 0) {
    const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
    });
}

// Export functions for use in other scripts
window.ResponsiveUtils = {
    isMobile,
    isTouchDevice,
    getViewport,
    scrollToElement
};
