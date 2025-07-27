// Tenant Management System JavaScript

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Load notifications on page load
    loadNotifications();
    
    // Set up periodic notification refresh
    setInterval(loadNotifications, 30000); // Every 30 seconds
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Confirm delete actions
    $('.delete-confirm').click(function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
    
    // Form validation
    $('form').submit(function() {
        var form = $(this);
        var isValid = true;
        
        // Check required fields
        form.find('input[required], select[required], textarea[required]').each(function() {
            if (!$(this).val()) {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        // Email validation
        form.find('input[type="email"]').each(function() {
            var email = $(this).val();
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (email && !emailRegex.test(email)) {
                $(this).addClass('is-invalid');
                isValid = false;
            }
        });
        
        // Phone validation
        form.find('input[type="tel"], input[name*="phone"]').each(function() {
            var phone = $(this).val();
            var phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (phone && !phoneRegex.test(phone.replace(/\s/g, ''))) {
                $(this).addClass('is-invalid');
                isValid = false;
            }
        });
        
        // Number validation
        form.find('input[type="number"]').each(function() {
            var value = $(this).val();
            var min = $(this).attr('min');
            var max = $(this).attr('max');
            
            if (value) {
                if (min && parseFloat(value) < parseFloat(min)) {
                    $(this).addClass('is-invalid');
                    isValid = false;
                }
                if (max && parseFloat(value) > parseFloat(max)) {
                    $(this).addClass('is-invalid');
                    isValid = false;
                }
            }
        });
        
        if (!isValid) {
            showAlert('Please correct the highlighted fields.', 'error');
            return false;
        }
        
        // Show loading state
        var submitBtn = form.find('button[type="submit"]');
        var originalText = submitBtn.html();
        submitBtn.html('<span class="loading"></span> Processing...').prop('disabled', true);
        
        // Re-enable button after 3 seconds (in case of issues)
        setTimeout(function() {
            submitBtn.html(originalText).prop('disabled', false);
        }, 3000);
    });
    
    // Real-time search
    $('#searchInput').keyup(function() {
        var value = $(this).val().toLowerCase();
        $('.searchable-table tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });
    
    // Auto-calculate totals in financial forms
    $('input[name="rent_amount"], input[name="utility_amount"], input[name="other_charges"]').keyup(function() {
        calculateTotal();
    });
    
    // Date picker constraints
    $('input[name="end_date"]').change(function() {
        var startDate = $('input[name="start_date"]').val();
        var endDate = $(this).val();
        
        if (startDate && endDate && new Date(endDate) <= new Date(startDate)) {
            showAlert('End date must be after start date.', 'error');
            $(this).val('');
        }
    });
    
    // Dynamic unit selection based on availability
    $('#tenant_id').change(function() {
        loadAvailableUnits();
    });
    
    // Maintenance priority color coding
    $('select[name="priority"]').change(function() {
        var priority = $(this).val();
        $(this).removeClass('priority-low priority-medium priority-high priority-urgent');
        if (priority) {
            $(this).addClass('priority-' + priority);
        }
    });
    
    // Status change confirmations
    $('select[name="status"]').change(function() {
        var newStatus = $(this).val();
        var currentStatus = $(this).data('current');
        
        if (newStatus === 'closed' || newStatus === 'resolved') {
            if (!confirm('Are you sure you want to mark this as ' + newStatus + '?')) {
                $(this).val(currentStatus);
            }
        }
    });
    
    // Toggle utility bill details
    $('.utility-toggle').click(function() {
        $(this).next('.utility-details').slideToggle();
    });
    
    // Export functionality
    $('.export-btn').click(function() {
        var format = $(this).data('format');
        var type = $(this).data('type');
        
        showAlert('Generating ' + format.toUpperCase() + ' report...', 'info');
        window.location.href = '/export/' + type + '/' + format;
    });
    
    // Quick actions
    $('.quick-action').click(function() {
        var action = $(this).data('action');
        var id = $(this).data('id');
        
        switch(action) {
            case 'mark-paid':
                markInvoicePaid(id);
                break;
            case 'send-reminder':
                sendPaymentReminder(id);
                break;
            case 'update-status':
                updateMaintenanceStatus(id);
                break;
        }
    });
});

// Load notifications from server
function loadNotifications() {
    $.get('/api/notifications')
        .done(function(data) {
            updateNotificationUI(data);
        })
        .fail(function() {
            console.log('Failed to load notifications');
        });
}

// Update notification UI
function updateNotificationUI(notifications) {
    var badge = $('#notification-badge');
    var list = $('#notification-list');
    
    if (notifications.length > 0) {
        badge.text(notifications.length).removeClass('d-none');
        
        var html = '';
        notifications.forEach(function(notification) {
            html += '<div class="notification-item ' + notification.type + '" onclick="window.location.href=\'' + notification.url + '\'">';
            html += '<i class="fas fa-' + getNotificationIcon(notification.type) + '"></i> ';
            html += notification.message;
            html += '</div>';
        });
        
        list.html(html);
    } else {
        badge.addClass('d-none');
        list.html('<div class="text-muted p-3">No new notifications</div>');
    }
}

// Get notification icon based on type
function getNotificationIcon(type) {
    switch(type) {
        case 'warning': return 'exclamation-triangle';
        case 'danger': return 'exclamation-circle';
        case 'info': return 'info-circle';
        case 'success': return 'check-circle';
        default: return 'bell';
    }
}

// Show alert message
function showAlert(message, type) {
    var alertClass = type === 'error' ? 'alert-danger' : 'alert-' + type;
    var alertHtml = '<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">';
    alertHtml += message;
    alertHtml += '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    alertHtml += '</div>';
    
    $('.main-content').prepend(alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').first().fadeOut('slow');
    }, 5000);
}

// Calculate total amount in forms
function calculateTotal() {
    var rent = parseFloat($('input[name="rent_amount"]').val()) || 0;
    var utility = parseFloat($('input[name="utility_amount"]').val()) || 0;
    var other = parseFloat($('input[name="other_charges"]').val()) || 0;
    var total = rent + utility + other;
    
    $('input[name="total_amount"]').val(total.toFixed(2));
    $('#total-display').text('$' + total.toFixed(2));
}

// Load available units for lease creation
function loadAvailableUnits() {
    var tenantId = $('#tenant_id').val();
    if (!tenantId) return;
    
    $.get('/api/available-units')
        .done(function(data) {
            var select = $('#unit_id');
            select.empty().append('<option value="">Select Unit</option>');
            
            data.forEach(function(unit) {
                select.append('<option value="' + unit.id + '">' + unit.number + ' - Floor ' + unit.floor + ' (' + unit.type + ')</option>');
            });
        });
}

// Mark invoice as paid
function markInvoicePaid(invoiceId) {
    if (!confirm('Mark this invoice as paid?')) return;
    
    $.post('/api/invoice/' + invoiceId + '/mark-paid')
        .done(function() {
            showAlert('Invoice marked as paid successfully!', 'success');
            location.reload();
        })
        .fail(function() {
            showAlert('Failed to update invoice status.', 'error');
        });
}

// Send payment reminder
function sendPaymentReminder(tenantId) {
    $.post('/api/tenant/' + tenantId + '/send-reminder')
        .done(function() {
            showAlert('Payment reminder sent successfully!', 'success');
        })
        .fail(function() {
            showAlert('Failed to send reminder.', 'error');
        });
}

// Update maintenance status
function updateMaintenanceStatus(requestId) {
    var status = prompt('Enter new status (open, in_progress, resolved, closed):');
    if (!status) return;
    
    $.post('/api/maintenance/' + requestId + '/update-status', {status: status})
        .done(function() {
            showAlert('Status updated successfully!', 'success');
            location.reload();
        })
        .fail(function() {
            showAlert('Failed to update status.', 'error');
        });
}

// Format currency
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// Format date
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Table sorting
function sortTable(columnIndex, tableId) {
    var table = document.getElementById(tableId);
    var rows = Array.from(table.querySelectorAll('tbody tr'));
    var isAscending = table.dataset.sortOrder !== 'asc';
    
    rows.sort(function(a, b) {
        var aText = a.cells[columnIndex].textContent.trim();
        var bText = b.cells[columnIndex].textContent.trim();
        
        // Try to parse as numbers
        var aNum = parseFloat(aText.replace(/[^0-9.-]/g, ''));
        var bNum = parseFloat(bText.replace(/[^0-9.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // Try to parse as dates
        var aDate = new Date(aText);
        var bDate = new Date(bText);
        
        if (!isNaN(aDate) && !isNaN(bDate)) {
            return isAscending ? aDate - bDate : bDate - aDate;
        }
        
        // String comparison
        return isAscending ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    
    var tbody = table.querySelector('tbody');
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    
    // Update sort indicators
    table.querySelectorAll('th .sort-indicator').forEach(function(indicator) {
        indicator.innerHTML = '';
    });
    
    var header = table.querySelectorAll('th')[columnIndex];
    var indicator = header.querySelector('.sort-indicator');
    if (indicator) {
        indicator.innerHTML = isAscending ? ' ↑' : ' ↓';
    }
}

// Print functionality
function printPage() {
    window.print();
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('Copied to clipboard!', 'success');
    });
}

// Auto-save form data
function autoSaveForm(formId) {
    var form = document.getElementById(formId);
    if (!form) return;
    
    var formData = new FormData(form);
    var data = {};
    
    for (var pair of formData.entries()) {
        data[pair[0]] = pair[1];
    }
    
    localStorage.setItem('autosave_' + formId, JSON.stringify(data));
}

// Restore form data
function restoreFormData(formId) {
    var saved = localStorage.getItem('autosave_' + formId);
    if (!saved) return;
    
    var data = JSON.parse(saved);
    var form = document.getElementById(formId);
    
    Object.keys(data).forEach(function(key) {
        var field = form.querySelector('[name="' + key + '"]');
        if (field) {
            field.value = data[key];
        }
    });
}

// Clear auto-saved data
function clearAutoSave(formId) {
    localStorage.removeItem('autosave_' + formId);
}

// Initialize charts (if Chart.js is loaded)
function initializeCharts() {
    if (typeof Chart === 'undefined') return;
    
    // Revenue chart
    var revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Monthly Revenue',
                    data: [12000, 15000, 14000, 16000, 13000, 17000],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Occupancy chart
    var occupancyCtx = document.getElementById('occupancyChart');
    if (occupancyCtx) {
        new Chart(occupancyCtx, {
            type: 'doughnut',
            data: {
                labels: ['Occupied', 'Available'],
                datasets: [{
                    data: [85, 15],
                    backgroundColor: ['#27ae60', '#e74c3c'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Initialize tooltips and other Bootstrap components
function initializeBootstrapComponents() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Theme toggle (if implementing dark mode)
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

// Initialize theme from localStorage
function initializeTheme() {
    var savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Call initialization functions when document is ready
$(document).ready(function() {
    initializeBootstrapComponents();
    initializeCharts();
    initializeTheme();
});