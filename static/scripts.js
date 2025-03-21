/**
 * OpenTale - Common JS functions
 */

// Check if document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-resize textareas
    document.querySelectorAll('textarea.auto-resize').forEach(function(textarea) {
        textarea.addEventListener('input', autoResizeTextarea);
        // Initial resize
        autoResizeTextarea.call(textarea);
    });

    // Handle active navigation links
    highlightActiveNav();
});

/**
 * Auto-resize a textarea based on its content
 */
function autoResizeTextarea() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
}

/**
 * Highlight the active navigation link based on the current page
 */
function highlightActiveNav() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Create toast element if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create the toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show the toast
    const bsToast = new bootstrap.Toast(toast, {
        animation: true,
        autohide: true,
        delay: 3000
    });
    
    bsToast.show();
    
    // Remove the toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Copy text to clipboard
 * @param {string} text - The text to copy
 * @returns {boolean} - Whether the copy was successful
 */
function copyToClipboard(text) {
    // Create a temporary textarea element
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    
    // Select and copy the text
    textarea.select();
    let success = false;
    
    try {
        success = document.execCommand('copy');
        if (success) {
            showNotification('Copied to clipboard!', 'success');
        } else {
            showNotification('Failed to copy to clipboard', 'error');
        }
    } catch (err) {
        console.error('Failed to copy', err);
        showNotification('Failed to copy to clipboard', 'error');
    }
    
    // Clean up
    document.body.removeChild(textarea);
    return success;
}

/**
 * Save form data to local storage
 * @param {string} formId - The ID of the form to save
 * @param {string} storageKey - The key to use in localStorage
 */
function saveFormToLocalStorage(formId, storageKey) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = {};
    const formElements = form.elements;
    
    for (let i = 0; i < formElements.length; i++) {
        const element = formElements[i];
        if (element.name && element.type !== 'submit' && element.type !== 'button') {
            formData[element.name] = element.value;
        }
    }
    
    localStorage.setItem(storageKey, JSON.stringify(formData));
}

/**
 * Load form data from local storage
 * @param {string} formId - The ID of the form to populate
 * @param {string} storageKey - The key to use in localStorage
 */
function loadFormFromLocalStorage(formId, storageKey) {
    const savedData = localStorage.getItem(storageKey);
    if (!savedData) return;
    
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = JSON.parse(savedData);
    const formElements = form.elements;
    
    for (let i = 0; i < formElements.length; i++) {
        const element = formElements[i];
        if (element.name && formData[element.name] !== undefined) {
            element.value = formData[element.name];
        }
    }
} 