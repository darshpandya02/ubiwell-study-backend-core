// Core JavaScript functionality for the study framework dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize sorting functionality
    initializeSorting();
    
    // Initialize filtering functionality
    initializeFiltering();
    
    // Initialize responsive behavior
    initializeResponsive();
});

function initializeSorting() {
    const sortableHeaders = document.querySelectorAll('th[data-sortable="true"]');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const columnIndex = Array.from(this.parentElement.children).indexOf(this);
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Toggle sort direction
            const currentDirection = this.getAttribute('data-sort-direction') || 'asc';
            const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            
            // Update sort direction indicator
            sortableHeaders.forEach(h => h.removeAttribute('data-sort-direction'));
            this.setAttribute('data-sort-direction', newDirection);
            
            // Sort rows
            rows.sort((a, b) => {
                const aValue = a.children[columnIndex]?.textContent || '';
                const bValue = b.children[columnIndex]?.textContent || '';
                
                if (newDirection === 'asc') {
                    return aValue.localeCompare(bValue);
                } else {
                    return bValue.localeCompare(aValue);
                }
            });
            
            // Reorder rows in the table
            rows.forEach(row => tbody.appendChild(row));
        });
        
        // Add visual indicator for sortable columns
        header.style.cursor = 'pointer';
        header.title = 'Click to sort';
    });
}

function initializeFiltering() {
    const filterableHeaders = document.querySelectorAll('th[data-filterable="true"]');
    
    filterableHeaders.forEach(header => {
        const columnIndex = Array.from(header.parentElement.children).indexOf(header);
        
        // Create filter input
        const filterInput = document.createElement('input');
        filterInput.type = 'text';
        filterInput.placeholder = `Filter ${header.textContent}`;
        filterInput.className = 'form-control form-control-sm mt-2';
        filterInput.style.width = '100%';
        
        // Insert filter input after header
        header.parentElement.insertBefore(filterInput, header.nextSibling);
        
        // Add filter functionality
        filterInput.addEventListener('input', function() {
            const filterValue = this.value.toLowerCase();
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');
            
            rows.forEach(row => {
                const cellValue = row.children[columnIndex]?.textContent || '';
                const matches = cellValue.toLowerCase().includes(filterValue);
                row.style.display = matches ? '' : 'none';
            });
        });
    });
}

function initializeResponsive() {
    // Handle responsive table behavior
    const tables = document.querySelectorAll('.dashboard-table');
    
    tables.forEach(table => {
        // Add horizontal scroll for small screens
        if (table.scrollWidth > table.clientWidth) {
            table.parentElement.style.overflowX = 'auto';
        }
    });
}

// Utility functions
function showLoading(element) {
    element.classList.add('loading');
}

function hideLoading(element) {
    element.classList.remove('loading');
}

function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message`;
    messageDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Export functions for use in study-specific scripts
window.StudyFramework = {
    showLoading,
    hideLoading,
    showMessage
};
