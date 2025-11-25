/**
 * Simple Time Tracker Dashboard
 * Main dashboard logic and UI management
 */

class Dashboard {
  constructor() {
    this.api = new TimeTrackerAPI();
    this.notifications = new NotificationManager();
    this.refreshInterval = null;
    this.isRefreshing = false;

    // UI elements
    this.elements = {
      connectionStatus: document.getElementById('connectionStatus'),
      projectsList: document.getElementById('projectsList'),
      timelineContent: document.getElementById('timelineContent'),
      statsContent: document.getElementById('statsContent'),
      refreshBtn: document.getElementById('refreshBtn'),
      analyticsDate: document.getElementById('analyticsDate'),
    };

    this.init();
  }

  /**
   * Initialize dashboard
   */
  async init() {
    try {
      console.log('🚀 Initializing Dashboard...');

      // Set up event listeners
      this.setupEventListeners();

      // Initialize date input
      this.elements.analyticsDate.valueAsDate = new Date();

      // Check connection and load data
      await this.checkConnection();
      await this.refreshAllData();

      // Start auto-refresh (every 30 seconds without loading indicator)
      this.startAutoRefresh();

      console.log('✅ Dashboard initialized successfully');
    } catch (error) {
      console.error('❌ Dashboard initialization failed:', error);
      this.notifications.error(`Ошибка инициализации: ${error.message}`);
      this.updateConnectionStatus('disconnected');
    }
  }

  /**
   * Set up event listeners
   */
  setupEventListeners() {
    // Refresh button
    this.elements.refreshBtn.addEventListener('click', () => {
      this.refreshAllData();
    });

    // Date change for analytics
    this.elements.analyticsDate.addEventListener('change', () => {
      this.loadAnalytics();
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', e => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'r':
            e.preventDefault();
            this.refreshAllData();
            break;
        }
      }
    });

    // Project toggle buttons using event delegation
    this.elements.projectsList.addEventListener('click', async e => {
      const button = e.target.closest('.toggle-project-btn');
      if (button) {
        e.preventDefault();
        const projectId = button.dataset.projectId;
        const currentStatus = button.dataset.currentStatus;
        await this.toggleProjectStatus(projectId, button);
      }
    });

    console.log('🔗 Event listeners set up with delegation');
  }

  /**
   * Check API connection
   */
  async checkConnection() {
    try {
      this.updateConnectionStatus('connecting');

      const isConnected = await this.api.testConnection();

      if (isConnected) {
        this.updateConnectionStatus('connected');
        console.log('✅ API connection successful');
        return true;
      } else {
        throw new Error('Connection test failed');
      }
    } catch (error) {
      console.error('❌ API connection failed:', error);
      this.updateConnectionStatus('disconnected');
      throw error;
    }
  }

  /**
   * Update connection status UI
   */
  updateConnectionStatus(status) {
    const statusEl = this.elements.connectionStatus;
    statusEl.className = `connection-status ${status}`;

    const statusMap = {
      connected: { text: 'Подключено', icon: 'fa-wifi' },
      disconnected: { text: 'Отключено', icon: 'fa-wifi-slash' },
      connecting: { text: 'Подключение...', icon: 'fa-spinner fa-spin' },
    };

    const statusInfo = statusMap[status];
    statusEl.innerHTML = `
            <i class="fas ${statusInfo.icon}"></i>
            <span>${statusInfo.text}</span>
        `;
  }

  /**
   * Start auto-refresh every 30 seconds (without loading indicator)
   */
  startAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }

    this.refreshInterval = setInterval(() => {
      if (!this.isRefreshing) {
        this.refreshActiveData();
      }
    }, 30000); // 30 seconds
  }

  /**
   * Refresh all dashboard data
   */
  async refreshAllData() {
    if (this.isRefreshing) return;

    this.isRefreshing = true;
    this.elements.refreshBtn.disabled = true;
    this.elements.refreshBtn.innerHTML =
      '<i class="fas fa-spinner fa-spin"></i> Обновление...';

    try {
      console.log('🔄 Refreshing all data...');

      // Refresh data in parallel
      await Promise.all([this.loadProjects(true), this.loadAnalytics()]);

      console.log('✅ All data refreshed successfully');
      this.notifications.success('Данные обновлены');
    } catch (error) {
      console.error('❌ Error refreshing data:', error);
      this.notifications.error(`Ошибка обновления: ${error.message}`);
    } finally {
      this.isRefreshing = false;
      this.elements.refreshBtn.disabled = false;
      this.elements.refreshBtn.innerHTML =
        '<i class="fas fa-sync-alt"></i> Обновить';
    }
  }

  /**
   * Refresh only active data (for auto-refresh)
   * Updates projects without showing loading indicator to prevent flickering
   */
  async refreshActiveData() {
    try {
      await this.loadProjects(false); // false = don't show loading indicator
    } catch (error) {
      console.warn('⚠️ Auto-refresh failed:', error);
    }
  }

  /**
   * Load and display all projects
   */
  async loadProjects(showLoading = true) {
    try {
      // Only show loading indicator if explicitly requested and container is empty or showing error
      const container = this.elements.projectsList;
      const shouldShowLoading =
        showLoading &&
        (!container.innerHTML.trim() ||
          container.querySelector('.loading') ||
          container.querySelector('.error') ||
          container.querySelector('.no-projects'));

      if (shouldShowLoading) {
        Utils.showLoading(container, 'Загрузка проектов...');
      }

      const data = await this.api.getProjects();
      this.renderProjects(data.projects);
    } catch (error) {
      console.error('❌ Error loading projects:', error);
      Utils.showError(this.elements.projectsList, error.message);
    }
  }

  /**
   * Render projects list
   */
  renderProjects(projects) {
    const container = this.elements.projectsList;

    if (!projects || projects.length === 0) {
      container.innerHTML = `
                <div class="no-projects" style="text-align: center; padding: 40px; color: #718096;">
                    <i class="fas fa-folder-open" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <p>Нет проектов</p>
                    <p style="font-size: 14px; margin-top: 8px;">Создайте первый проект через командную строку</p>
                </div>
            `;
      return;
    }

    container.innerHTML = projects
      .map(
        project => `
            <div class="project-item ${
              project.status === 'active' ? 'active' : ''
            }">
                <div class="project-header">
                    <div class="project-info">
                        <h4>${project.id}</h4>
                        <p>${project.description || 'Без описания'}</p>
                    </div>
                    <div class="project-status ${Utils.getStatusClass(
                      project.status
                    )}">
                        ${Utils.formatStatus(project.status)}
                    </div>
                </div>
                
                <div class="project-stats">
                    <div class="stat">
                        <span class="stat-value">${project.total_time}</span>
                        <span class="stat-label">Общее время</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${
                          project.aggregated_time
                        }</span>
                        <span class="stat-label">Активное время</span>
                    </div>
                </div>
                
                <div class="project-actions">
                    <!-- Universal Start/Pause Button -->
                    <button class="btn ${
                      project.status === 'active'
                        ? 'btn-warning'
                        : 'btn-success'
                    } btn-sm toggle-project-btn" 
                            data-project-id="${project.id}" 
                            data-current-status="${project.status}">
                        <i class="fas ${
                          project.status === 'active' ? 'fa-pause' : 'fa-play'
                        }"></i>
                        <span class="btn-text">${
                          project.status === 'active' ? 'Пауза' : 'Запустить'
                        }</span>
                    </button>
                    
                    ${this.getOtherProjectActions(project)}
                </div>
            </div>
        `
      )
      .join('');

    // Bind action buttons
    this.bindProjectActions();
  }

  /**
   * Get additional action buttons HTML for project (excluding universal start/pause button)
   */
  getOtherProjectActions(project) {
    const identifier = project.id;
    const actions = [];

    switch (project.status) {
      case 'active':
        actions.push(`
                    <button class="btn btn-success btn-sm" onclick="dashboard.completeProject('${identifier}')">
                        <i class="fas fa-check"></i> Завершить
                    </button>
                `);
        break;

      case 'paused':
        actions.push(`
                    <button class="btn btn-success btn-sm" onclick="dashboard.completeProject('${identifier}')">
                        <i class="fas fa-check"></i> Завершить
                    </button>
                `);
        actions.push(`
                    <button class="btn btn-danger btn-sm" onclick="dashboard.archiveProject('${identifier}')">
                        <i class="fas fa-archive"></i> Архив
                    </button>
                `);
        break;

      case 'completed':
        actions.push(`
                    <button class="btn btn-danger btn-sm" onclick="dashboard.archiveProject('${identifier}')">
                        <i class="fas fa-archive"></i> Архив
                    </button>
                `);
        break;

      case 'archived':
        // No additional actions for archived projects
        break;
    }

    return actions.join('');
  }

  /**
   * Bind project action events
   */
  bindProjectActions() {
    // Events are now handled by delegation in setupEventListeners
    console.log('🔗 Project action events ready (delegated)');
  }

  /**
   * Load and display analytics
   */
  async loadAnalytics() {
    try {
      const date = this.elements.analyticsDate.value;

      Utils.showLoading(
        this.elements.timelineContent,
        'Загрузка временной шкалы...'
      );
      Utils.showLoading(this.elements.statsContent, 'Загрузка статистики...');

      const [timelineData, statsData] = await Promise.all([
        this.api.getTimeline(date),
        this.api.getAnalytics(date),
      ]);

      this.renderTimeline(timelineData.timeline);
      this.renderStats(statsData.analytics);
    } catch (error) {
      console.error('❌ Error loading analytics:', error);
      Utils.showError(this.elements.timelineContent, error.message);
      Utils.showError(this.elements.statsContent, error.message);
    }
  }

  /**
   * Render timeline data
   */
  renderTimeline(timelineData) {
    const container = this.elements.timelineContent;

    if (!timelineData || !timelineData.raw_output) {
      container.innerHTML = `
                <div class="no-data" style="text-align: center; padding: 20px; color: #718096;">
                    <i class="fas fa-calendar-times" style="font-size: 32px; margin-bottom: 10px;"></i>
                    <p>Нет данных временной шкалы</p>
                </div>
            `;
      return;
    }

    container.innerHTML = `
            <div class="timeline-data">
                <pre style="background: #f7fafc; padding: 15px; border-radius: 8px; font-size: 12px; white-space: pre-wrap; overflow-x: auto;">${timelineData.raw_output}</pre>
            </div>
        `;
  }

  /**
   * Render statistics data
   */
  renderStats(statsData) {
    const container = this.elements.statsContent;

    if (!statsData || !statsData.raw_output) {
      container.innerHTML = `
                <div class="no-data" style="text-align: center; padding: 20px; color: #718096;">
                    <i class="fas fa-chart-bar" style="font-size: 32px; margin-bottom: 10px;"></i>
                    <p>Нет статистических данных</p>
                </div>
            `;
      return;
    }

    container.innerHTML = `
            <div class="stats-data">
                <pre style="background: #f7fafc; padding: 15px; border-radius: 8px; font-size: 12px; white-space: pre-wrap; overflow-x: auto;">${statsData.raw_output}</pre>
            </div>
        `;
  }

  /**
   * Auto-scroll projects list to top
   */
  scrollProjectsToTop() {
    // Smooth scroll to top of projects list
    this.elements.projectsList.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  }

  /**
   * Toggle project status (start/pause)
   */
  async toggleProjectStatus(identifier, buttonElement) {
    const originalContent = buttonElement.innerHTML;
    const buttonText = buttonElement.querySelector('.btn-text');
    const icon = buttonElement.querySelector('i');

    try {
      // Disable button during operation
      buttonElement.disabled = true;
      buttonElement.innerHTML =
        '<i class="fas fa-spinner fa-spin"></i> Обработка...';

      const currentStatus = buttonElement.dataset.currentStatus;
      let newStatus;

      if (currentStatus === 'active') {
        // Pause the project
        await this.api.pauseProject(identifier);
        newStatus = 'paused';
        this.notifications.success(`Проект "${identifier}" приостановлен`);
      } else {
        // Start the project
        await this.api.startProject(identifier);
        newStatus = 'active';
        this.notifications.success(`Проект "${identifier}" запущен`);
      }

      // Update button appearance
      buttonElement.dataset.currentStatus = newStatus;

      if (newStatus === 'active') {
        buttonElement.className = 'btn btn-warning btn-sm toggle-project-btn';
        icon.className = 'fas fa-pause';
        buttonText.textContent = 'Пауза';
      } else {
        buttonElement.className = 'btn btn-success btn-sm toggle-project-btn';
        icon.className = 'fas fa-play';
        buttonText.textContent = 'Запустить';
      }

      // Refresh data to update other UI elements
      await this.refreshActiveData();

      // Auto-scroll to top to show the project that was just changed
      this.scrollProjectsToTop();
    } catch (error) {
      console.error('Error toggling project status:', error);
      this.notifications.error(`Ошибка изменения статуса: ${error.message}`);

      // Restore original button content on error
      buttonElement.innerHTML = originalContent;
    } finally {
      buttonElement.disabled = false;
    }
  }

  /**
   * Project action methods
   */
  async startProject(identifier) {
    try {
      await this.api.startProject(identifier);
      this.notifications.success(`Проект "${identifier}" запущен`);
      await this.refreshActiveData();
    } catch (error) {
      this.notifications.error(error.message);
    }
  }

  async pauseProject(identifier) {
    try {
      await this.api.pauseProject(identifier);
      this.notifications.success(`Проект "${identifier}" приостановлен`);
      await this.refreshActiveData();
    } catch (error) {
      this.notifications.error(error.message);
    }
  }

  async completeProject(identifier) {
    try {
      await this.api.completeProject(identifier);
      this.notifications.success(`Проект "${identifier}" завершен`);
      await this.refreshActiveData();
    } catch (error) {
      this.notifications.error(error.message);
    }
  }

  async archiveProject(identifier) {
    try {
      await this.api.archiveProject(identifier);
      this.notifications.success(`Проект "${identifier}" архивирован`);
      await this.refreshActiveData();
    } catch (error) {
      this.notifications.error(error.message);
    }
  }

  /**
   * Cleanup and destroy dashboard
   */
  destroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }

    console.log('🧹 Dashboard destroyed');
  }
}

// Initialize dashboard when DOM is ready
let dashboard;

document.addEventListener('DOMContentLoaded', () => {
  console.log('🎯 DOM loaded, initializing dashboard...');
  dashboard = new Dashboard();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
  if (dashboard) {
    dashboard.destroy();
  }
});

// Export for global access
window.Dashboard = Dashboard;
