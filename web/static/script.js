// 🌸 Ayaka AI Girlfriend System - Main JavaScript File 🌸

// 🌸 Execute after page loads 🌸
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌸 Ayaka AI Girlfriend System loaded 🌸');

    // 🌸 Initialize page elements
    initializePage();
});

// 🌸 Initialize page 🌸
function initializePage() {
    // 🌸 Add smooth scrolling effect
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // 🌸 Add loading animation
    animateElements();
}

// 🌸 Animation effects 🌸
function animateElements() {
    const elements = document.querySelectorAll('.fade-in');
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 200);
    });
}

// 🌸 API call function 🌸
async function callAPI(endpoint, data = {}) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        return await response.json();
    } catch (error) {
        console.error('🌸 API call failed:', error);
        throw error;
    }
}

// 🌸 Show notification 🌸
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    // Add styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '10px',
        color: 'white',
        fontWeight: 'bold',
        zIndex: '1000',
        opacity: '0',
        transform: 'translateX(100%)',
        transition: 'all 0.3s ease'
    });

    // Set background color
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#28a745';
            break;
        case 'error':
            notification.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            notification.style.backgroundColor = '#ffc107';
            notification.style.color = '#333';
            break;
        default:
            notification.style.backgroundColor = '#17a2b8';
    }

    // Add to page
    document.body.appendChild(notification);

    // Show animation
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto disappear after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 🌸 Format time 🌸
function formatTime(date) {
    return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 🌸 Utility functions 🌸
const utils = {
    // 🌸 Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // 🌸 Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// 🌸 Export functions for other modules to use 🌸
window.AyakaUtils = {
    callAPI,
    showNotification,
    formatTime,
    utils
};