/**
 * Offline Upload Queue Manager
 * Manages file uploads when offline and syncs when online
 */

class OfflineManager {
    constructor() {
        this.dbName = 'GreenCloudOfflineDB';
        this.storeName = 'uploadQueue';
        this.db = null;
        this.isOnline = navigator.onLine;
        this.syncInProgress = false;
        
        this.init();
    }

    /**
     * Initialize IndexedDB and event listeners
     */
    async init() {
        await this.openDB();
        this.setupEventListeners();
        this.updateOnlineStatus();
        
        // Try to sync on startup if online
        if (this.isOnline) {
            this.syncQueue();
        }
    }

    /**
     * Open IndexedDB connection
     */
    openDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, 1);

            request.onerror = () => {
                console.error('[OfflineManager] DB Error:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('[OfflineManager] DB opened successfully');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    const objectStore = db.createObjectStore(this.storeName, { 
                        keyPath: 'id', 
                        autoIncrement: true 
                    });
                    objectStore.createIndex('timestamp', 'timestamp', { unique: false });
                    objectStore.createIndex('status', 'status', { unique: false });
                }
            };
        });
    }

    /**
     * Setup online/offline event listeners
     */
    setupEventListeners() {
        window.addEventListener('online', () => {
            console.log('[OfflineManager] Connection restored');
            this.isOnline = true;
            this.updateOnlineStatus();
            this.syncQueue();
        });

        window.addEventListener('offline', () => {
            console.log('[OfflineManager] Connection lost');
            this.isOnline = false;
            this.updateOnlineStatus();
        });
    }

    /**
     * Update UI online status indicator
     */
    updateOnlineStatus() {
        const statusEl = document.getElementById('connection-status');
        const queueCountEl = document.getElementById('queue-count');
        
        if (statusEl) {
            if (this.isOnline) {
                statusEl.className = 'status-online';
                statusEl.innerHTML = '<i class="fas fa-wifi"></i> Online';
            } else {
                statusEl.className = 'status-offline';
                statusEl.innerHTML = '<i class="fas fa-wifi-slash"></i> Offline';
            }
        }

        // Update queue count
        this.getQueueCount().then(count => {
            if (queueCountEl && count > 0) {
                queueCountEl.textContent = `${count} file${count > 1 ? 's' : ''} queued`;
                queueCountEl.style.display = 'inline';
            } else if (queueCountEl) {
                queueCountEl.style.display = 'none';
            }
        });
    }

    /**
     * Add file to upload queue
     */
    async addToQueue(file, folderId = null) {
        if (!this.db) {
            await this.openDB();
        }

        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const queueItem = {
                    filename: file.name,
                    fileData: e.target.result,
                    fileType: file.type,
                    fileSize: file.size,
                    folderId: folderId,
                    timestamp: Date.now(),
                    status: 'pending'
                };

                const transaction = this.db.transaction([this.storeName], 'readwrite');
                const objectStore = transaction.objectStore(this.storeName);
                const request = objectStore.add(queueItem);

                request.onsuccess = () => {
                    console.log('[OfflineManager] File added to queue:', file.name);
                    this.updateOnlineStatus();
                    resolve(request.result);
                };

                request.onerror = () => {
                    console.error('[OfflineManager] Error adding to queue:', request.error);
                    reject(request.error);
                };
            };

            reader.onerror = () => {
                reject(reader.error);
            };

            reader.readAsDataURL(file);
        });
    }

    /**
     * Get count of queued items
     */
    async getQueueCount() {
        if (!this.db) {
            return 0;
        }

        return new Promise((resolve) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const objectStore = transaction.objectStore(this.storeName);
            const index = objectStore.index('status');
            const request = index.count('pending');

            request.onsuccess = () => {
                resolve(request.result);
            };

            request.onerror = () => {
                resolve(0);
            };
        });
    }

    /**
     * Sync queued uploads when online
     */
    async syncQueue() {
        if (!this.isOnline || this.syncInProgress || !this.db) {
            return;
        }

        this.syncInProgress = true;
        console.log('[OfflineManager] Starting sync...');

        try {
            const items = await this.getQueuedItems();
            
            if (items.length === 0) {
                console.log('[OfflineManager] No items to sync');
                this.syncInProgress = false;
                return;
            }

            // Show sync status
            this.showSyncStatus(items.length);

            for (const item of items) {
                try {
                    await this.uploadQueuedItem(item);
                    await this.removeFromQueue(item.id);
                } catch (error) {
                    console.error('[OfflineManager] Failed to upload:', item.filename, error);
                    // Continue with next item
                }
            }

            this.updateOnlineStatus();
            this.hideSyncStatus();
            this.showNotification('All queued files uploaded successfully!', 'success');
            
        } catch (error) {
            console.error('[OfflineManager] Sync error:', error);
            this.hideSyncStatus();
        }

        this.syncInProgress = false;
    }

    /**
     * Get all queued items
     */
    getQueuedItems() {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const objectStore = transaction.objectStore(this.storeName);
            const index = objectStore.index('status');
            const request = index.getAll('pending');

            request.onsuccess = () => {
                resolve(request.result);
            };

            request.onerror = () => {
                reject(request.error);
            };
        });
    }

    /**
     * Upload a queued item
     */
    async uploadQueuedItem(item) {
        // Convert base64 back to blob
        const byteString = atob(item.fileData.split(',')[1]);
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        const blob = new Blob([ab], { type: item.fileType });
        const file = new File([blob], item.filename, { type: item.fileType });

        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        if (item.folderId) {
            formData.append('folder_id', item.folderId);
        }

        // Upload
        const response = await fetch('/files/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Remove item from queue
     */
    removeFromQueue(id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const objectStore = transaction.objectStore(this.storeName);
            const request = objectStore.delete(id);

            request.onsuccess = () => {
                console.log('[OfflineManager] Removed from queue:', id);
                resolve();
            };

            request.onerror = () => {
                reject(request.error);
            };
        });
    }

    /**
     * Show sync status message
     */
    showSyncStatus(count) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.className = 'status-syncing';
            statusEl.innerHTML = `<i class="fas fa-sync fa-spin"></i> Syncing ${count} file${count > 1 ? 's' : ''}...`;
        }
    }

    /**
     * Hide sync status
     */
    hideSyncStatus() {
        this.updateOnlineStatus();
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Use existing notification system if available
        if (typeof showAlert === 'function') {
            showAlert(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
}

// Initialize offline manager when DOM is ready
let offlineManager;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        offlineManager = new OfflineManager();
    });
} else {
    offlineManager = new OfflineManager();
}
