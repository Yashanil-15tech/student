// Main JavaScript for Student Portal

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirm delete actions
    $('.delete-confirm').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });

    // Character counter for textareas
    $('textarea[maxlength]').each(function() {
        var maxLength = $(this).attr('maxlength');
        var currentLength = $(this).val().length;
        var $counter = $('<small class="text-muted float-end"></small>');
        $counter.text(currentLength + ' / ' + maxLength);
        $(this).after($counter);
        
        $(this).on('input', function() {
            var length = $(this).val().length;
            $counter.text(length + ' / ' + maxLength);
        });
    });

    // Table row click to navigate
    $('.clickable-row').on('click', function() {
        window.location = $(this).data('href');
    });

    // Search functionality for tables
    $('.table-search').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        var table = $(this).data('table');
        $(table + ' tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });

    // Smooth scroll to top
    $('.scroll-to-top').on('click', function(e) {
        e.preventDefault();
        $('html, body').animate({scrollTop: 0}, 'smooth');
    });

    // File upload preview
    $('input[type="file"]').on('change', function() {
        var fileName = $(this).val().split('\\').pop();
        $(this).next('.custom-file-label').html(fileName);
    });

    // Form validation feedback
    $('form').on('submit', function() {
        var isValid = true;
        $(this).find('input[required], textarea[required], select[required]').each(function() {
            if ($(this).val() === '') {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        return isValid;
    });

    // Clear form validation on input
    $('input, textarea, select').on('input change', function() {
        $(this).removeClass('is-invalid');
    });

    // Attendance percentage color coding
    $('.attendance-percentage').each(function() {
        var percentage = parseFloat($(this).text());
        if (percentage >= 75) {
            $(this).addClass('text-success');
        } else if (percentage >= 60) {
            $(this).addClass('text-warning');
        } else {
            $(this).addClass('text-danger');
        }
    });

    // Grade color coding
    $('.grade-badge').each(function() {
        var grade = $(this).text().trim();
        switch(grade) {
            case 'A+':
            case 'A':
                $(this).addClass('bg-success');
                break;
            case 'B+':
            case 'B':
                $(this).addClass('bg-info');
                break;
            case 'C':
                $(this).addClass('bg-warning');
                break;
            case 'D':
            case 'F':
                $(this).addClass('bg-danger');
                break;
        }
    });

    // Dynamic time display
    function updateTime() {
        var now = new Date();
        var timeString = now.toLocaleTimeString();
        $('.current-time').text(timeString);
    }
    
    if ($('.current-time').length) {
        updateTime();
        setInterval(updateTime, 1000);
    }

    // Progress bar animation
    $('.progress-bar').each(function() {
        var $bar = $(this);
        var targetWidth = $bar.attr('aria-valuenow') + '%';
        $bar.css('width', '0%').animate({
            width: targetWidth
        }, 1000);
    });

    // Copy to clipboard functionality
    $('.copy-btn').on('click', function() {
        var text = $(this).data('copy');
        var $temp = $('<input>');
        $('body').append($temp);
        $temp.val(text).select();
        document.execCommand('copy');
        $temp.remove();
        
        var $btn = $(this);
        var originalText = $btn.html();
        $btn.html('<i class="fas fa-check"></i> Copied!');
        setTimeout(function() {
            $btn.html(originalText);
        }, 2000);
    });

    // Print functionality
    $('.print-btn').on('click', function() {
        window.print();
    });

    // Export table to CSV
    $('.export-csv').on('click', function() {
        var table = $(this).data('table');
        var csv = [];
        var rows = $(table + ' tr');
        
        rows.each(function() {
            var row = [];
            $(this).find('th, td').each(function() {
                row.push($(this).text());
            });
            csv.push(row.join(','));
        });
        
        var csvContent = csv.join('\n');
        var blob = new Blob([csvContent], { type: 'text/csv' });
        var url = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'export.csv';
        a.click();
    });
});

// Utility functions
function showLoading() {
    $('body').append('<div class="loading-overlay"><div class="spinner-border text-primary" role="status"></div></div>');
}

function hideLoading() {
    $('.loading-overlay').remove();
}

function showNotification(message, type = 'info') {
    var alertClass = 'alert-' + type;
    var $alert = $('<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
                    message +
                    '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                    '</div>');
    $('.container').first().prepend($alert);
    
    setTimeout(function() {
        $alert.fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}
