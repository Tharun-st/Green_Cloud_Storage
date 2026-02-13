// GreenCloud - Main JavaScript

// Register Service Worker for offline support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== Mobile Menu Toggle =====
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // ===== Close Flash Messages =====
    const alertCloses = document.querySelectorAll('.alert-close');
    alertCloses.forEach(function(close) {
        close.addEventListener('click', function() {
            this.parentElement.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                this.parentElement.remove();
            }, 300);
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                alert.remove();
            }, 300);
        });
    }, 5000);
    
    // ===== Modal Functions =====
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
    
    // ===== File Input Styling =====
    const fileInputs = document.querySelectorAll('.file-input');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                const label = this.nextElementSibling;
                if (label) {
                    label.textContent = fileName;
                }
            }
        });
    });
    
    // ===== Active Navigation Highlighting =====
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(function(item) {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });
    
    // ===== Storage Bar Animation =====
    const storageFill = document.querySelector('.storage-fill');
    if (storageFill) {
        const targetWidth = storageFill.style.width;
        storageFill.style.width = '0';
        setTimeout(() => {
            storageFill.style.width = targetWidth;
        }, 100);
    }
    
    // ===== Drag and Drop File Upload =====
    const uploadModal = document.getElementById('uploadModal');
    if (uploadModal) {
        const fileInput = uploadModal.querySelector('input[type="file"]');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            document.body.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            document.body.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight(e) {
            document.body.classList.add('drag-over');
        }
        
        function unhighlight(e) {
            document.body.classList.remove('drag-over');
        }
        
        document.body.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0 && fileInput) {
                fileInput.files = files;
                uploadModal.style.display = 'flex';
            }
        }
    }
    
    // ===== Smooth Scroll =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ===== Form Validation =====
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = 'var(--danger-color)';
                } else {
                    input.style.borderColor = '#ddd';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // ===== Tooltips =====
    const tooltipElements = document.querySelectorAll('[title]');
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', function() {
            const title = this.getAttribute('title');
            if (title) {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = title;
                tooltip.style.cssText = `
                    position: absolute;
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-size: 12px;
                    pointer-events: none;
                    z-index: 10000;
                    white-space: nowrap;
                `;
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
                
                this._tooltip = tooltip;
            }
        });
        
        el.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
    
    // ===== Copy File Link Buttons =====
    const copyLinkButtons = document.querySelectorAll('.copy-link-btn');
    if (copyLinkButtons.length) {
        copyLinkButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                const url = this.dataset.url;
                if (!url) return;

                function doCopy(text) {
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    textarea.style.position = 'fixed';
                    textarea.style.opacity = '0';
                    document.body.appendChild(textarea);
                    textarea.select();
                    try {
                        document.execCommand('copy');
                    } catch (e) {
                        console.warn('Copy failed', e);
                    }
                    document.body.removeChild(textarea);
                }

                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(url).then(() => {
                        showNotification('Link copied to clipboard!', 'success');
                    }).catch(() => {
                        doCopy(url);
                        showNotification('Link copied to clipboard!', 'success');
                    });
                } else {
                    doCopy(url);
                    showNotification('Link copied to clipboard!', 'success');
                }
            });
        });
    }

    // ===== Console Welcome Message =====
    console.log('%cGreenCloud Storage', 'color: #2ecc71; font-size: 20px; font-weight: bold;');
    console.log('%cWelcome to eco-friendly cloud storage!', 'color: #3498db; font-size: 14px;');
});

// ===== Utility Functions =====

// Format bytes to human readable
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
        <button class="alert-close">&times;</button>
    `;
    
    const container = document.querySelector('.flash-messages') || document.body;
    container.appendChild(notification);
    
    notification.querySelector('.alert-close').addEventListener('click', function() {
        notification.remove();
    });
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Confirm dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Handle file upload with offline support
function handleFileUpload(e) {
    e.preventDefault();
    
    const fileInput = e.target.querySelector('input[type="file"]');
    
    if (!fileInput || !fileInput.files.length) {
        showNotification('Please select a file', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    const folderId = e.target.querySelector('select[name="folder_id"]')?.value || null;
    
    // Check if offline
    if (!navigator.onLine && typeof offlineManager !== 'undefined') {
        // Add to offline queue
        offlineManager.addToQueue(file, folderId)
            .then(() => {
                showNotification(`File "${file.name}" queued for upload when online`, 'info');
                fileInput.value = '';
                e.target.closest('.modal')?.style.display = 'none';
            })
            .catch(error => {
                console.error('Error queuing file:', error);
                showNotification('Failed to queue file for offline upload', 'error');
            });
        return;
    }
    
    // Online upload
    const formData = new FormData(e.target);
    
    // Show upload progress
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn?.innerHTML;
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    }
    
    fetch('/files/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok && !navigator.onLine && typeof offlineManager !== 'undefined') {
            // Network error while uploading, add to queue
            return offlineManager.addToQueue(file, folderId)
                .then(() => {
                    showNotification(`Connection lost. File "${file.name}" queued for upload`, 'info');
                    fileInput.value = '';
                    e.target.closest('.modal')?.style.display = 'none';
                    return { queued: true };
                });
        }
        return response.json();
    })
    .then(data => {
        if (data.queued) {
            // Already handled
        } else if (data.success) {
            showNotification('File uploaded successfully!', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(data.message || 'Upload failed', 'error');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        // Try to queue if offline manager is available
        if (!navigator.onLine && typeof offlineManager !== 'undefined') {
            offlineManager.addToQueue(file, folderId)
                .then(() => {
                    showNotification(`Connection lost. File "${file.name}" queued for upload`, 'info');
                    fileInput.value = '';
                    e.target.closest('.modal')?.style.display = 'none';
                })
                .catch(() => {
                    showNotification('Upload failed. Please try again.', 'error');
                });
        } else {
            showNotification('Upload failed. Please try again.', 'error');
        }
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
}

// Show alert (alias for showNotification)
function showAlert(message, type) {
    showNotification(message, type);
}
