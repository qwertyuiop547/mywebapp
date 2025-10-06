/**
 * CSRF Token Handler
 * Automatically includes CSRF tokens in all AJAX/fetch requests
 */

// Global CSRF token getter function
function getCSRFToken() {
    // Try to get from cookie first
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    
    // Fallback to meta tag
    if (!cookieValue) {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            cookieValue = metaTag.getAttribute('content');
        }
    }
    
    // Fallback to form input
    if (!cookieValue) {
        const formInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (formInput) {
            cookieValue = formInput.value;
        }
    }
    
    return cookieValue;
}

// Set up CSRF token for all AJAX requests
document.addEventListener('DOMContentLoaded', function() {
    // Configure fetch to include CSRF token by default
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        // Only add CSRF token for same-origin requests
        if (!url.startsWith('http') || url.startsWith(window.location.origin)) {
            const method = (options.method || 'GET').toUpperCase();
            
            // Add CSRF token for unsafe methods
            if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
                options.headers = options.headers || {};
                
                // Don't override if already set
                if (!options.headers['X-CSRFToken']) {
                    const csrfToken = getCSRFToken();
                    if (csrfToken) {
                        if (options.headers instanceof Headers) {
                            options.headers.set('X-CSRFToken', csrfToken);
                        } else {
                            options.headers['X-CSRFToken'] = csrfToken;
                        }
                    }
                }
            }
        }
        
        return originalFetch(url, options);
    };

    // Also set up for jQuery if it's being used
    if (window.jQuery) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
                }
            }
        });
    }
});

