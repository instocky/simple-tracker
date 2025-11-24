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
      activeProjectDisplay: document.getElementById('activeProjectDisplay'),
      timelineContent: document.getElementById('timelineContent'),
      statsContent: document.getElementById('statsContent'),
      refreshBtn: document.getElementById('refreshBtn'),
      analyticsDate: document.getElementById('analyticsDate'),
      startFirstProject: document.getElementById('startFirstProject'),
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

      // Start auto-refresh
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

    // Start first project button
    this.elements.startFirstProject.addEventListener('click', () => {
      this.startFirstAvailableProject();
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
   * Start auto-refresh every 5 seconds
   */
  startAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }

    this.refreshInterval = setInterval(() => {
      if (!this.isRefreshing) {
        this.refreshActiveData();
      }
    }, 5000); // 5 seconds
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
      await Promise.all([
        this.loadActiveProject(),
        this.loadProjects(),
        this.loadAnalytics(),
      ]);

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
   */
  async refreshActiveData() {
    try {
      await Promise.all([this.loadActiveProject(), this.updateProjectTimers()]);
    } catch (error) {
      console.warn('⚠️ Auto-refresh failed:', error);
    }
  }

  /**
   * Load and display active project
   */
  async loadActiveProject() {
    try {
      const data = await this.api.getActiveProject();
      this.renderActiveProject(data.project);
    } catch (error) {
      console.error('❌ Error loading active project:', error);
      Utils.showError(this.elements.activeProjectDisplay, error.message);
    }
  }

  /**
   * Render active project display
   */
  renderActiveProject(activeProject) {
    const container = this.elements.activeProjectDisplay;

    if (!activeProject) {
      container.innerHTML = `
                <div class="no-active-project">
                    <i class="fas fa-pause-circle"></i>
                    <p>Нет активного проекта</p>
                    <button id="startFirstProject" class="btn btn-primary">
                        Запустить первый проект
                    </button>
                </div>
            `;

      // Re-bind the click event
      container
        .querySelector('#startFirstProject')
        .addEventListener('click', () => {
          this.startFirstAvailableProject();
        });
    } else {
      container.innerHTML = `
                <div class="active-project-info">
                    <div class="project-details">
                        <h3><i class="fas fa-play-circle"></i> ${
                          activeProject.title
                        }</h3>
                        <p>${activeProject.description || 'Без описания'}</p>
                    </div>
                    <div class="project-timer">
                        <span id="activeTimer">${
                          activeProject.total_time
                        }</span>
                    </div>
                </div>
            `;
    }
  }

  /**
   * Load and display all projects
   */
  async loadProjects() {
    try {
      Utils.showLoading(this.elements.projectsList, 'Загрузка проектов...');

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
                        <h4>${project.title}</h4>
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
                    ${this.getProjectActions(project)}
                </div>
            </div>
        `
      )
      .join('');

    // Bind action buttons
    this.bindProjectActions();
  }

  /**
   * Get action buttons HTML for project
   */
  getProjectActions(project) {
    const identifier = project.id;
    const actions = [];

    switch (project.status) {
      case 'active':
        actions.push(`
                    <button class="btn btn-warning btn-sm" onclick="dashboard.pauseProject('${identifier}')">
                        <i class="fas fa-pause"></i> Пауза
                    </button>
                `);
        actions.push(`
                    <button class="btn btn-success btn-sm" onclick="dashboard.completeProject('${identifier}')">
                        <i class="fas fa-check"></i> Завершить
                    </button>
                `);
        break;

      case 'paused':
        actions.push(`
                    <button class="btn btn-success btn-sm" onclick="dashboard.startProject('${identifier}')">
                        <i class="fas fa-play"></i> Запустить
                    </button>
                `);
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
                    <button class="btn btn-success btn-sm" onclick="dashboard.startProject('${identifier}')">
                        <i class="fas fa-play"></i> Продолжить
                    </button>
                `);
        actions.push(`
                    <button class="btn btn-danger btn-sm" onclick="dashboard.archiveProject('${identifier}')">
                        <i class="fas fa-archive"></i> Архив
                    </button>
                `);
        break;

      case 'archived':
        actions.push(`
                    <button class="btn btn-success btn-sm" onclick="dashboard.startProject('${identifier}')">
                        <i class="fas fa-play"></i> Восстановить
                    </button>
                `);
        break;
    }

    return actions.join('');
  }

  /**
   * Bind project action events
   */
  bindProjectActions() {
    // Event binding is handled by onclick handlers in getProjectActions
    console.log('🔗 Project action events bound');
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
   * Update project timers (for auto-refresh)
   */
  updateProjectTimers() {
    const activeTimer = document.getElementById('activeTimer');
    if (activeTimer) {
      // Update timer display - in a real implementation,
      // you would calculate elapsed time from start
      const now = Utils.getCurrentTime();
      activeTimer.textContent = now;
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
   * Start the first available project
   */
  async startFirstAvailableProject() {
    try {
      const data = await this.api.getProjects();
      const projects = data.projects;

      if (projects && projects.length > 0) {
        // Find first non-archived project
        const firstProject = projects.find(p => p.status !== 'archived');
        if (firstProject) {
          await this.startProject(firstProject.id);
        } else {
          this.notifications.warning('Нет доступных проектов для запуска');
        }
      } else {
        this.notifications.warning('Нет проектов для запуска');
      }
    } catch (error) {
      this.notifications.error(`Ошибка запуска проекта: ${error.message}`);
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
