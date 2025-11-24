/**
 * API Client for Simple Time Tracker Dashboard
 * Handles all communication with the Flask backend
 */

class TimeTrackerAPI {
    constructor(baseURL = 'http://localhost:8080') {
        this.baseURL = baseURL;
        this.requestTimeout = 10000; // 10 seconds
    }

    /**
     * Make HTTP request with error handling
     */
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            timeout: this.requestTimeout,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            console.log(`🔄 API Request: ${options.method || 'GET'} ${url}`);
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.requestTimeout);
            
            config.signal = controller.signal;

            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            console.log(`📡 API Response: ${response.status} ${url}`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error(`❌ API Error: ${endpoint}`, error);
            
            if (error.name === 'AbortError') {
                throw new Error('Запрос превысил время ожидания');
            }
            
            throw error;
        }
    }

    /**
     * Get all projects
     */
    async getProjects() {
        try {
            const response = await this.makeRequest('/api/projects');
            return response.data;
        } catch (error) {
            throw new Error(`Ошибка загрузки проектов: ${error.message}`);
        }
    }

    /**
     * Get active project
     */
    async getActiveProject() {
        try {
            const response = await this.makeRequest('/api/active');
            return response.data;
        } catch (error) {
            throw new Error(`Ошибка получения активного проекта: ${error.message}`);
        }
    }

    /**
     * Start a project
     */
    async startProject(identifier) {
        try {
            const response = await this.makeRequest('/api/start', {
                method: 'POST',
                body: JSON.stringify({ identifier })
            });
            return response;
        } catch (error) {
            throw new Error(`Ошибка запуска проекта "${identifier}": ${error.message}`);
        }
    }

    /**
     * Pause a project
     */
    async pauseProject(identifier) {
        try {
            const response = await this.makeRequest('/api/pause', {
                method: 'POST',
                body: JSON.stringify({ identifier })
            });
            return response;
        } catch (error) {
            throw new Error(`Ошибка приостановки проекта "${identifier}": ${error.message}`);
        }
    }

    /**
     * Complete a project
     */
    async completeProject(identifier) {
        try {
            const response = await this.makeRequest('/api/complete', {
                method: 'POST',
                body: JSON.stringify({ identifier })
            });
            return response;
        } catch (error) {
            throw new Error(`Ошибка завершения проекта "${identifier}": ${error.message}`);
        }
    }

    /**
     * Archive a project
     */
    async archiveProject(identifier) {
        try {
            const response = await this.makeRequest('/api/archive', {
                method: 'POST',
                body: JSON.stringify({ identifier })
            });
            return response;
        } catch (error) {
            throw new Error(`Ошибка архивации проекта "${identifier}": ${error.message}`);
        }
    }

    /**
     * Get analytics data
     */
    async getAnalytics(date = null) {
        try {
            const params = new URLSearchParams();
            if (date) params.append('date', date);
            
            const endpoint = `/api/analytics${params.toString() ? '?' + params.toString() : ''}`;
            const response = await this.makeRequest(endpoint);
            return response.data;
        } catch (error) {
            throw new Error(`Ошибка получения аналитики: ${error.message}`);
        }
    }

    /**
     * Get timeline data
     */
    async getTimeline(date = null) {
        try {
            const params = new URLSearchParams();
            if (date) params.append('date', date);
            
            const endpoint = `/api/timeline${params.toString() ? '?' + params.toString() : ''}`;
            const response = await this.makeRequest(endpoint);
            return response.data;
        } catch (error) {
            throw new Error(`Ошибка получения временной шкалы: ${error.message}`);
        }
    }

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await this.makeRequest('/api/health');
            return response.data;
        } catch (error) {
            throw new Error(`Проблема соединения: ${error.message}`);
        }
    }

    /**
     * Test connection to API
     */
    async testConnection() {
        try {
            await this.healthCheck();
            return true;
        } catch (error) {
            return false;
        }
    }
}

/**
 * Notification system
 */
class NotificationManager {
    constructor(containerId = 'notificationArea') {
        this.container = document.getElementById(containerId);
        this.notifications = [];
        this.maxNotifications = 5;
    }

    show(message, type = 'info', duration = 5000) {
        const notification = this.createNotification(message, type);
        
        if (this.notifications.length >= this.maxNotifications) {
            const oldest = this.notifications.shift();
            oldest.remove();
        }
        
        this.notifications.push(notification);
        this.container.appendChild(notification);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }

        return notification;
    }

    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas ${this.getIcon(type)}"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="margin-left: auto; background: none; border: none; cursor: pointer; color: inherit;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add click to dismiss
        notification.addEventListener('click', () => {
            this.remove(notification);
        });

        return notification;
    }

    remove(notification) {
        const index = this.notifications.indexOf(notification);
        if (index > -1) {
            this.notifications.splice(index, 1);
        }
        
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }

    getIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

/**
 * Utility functions
 */
const Utils = {
    /**
     * Format time duration in minutes to human readable format
     */
    formatDuration(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        
        if (hours === 0) {
            return `${mins}м`;
        } else if (mins === 0) {
            return `${hours}ч`;
        } else {
            return `${hours}ч ${mins}м`;
        }
    },

    /**
     * Format project status for display
     */
    formatStatus(status) {
        const statusMap = {
            'active': 'Активный',
            'paused': 'Приостановлен',
            'completed': 'Завершен',
            'archived': 'Архивирован'
        };
        return statusMap[status] || status;
    },

    /**
     * Get status class for styling
     */
    getStatusClass(status) {
        return `status-${status}`;
    },

    /**
     * Show loading state
     */
    showLoading(element, message = 'Загрузка...') {
        element.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                <span>${message}</span>
            </div>
        `;
    },

    /**
     * Show error state
     */
    showError(element, message) {
        element.innerHTML = `
            <div class="error-state" style="text-align: center; padding: 20px; color: #e53e3e;">
                <i class="fas fa-exclamation-triangle" style="font-size: 32px; margin-bottom: 10px;"></i>
                <p>${message}</p>
                <button class="btn btn-secondary btn-sm" onclick="location.reload()">
                    <i class="fas fa-sync-alt"></i> Повторить
                </button>
            </div>
        `;
    },

    /**
     * Debounce function calls
     */
    debounce(func, wait) {
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

    /**
     * Format current time
     */
    getCurrentTime() {
        return new Date().toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TimeTrackerAPI, NotificationManager, Utils };
}  /**
   * Format current time
   */
  getCurrentTime() {
    return new Date().toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit',
    });
  },
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { TimeTrackerAPI, NotificationManager, Utils };
}
