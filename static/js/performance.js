/**
 * Performance Optimization JavaScript
 * Handles lazy loading, AJAX pagination, loading states, and smooth interactions
 */

// =============================================================================
// LOADING STATES & SPINNERS
// =============================================================================

class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
        this.init();
    }

    init() {
        // Create loading overlay template
        if (!document.getElementById('global-loading-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'global-loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner-border text-light" role="status">
                        <span class="sr-only">Loading...</span>
                    </div>
                    <p class="loading-text mt-3">Loading...</p>
                </div>
            `;
            document.body.appendChild(overlay);
        }
    }

    show(message = 'Loading...', target = null) {
        const loaderId = Date.now().toString();
        this.activeLoaders.add(loaderId);

        if (target) {
            // Show loading in specific element
            const element = typeof target === 'string' ? document.querySelector(target) : target;
            if (element) {
                const spinner = document.createElement('div');
                spinner.className = 'local-spinner';
                spinner.dataset.loaderId = loaderId;
                spinner.innerHTML = `
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="sr-only">${message}</span>
                    </div>
                    <span class="ml-2">${message}</span>
                `;
                element.style.position = 'relative';
                element.appendChild(spinner);
            }
        } else {
            // Show global loading
            const overlay = document.getElementById('global-loading-overlay');
            if (overlay) {
                overlay.querySelector('.loading-text').textContent = message;
                overlay.classList.add('active');
            }
        }

        return loaderId;
    }

    hide(loaderId = null, target = null) {
        if (loaderId) {
            this.activeLoaders.delete(loaderId);
        }

        if (target) {
            // Hide local spinner
            const element = typeof target === 'string' ? document.querySelector(target) : target;
            if (element) {
                const spinner = element.querySelector(`.local-spinner[data-loader-id="${loaderId}"]`);
                if (spinner) {
                    spinner.remove();
                }
            }
        } else {
            // Hide global loading only if no active loaders
            if (this.activeLoaders.size === 0) {
                const overlay = document.getElementById('global-loading-overlay');
                if (overlay) {
                    overlay.classList.remove('active');
                }
            }
        }
    }

    hideAll() {
        this.activeLoaders.clear();
        const overlay = document.getElementById('global-loading-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
        // Remove all local spinners
        document.querySelectorAll('.local-spinner').forEach(s => s.remove());
    }
}

// Global loading manager instance
const loading = new LoadingManager();


// =============================================================================
// LAZY LOADING IMAGES
// =============================================================================

class LazyLoader {
    constructor(options = {}) {
        this.options = {
            rootMargin: '50px',
            threshold: 0.01,
            ...options
        };
        this.observer = null;
        this.init();
    }

    init() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver(
                this.onIntersection.bind(this),
                this.options
            );
            this.observe();
        } else {
            // Fallback for older browsers
            this.loadAll();
        }
    }

    observe() {
        const lazyElements = document.querySelectorAll('[data-lazy-src], [data-lazy-bg]');
        lazyElements.forEach(el => this.observer.observe(el));
    }

    onIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadElement(entry.target);
                this.observer.unobserve(entry.target);
            }
        });
    }

    loadElement(element) {
        const lazySrc = element.dataset.lazySrc;
        const lazyBg = element.dataset.lazyBg;

        if (lazySrc) {
            // Load image
            const img = new Image();
            img.onload = () => {
                element.src = lazySrc;
                element.classList.add('lazy-loaded');
                element.removeAttribute('data-lazy-src');
            };
            img.onerror = () => {
                element.classList.add('lazy-error');
            };
            img.src = lazySrc;
        }

        if (lazyBg) {
            // Load background image
            const img = new Image();
            img.onload = () => {
                element.style.backgroundImage = `url('${lazyBg}')`;
                element.classList.add('lazy-loaded');
                element.removeAttribute('data-lazy-bg');
            };
            img.src = lazyBg;
        }
    }

    loadAll() {
        const lazyElements = document.querySelectorAll('[data-lazy-src], [data-lazy-bg]');
        lazyElements.forEach(el => this.loadElement(el));
    }

    refresh() {
        this.observe();
    }
}

// Global lazy loader instance
const lazyLoader = new LazyLoader();


// =============================================================================
// AJAX PAGINATION
// =============================================================================

class AjaxPagination {
    constructor(options = {}) {
        this.options = {
            container: '#content-container',
            paginationSelector: '.pagination a',
            scrollToTop: true,
            onSuccess: null,
            ...options
        };
        this.init();
    }

    init() {
        this.attachListeners();
    }

    attachListeners() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest(this.options.paginationSelector);
            if (target && this.isAjaxPagination(target)) {
                e.preventDefault();
                this.loadPage(target.href);
            }
        });
    }

    isAjaxPagination(element) {
        return element.dataset.ajaxPagination !== 'false';
    }

    async loadPage(url) {
        const loaderId = loading.show('Loading page...', this.options.container);

        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const html = await response.text();
            const container = document.querySelector(this.options.container);
            
            if (container) {
                container.innerHTML = html;

                // Scroll to top if enabled
                if (this.options.scrollToTop) {
                    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }

                // Refresh lazy loader
                lazyLoader.refresh();

                // Call success callback
                if (this.options.onSuccess) {
                    this.options.onSuccess(container);
                }

                // Update URL
                window.history.pushState({}, '', url);
            }
        } catch (error) {
            console.error('Pagination error:', error);
            window.location.href = url; // Fallback to normal navigation
        } finally {
            loading.hide(loaderId, this.options.container);
        }
    }
}


// =============================================================================
// INFINITE SCROLL
// =============================================================================

class InfiniteScroll {
    constructor(options = {}) {
        this.options = {
            container: '#content-container',
            nextPageSelector: '.pagination .next',
            threshold: 300, // pixels from bottom
            ...options
        };
        this.loading = false;
        this.hasMore = true;
        this.init();
    }

    init() {
        this.attachScrollListener();
    }

    attachScrollListener() {
        let ticking = false;

        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    this.checkScroll();
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    checkScroll() {
        if (this.loading || !this.hasMore) return;

        const scrollPosition = window.innerHeight + window.scrollY;
        const threshold = document.documentElement.scrollHeight - this.options.threshold;

        if (scrollPosition >= threshold) {
            this.loadMore();
        }
    }

    async loadMore() {
        const nextLink = document.querySelector(this.options.nextPageSelector);
        if (!nextLink) {
            this.hasMore = false;
            return;
        }

        this.loading = true;
        const loaderId = loading.show('Loading more...', this.options.container);

        try {
            const response = await fetch(nextLink.href, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const html = await response.text();
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;

            const container = document.querySelector(this.options.container);
            const newContent = tempDiv.querySelector(this.options.container);

            if (newContent) {
                // Append new items
                Array.from(newContent.children).forEach(child => {
                    container.appendChild(child);
                });

                // Check if there are more pages
                const newNextLink = tempDiv.querySelector(this.options.nextPageSelector);
                if (!newNextLink) {
                    this.hasMore = false;
                }

                // Refresh lazy loader
                lazyLoader.refresh();
            }
        } catch (error) {
            console.error('Infinite scroll error:', error);
            this.hasMore = false;
        } finally {
            this.loading = false;
            loading.hide(loaderId, this.options.container);
        }
    }
}


// =============================================================================
// DEBOUNCE & THROTTLE UTILITIES
// =============================================================================

function debounce(func, wait = 300) {
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

function throttle(func, limit = 300) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}


// =============================================================================
// FORM SUBMISSION WITH AJAX
// =============================================================================

class AjaxForm {
    constructor(formSelector, options = {}) {
        this.form = typeof formSelector === 'string' 
            ? document.querySelector(formSelector) 
            : formSelector;
        
        this.options = {
            onSuccess: null,
            onError: null,
            showLoading: true,
            resetOnSuccess: false,
            ...options
        };

        this.init();
    }

    init() {
        if (!this.form) return;

        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submit();
        });
    }

    async submit() {
        const formData = new FormData(this.form);
        const loaderId = this.options.showLoading 
            ? loading.show('Submitting...', this.form) 
            : null;

        try {
            const response = await fetch(this.form.action || window.location.href, {
                method: this.form.method || 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (response.ok) {
                if (this.options.resetOnSuccess) {
                    this.form.reset();
                }

                if (this.options.onSuccess) {
                    this.options.onSuccess(data);
                }

                // Show success message
                this.showMessage('Success!', 'success');
            } else {
                throw new Error(data.error || 'Form submission failed');
            }
        } catch (error) {
            console.error('Form submission error:', error);

            if (this.options.onError) {
                this.options.onError(error);
            }

            // Show error message
            this.showMessage(error.message || 'An error occurred', 'error');
        } finally {
            if (loaderId) {
                loading.hide(loaderId, this.form);
            }
        }
    }

    showMessage(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}


// =============================================================================
// SEARCH WITH AUTOCOMPLETE
// =============================================================================

class LiveSearch {
    constructor(inputSelector, options = {}) {
        this.input = typeof inputSelector === 'string'
            ? document.querySelector(inputSelector)
            : inputSelector;

        this.options = {
            url: null,
            minChars: 2,
            delay: 300,
            onSelect: null,
            ...options
        };

        this.results = [];
        this.init();
    }

    init() {
        if (!this.input) return;

        // Create results container
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = 'autocomplete-results';
        this.input.parentElement.style.position = 'relative';
        this.input.parentElement.appendChild(this.resultsContainer);

        // Attach listener with debounce
        this.input.addEventListener('input', debounce(async (e) => {
            await this.search(e.target.value);
        }, this.options.delay));

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!this.input.parentElement.contains(e.target)) {
                this.hideResults();
            }
        });
    }

    async search(query) {
        if (query.length < this.options.minChars) {
            this.hideResults();
            return;
        }

        try {
            const response = await fetch(`${this.options.url}?q=${encodeURIComponent(query)}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            this.results = data.results || [];
            this.showResults();
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    showResults() {
        if (this.results.length === 0) {
            this.hideResults();
            return;
        }

        this.resultsContainer.innerHTML = this.results.map((result, index) => `
            <div class="autocomplete-item" data-index="${index}">
                ${result.title || result.name}
            </div>
        `).join('');

        this.resultsContainer.classList.add('show');

        // Attach click listeners
        this.resultsContainer.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.selectResult(this.results[index]);
            });
        });
    }

    hideResults() {
        this.resultsContainer.classList.remove('show');
    }

    selectResult(result) {
        if (this.options.onSelect) {
            this.options.onSelect(result);
        }
        this.hideResults();
    }
}


// =============================================================================
// INITIALIZE ON PAGE LOAD
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize lazy loading
    console.log('Performance optimizations loaded');

    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    // Auto-hide loading overlay on page load
    setTimeout(() => loading.hideAll(), 100);
});


// =============================================================================
// EXPORT FOR MODULE USE
// =============================================================================

window.PerformanceUtils = {
    loading,
    lazyLoader,
    AjaxPagination,
    InfiniteScroll,
    AjaxForm,
    LiveSearch,
    debounce,
    throttle
};

