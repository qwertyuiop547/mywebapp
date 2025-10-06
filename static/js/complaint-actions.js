/**
 * Complaint Actions
 * Handles delete, resolve, accept, and close actions for complaints
 */

// Show message function (used by all actions)
function showMessage(type, message) {
    const alertHtml = `
        <div class="alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show" role="alert">
            <i class="bi ${type === 'success' ? 'bi-check-circle' : 'bi-exclamation-triangle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Find or create messages container
    let messagesContainer = document.querySelector('.container .messages-container');
    if (!messagesContainer) {
        const mainContainer = document.querySelector('main .container');
        if (mainContainer) {
            messagesContainer = document.createElement('div');
            messagesContainer.className = 'messages-container mt-3';
            mainContainer.insertBefore(messagesContainer, mainContainer.firstChild);
        }
    }
    
    if (messagesContainer) {
        messagesContainer.innerHTML = alertHtml;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = messagesContainer.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

// Delete complaint
function deleteComplaintAjax(complaintId, complaintTitle) {
    // Show loading indicator
    const deleteBtn = document.querySelector(`[data-complaint-id="${complaintId}"] .delete-btn`);
    if (deleteBtn) {
        deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        deleteBtn.disabled = true;
    }

    // Get CSRF token
    const csrfToken = getCSRFToken();

    // Make AJAX request
    fetch(`/complaints/${complaintId}/delete/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove complaint from DOM
            const complaintRow = document.querySelector(`[data-complaint-id="${complaintId}"]`);
            if (complaintRow) {
                complaintRow.style.transition = 'opacity 0.3s ease';
                complaintRow.style.opacity = '0';
                
                setTimeout(() => {
                    complaintRow.remove();
                    
                    // Check if no more complaints
                    const complaintsList = document.querySelector('.complaints-list');
                    if (complaintsList && complaintsList.children.length === 0) {
                        complaintsList.innerHTML = '<div class="text-center py-5 text-muted"><i class="fas fa-inbox fa-3x mb-3"></i><p class="mb-0">No complaints found</p></div>';
                    }
                }, 300);
            }
            
            showMessage('success', data.message);
        } else {
            showMessage('error', data.error || 'Failed to delete complaint');
            
            if (deleteBtn) {
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                deleteBtn.disabled = false;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('error', 'An error occurred while deleting the complaint');
        
        if (deleteBtn) {
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
            deleteBtn.disabled = false;
        }
    });
}

// Mark complaint as resolved
function markComplaintResolved(complaintId, complaintTitle) {
    const resolveBtn = document.querySelector('.mark-resolved-btn');
    if (resolveBtn) {
        resolveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Marking as Resolved...';
        resolveBtn.disabled = true;
    }

    const csrfToken = getCSRFToken();

    fetch(`/complaints/${complaintId}/mark-resolved/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const statusBadge = document.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = 'status-badge status-resolved';
                statusBadge.innerHTML = '<i class="fas fa-check-circle me-1"></i> Resolved';
            }
            
            const resolvedInfo = document.querySelector('.resolved-info');
            if (resolvedInfo) {
                resolvedInfo.innerHTML = `<i class="fas fa-check-circle text-success me-1"></i> Resolved on ${data.resolved_at}`;
                resolvedInfo.style.display = 'block';
            }
            
            if (resolveBtn) {
                resolveBtn.style.display = 'none';
            }
            
            showMessage('success', data.message);
        } else {
            showMessage('error', data.error || 'Failed to mark complaint as resolved');
            
            if (resolveBtn) {
                resolveBtn.innerHTML = '<i class="fas fa-check me-1"></i> Mark Resolved';
                resolveBtn.disabled = false;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('error', 'An error occurred while marking the complaint as resolved');
        
        if (resolveBtn) {
            resolveBtn.innerHTML = '<i class="fas fa-check me-1"></i> Mark Resolved';
            resolveBtn.disabled = false;
        }
    });
}

// Accept complaint
function acceptComplaint(complaintId, complaintTitle) {
    const acceptBtn = document.querySelector('.accept-complaint-btn');
    if (acceptBtn) {
        acceptBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Accepting...';
        acceptBtn.disabled = true;
    }

    const csrfToken = getCSRFToken();

    fetch(`/complaints/${complaintId}/accept/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const statusBadge = document.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = 'status-badge status-in_progress';
                statusBadge.innerHTML = '<i class="fas fa-hourglass-half me-1"></i> In Progress';
            }
            
            if (acceptBtn) {
                acceptBtn.style.display = 'none';
            }
            
            const actionButtons = document.querySelector('.workflow-actions');
            if (actionButtons) {
                const resolveBtn = document.createElement('button');
                resolveBtn.type = 'button';
                resolveBtn.className = 'btn btn-success me-2 mark-resolved-btn';
                resolveBtn.onclick = () => markComplaintResolved(complaintId, complaintTitle);
                resolveBtn.innerHTML = '<i class="fas fa-check me-1"></i> Mark Resolved';
                actionButtons.appendChild(resolveBtn);
            }
            
            showMessage('success', data.message);
        } else {
            showMessage('error', data.error || 'Failed to accept complaint');
            
            if (acceptBtn) {
                acceptBtn.innerHTML = '<i class="fas fa-thumbs-up me-1"></i> Accept Complaint';
                acceptBtn.disabled = false;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('error', 'An error occurred while accepting the complaint');
        
        if (acceptBtn) {
            acceptBtn.innerHTML = '<i class="fas fa-thumbs-up me-1"></i> Accept Complaint';
            acceptBtn.disabled = false;
        }
    });
}

// Close complaint
function closeComplaint(complaintId, complaintTitle) {
    const closeBtn = document.querySelector('.close-complaint-btn');
    if (closeBtn) {
        closeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Closing...';
        closeBtn.disabled = true;
    }

    const csrfToken = getCSRFToken();

    fetch(`/complaints/${complaintId}/close/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const statusBadge = document.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = 'status-badge status-closed';
                statusBadge.innerHTML = '<i class="fas fa-times-circle me-1"></i> Closed';
            }
            
            if (closeBtn) {
                closeBtn.style.display = 'none';
            }
            
            const actionButtons = document.querySelector('.workflow-actions');
            if (actionButtons) {
                const deleteBtn = document.createElement('button');
                deleteBtn.type = 'button';
                deleteBtn.className = 'btn btn-danger delete-btn';
                deleteBtn.setAttribute('data-complaint-id', complaintId);
                deleteBtn.onclick = () => deleteComplaintAjax(complaintId, complaintTitle);
                deleteBtn.innerHTML = '<i class="fas fa-trash me-1"></i> Delete';
                actionButtons.appendChild(deleteBtn);
            }
            
            showMessage('success', data.message);
        } else {
            showMessage('error', data.error || 'Failed to close complaint');
            
            if (closeBtn) {
                closeBtn.innerHTML = '<i class="fas fa-times-circle me-1"></i> Close Complaint';
                closeBtn.disabled = false;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('error', 'An error occurred while closing the complaint');
        
        if (closeBtn) {
            closeBtn.innerHTML = '<i class="fas fa-times-circle me-1"></i> Close Complaint';
            closeBtn.disabled = false;
        }
    });
}

