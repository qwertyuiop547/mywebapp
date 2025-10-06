/**
 * Notification System
 * Handles real-time notifications, polling, and marking as read
 */

let notificationCount = 0;
let lastNotificationCheck = new Date();

function updateNotificationBadge(count) {
    const badge = document.getElementById('notification-count');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

function fetchNotifications() {
    // Get the API URL from the element if it exists
    const notificationList = document.getElementById('notification-list');
    if (!notificationList) return;

    const apiUrl = notificationList.getAttribute('data-api-url') || '/notifications/api/list/';
    
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const unreadCount = data.filter(n => !n.is_read).length;
            updateNotificationBadge(unreadCount);
            
            if (data.length === 0) {
                notificationList.innerHTML = '<li class="text-center text-muted p-3">No new notifications</li>';
            } else {
                notificationList.innerHTML = data.slice(0, 5).map(notification => `
                    <li class="notification-item ${!notification.is_read ? 'unread' : ''}">
                        <a href="${notification.link}" class="text-decoration-none" onclick="markAsReadAndNavigate(event, ${notification.id}, '${notification.link}')">
                            <div class="d-flex">
                                <div class="flex-grow-1">
                                    <strong>${notification.title}</strong>
                                    <div class="text-muted small">${notification.message}</div>
                                    <div class="text-muted small">${new Date(notification.created_at).toLocaleString()}</div>
                                </div>
                                ${!notification.is_read ? '<div class="text-primary"><i class="bi bi-circle-fill"></i></div>' : ''}
                            </div>
                        </a>
                    </li>
                `).join('');
            }
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

function markAsRead(notificationId, markReadUrl) {
    const url = markReadUrl.replace('0', notificationId);
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fetchNotifications();
        }
    })
    .catch(error => console.error('Error marking notification as read:', error));
}

function markAsReadAndNavigate(event, notificationId, link) {
    event.preventDefault();
    
    // Get the mark read URL from data attribute
    const notificationList = document.getElementById('notification-list');
    const markReadUrl = notificationList ? notificationList.getAttribute('data-mark-read-url') : '/notifications/mark-read/0/';
    const url = markReadUrl.replace('0', notificationId);
    
    // Mark as read and then navigate
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = link;
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
        // Navigate anyway even if marking as read fails
        window.location.href = link;
    });
}

function markAllAsRead() {
    const notificationList = document.getElementById('notification-list');
    const markAllUrl = notificationList ? notificationList.getAttribute('data-mark-all-url') : '/notifications/mark-all-read/';
    
    fetch(markAllUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fetchNotifications();
        }
    })
    .catch(error => console.error('Error marking all notifications as read:', error));
}

// Initialize notification system
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if notification elements exist
    if (document.getElementById('notification-list')) {
        fetchNotifications();
        setInterval(fetchNotifications, 30000); // Check every 30 seconds
        
        const markAllBtn = document.getElementById('mark-all-read');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', function(e) {
                e.preventDefault();
                markAllAsRead();
            });
        }
    }
});

