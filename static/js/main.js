/**
 * CampusKart - Main JavaScript File
 * College Marketplace Platform
 */

// ===== DOCUMENT READY =====
$(document).ready(function() {
    console.log('CampusKart initialized');
    
    // Initialize all components
    initializeTooltips();
    initializePopovers();
    initializeImagePreview();
    initializeFormValidation();
    initializeAutoHideAlerts();
    initializeSearchFilters();
    initializeInfiniteScroll();
    initializeRatingSystem();
    initializeCopyToClipboard();
    
    // Add fade-in animation to main content
    $('main').addClass('fade-in');
});

// ===== INITIALIZATION FUNCTIONS =====

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize image preview for file inputs
 */
function initializeImagePreview() {
    $('input[type="file"][accept*="image"]').each(function() {
        $(this).on('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                const previewId = $(this).data('preview') || 'imagePreview';
                
                reader.onload = function(event) {
                    $('#' + previewId).attr('src', event.target.result).show();
                }
                
                reader.readAsDataURL(file);
            }
        });
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    // Phone number validation
    $('input[name="phone_number"]').on('input', function() {
        validatePhoneInput($(this));
    });
    
    // Price validation
    $('input[name="price"]').on('input', function() {
        validatePriceInput($(this));
    });
    
    // Email validation
    $('input[type="email"]').on('blur', function() {
        validateEmailInput($(this));
    });
}

/**
 * Initialize auto-hide alerts
 */
function initializeAutoHideAlerts() {
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

/**
 * Initialize search filters
 */
function initializeSearchFilters() {
    // Category filter
    $('#categoryFilter').on('change', function() {
        $('#filterForm').submit();
    });
    
    // Price range slider
    $('#priceRange').on('input', function() {
        $('#priceValue').text('$' + $(this).val());
    });
    
    // Sort selector
    $('#sortSelect').on('change', function() {
        const sortValue = $(this).val();
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('sort', sortValue);
        window.location.href = currentUrl.toString();
    });
}

/**
 * Initialize infinite scroll for product listing
 */
function initializeInfiniteScroll() {
    let loading = false;
    let page = 2;
    
    $(window).on('scroll', function() {
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
            if (!loading && $('#loadMore').length && !$('#loadMore').hasClass('disabled')) {
                loading = true;
                loadMoreProducts(page++);
            }
        }
    });
}

/**
 * Initialize rating system
 */
function initializeRatingSystem() {
    $('.rating-star').on('click', function() {
        const rating = $(this).data('rating');
        const productId = $(this).data('product-id');
        
        $('.rating-star').each(function() {
            if ($(this).data('rating') <= rating) {
                $(this).addClass('active');
            } else {
                $(this).removeClass('active');
            }
        });
        
        // Submit rating via AJAX
        submitRating(productId, rating);
    });
}

/**
 * Initialize copy to clipboard functionality
 */
function initializeCopyToClipboard() {
    $('.copy-to-clipboard').on('click', function() {
        const textToCopy = $(this).data('copy');
        copyToClipboard(textToCopy);
    });
}

// ===== VALIDATION FUNCTIONS =====

/**
 * Validate phone number input
 */
function validatePhoneInput(input) {
    const phone = input.val();
    const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
    
    if (phone && !phoneRegex.test(phone)) {
        input.addClass('is-invalid');
        input.removeClass('is-valid');
        return false;
    } else {
        input.removeClass('is-invalid');
        input.addClass('is-valid');
        return true;
    }
}

/**
 * Validate price input
 */
function validatePriceInput(input) {
    const price = parseFloat(input.val());
    
    if (isNaN(price) || price < 0) {
        input.addClass('is-invalid');
        input.removeClass('is-valid');
        return false;
    } else {
        input.removeClass('is-invalid');
        input.addClass('is-valid');
        return true;
    }
}

/**
 * Validate email input
 */
function validateEmailInput(input) {
    const email = input.val();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        input.addClass('is-invalid');
        input.removeClass('is-valid');
        showNotification('Please enter a valid email address', 'warning');
        return false;
    } else {
        input.removeClass('is-invalid');
        input.addClass('is-valid');
        return true;
    }
}

// ===== AJAX FUNCTIONS =====

/**
 * Load more products (infinite scroll)
 */
function loadMoreProducts(page) {
    const url = window.location.pathname + '?page=' + page + '&' + window.location.search.substring(1);
    
    $.ajax({
        url: url,
        type: 'GET',
        beforeSend: function() {
            $('#loadMore').html('<span class="spinner-border spinner-border-sm"></span> Loading...');
        },
        success: function(data) {
            if (data.products && data.products.length > 0) {
                $('#productsContainer').append(data.products);
                $('#loadMore').html('Load More');
                
                if (!data.has_next) {
                    $('#loadMore').addClass('disabled').hide();
                }
            } else {
                $('#loadMore').addClass('disabled').hide();
            }
        },
        error: function() {
            showNotification('Error loading more products', 'danger');
            $('#loadMore').html('Load More');
        },
        complete: function() {
            loading = false;
        }
    });
}

/**
 * Submit product rating
 */
function submitRating(productId, rating) {
    $.ajax({
        url: '/api/rate-product/',
        type: 'POST',
        data: {
            product_id: productId,
            rating: rating,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
            showNotification('Rating submitted successfully!', 'success');
        },
        error: function() {
            showNotification('Error submitting rating', 'danger');
        }
    });
}

/**
 * Request product purchase
 */
function requestProduct(productId) {
    $.ajax({
        url: '/api/request-product/',
        type: 'POST',
        data: {
            product_id: productId,
            csrfmiddlewaretoken: getCSRFToken()
        },
        success: function(response) {
            showNotification('Request sent successfully!', 'success');
            setTimeout(function() {
                location.reload();
            }, 2000);
        },
        error: function() {
            showNotification('Error sending request', 'danger');
        }
    });
}

// ===== UTILITY FUNCTIONS =====

/**
 * Get CSRF token from cookies
 */
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('#messages').append(alertHtml);
    
    setTimeout(function() {
        $('.alert').last().fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Copied to clipboard!', 'success');
    }, function() {
        showNotification('Failed to copy!', 'danger');
    });
}

/**
 * Format price with currency symbol
 */
function formatPrice(price) {
    return '$' + parseFloat(price).toFixed(2);
}

/**
 * Format date to relative time
 */
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + ' minutes ago';
    if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + ' hours ago';
    if (diffInSeconds < 604800) return Math.floor(diffInSeconds / 86400) + ' days ago';
    
    return date.toLocaleDateString();
}

/**
 * Debounce function for performance
 */
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

/**
 * Throttle function for performance
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ===== EVENT HANDLERS =====

/**
 * Handle search form submission
 */
$('#searchForm').on('submit', function(e) {
    $(this).find('button[type="submit"]').html('<span class="spinner-border spinner-border-sm"></span> Searching...');
});

/**
 * Handle delete confirmation
 */
$('.delete-confirm').on('click', function(e) {
    if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        e.preventDefault();
    }
});

/**
 * Handle image error fallback
 */
$('img').on('error', function() {
    $(this).attr('src', '/static/images/placeholder.jpg');
});

/**
 * Handle smooth scrolling for anchor links
 */
$('a[href*="#"]').not('[href="#"]').not('[href="#0"]').on('click', function(event) {
    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && 
        location.hostname == this.hostname) {
        
        var target = $(this.hash);
        target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
        
        if (target.length) {
            event.preventDefault();
            $('html, body').animate({
                scrollTop: target.offset().top - 70
            }, 1000);
        }
    }
});

// ===== WINDOW EVENTS =====

/**
 * Handle window resize
 */
$(window).on('resize', debounce(function() {
    // Adjust UI elements on resize
    if ($(window).width() < 768) {
        $('.desktop-only').hide();
        $('.mobile-only').show();
    } else {
        $('.desktop-only').show();
        $('.mobile-only').hide();
    }
}, 250));

/**
 * Handle page visibility change
 */
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('Page hidden');
    } else {
        console.log('Page visible');
        // Refresh data if needed
    }
});

// ===== EXPORT FUNCTIONS FOR GLOBAL USE =====
window.CampusKart = {
    showNotification: showNotification,
    formatPrice: formatPrice,
    formatRelativeTime: formatRelativeTime,
    copyToClipboard: copyToClipboard,
    requestProduct: requestProduct
};