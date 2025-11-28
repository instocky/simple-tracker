/**
 * TimelineChart - Интерактивная временная шкала на основе Chart.js
 * Вертикальная столбчатая диаграмма с часовыми временными слотами
 */

class TimelineChart {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.chart = null;

    // Настройки по умолчанию
    this.options = {
      timeSlots: this.generateTimeSlots(8, 18), // 08:00 - 18:00
      maxMinutes: 60,
      chartHeight: 300,
      showGrid: true,
      showTooltips: true,
      colorScheme: {
        active: '#48bb78', // Зеленый для активности
        low: '#ed8936', // Оранжевый для низкой активности
        medium: '#4299e1', // Синий для средней активности
        high: '#48bb78', // Зеленый для высокой активности
        grid: 'rgba(0,0,0,0.1)',
        background: 'rgba(255,255,255,0.95)',
      },
      ...options,
    };

    this.init();
  }

  /**
   * Генерация временных слотов
   * @param {number} startHour - Начальный час (включительно)
   * @param {number} endHour - Конечный час (исключительно)
   * @returns {Array} Массив временных меток
   */
  generateTimeSlots(startHour, endHour) {
    const slots = [];
    for (let hour = startHour; hour < endHour; hour++) {
      slots.push(`${hour.toString().padStart(2, '0')}:00`);
    }
    return slots;
  }

  /**
   * Инициализация компонента
   */
  init() {
    if (!this.container) {
      console.error(`Container with id '${this.containerId}' not found`);
      return;
    }

    this.setupContainer();
    this.createEmptyChart();
  }

  /**
   * Настройка контейнера для графика
   */
  setupContainer() {
    this.container.innerHTML = `
      <div class="timeline-chart-wrapper">
        <div class="timeline-chart-header">
          <h4><i class="fas fa-chart-bar"></i> Временная активность</h4>
          <div class="chart-controls">
            <button class="btn-toggle" data-mode="minutes" title="Показать в минутах">
              <i class="fas fa-clock"></i>
            </button>
            <button class="btn-toggle" data-mode="percentage" title="Показать в процентах">
              <i class="fas fa-percentage"></i>
            </button>
          </div>
        </div>
        <div class="timeline-chart-container">
          <canvas id="timelineChartCanvas"></canvas>
        </div>
        <div class="timeline-chart-footer">
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-color" style="background: #48bb78;"></span>
              <span>Высокая активность (45-60 мин)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #4299e1;"></span>
              <span>Средняя активность (15-45 мин)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #ed8936;"></span>
              <span>Низкая активность (0-15 мин)</span>
            </div>
          </div>
        </div>
      </div>
    `;

    this.setupEventListeners();
  }

  /**
   * Настройка обработчиков событий
   */
  setupEventListeners() {
    const toggleButtons = this.container.querySelectorAll('.btn-toggle');
    toggleButtons.forEach(button => {
      button.addEventListener('click', e => {
        const mode = e.currentTarget.dataset.mode;
        this.toggleMode(mode);

        // Обновление активной кнопки
        toggleButtons.forEach(btn => btn.classList.remove('active'));
        e.currentTarget.classList.add('active');
      });
    });

    // Активируем первую кнопку по умолчанию
    if (toggleButtons.length > 0) {
      toggleButtons[0].classList.add('active');
    }
  }

  /**
   * Переключение режима отображения (минуты/проценты)
   */
  toggleMode(mode) {
    this.options.currentMode = mode;
    if (this.chart && this.lastData) {
      this.updateChart(this.lastData);
    }
  }

  /**
   * Создание пустого графика
   */
  createEmptyChart() {
    const ctx = document.getElementById('timelineChartCanvas').getContext('2d');

    const config = {
      type: 'bar',
      data: {
        labels: this.options.timeSlots,
        datasets: [
          {
            label: 'Активность',
            data: this.options.timeSlots.map(() => 0),
            backgroundColor: this.options.timeSlots.map(
              () => this.options.colorScheme.grid
            ),
            borderColor: 'transparent',
            borderWidth: 0,
            borderRadius: 8,
            borderSkipped: false,
          },
        ],
      },
      options: this.getChartOptions(),
    };

    this.chart = new Chart(ctx, config);
  }

  /**
   * Получение опций конфигурации Chart.js
   */
  getChartOptions() {
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index',
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          enabled: this.options.showTooltips,
          backgroundColor: 'rgba(0,0,0,0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: '#667eea',
          borderWidth: 1,
          cornerRadius: 8,
          displayColors: false,
          callbacks: {
            title: context => {
              return `Время: ${context[0].label}`;
            },
            label: context => {
              const data = context.raw;
              if (this.options.currentMode === 'percentage') {
                return `Продуктивность: ${Math.round(data)}%`;
              } else {
                return `Активность: ${data} мин`;
              }
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: this.options.maxMinutes,
          grid: {
            display: this.options.showGrid,
            color: this.options.colorScheme.grid,
            drawBorder: false,
            lineWidth: 1,
          },
          ticks: {
            color: '#718096',
            font: {
              size: 12,
            },
            callback: value => {
              if (this.options.currentMode === 'percentage') {
                return `${value}%`;
              } else {
                return `${value}м`;
              }
            },
          },
        },
        x: {
          grid: {
            display: false,
          },
          ticks: {
            color: '#718096',
            font: {
              size: 11,
            },
            maxRotation: 45,
            minRotation: 45,
          },
        },
      },
      animation: {
        duration: 800,
        easing: 'easeInOutCubic',
      },
    };
  }

  /**
   * Обновление данных графика (Clean version)
   */
  updateChart(data) {
    this.lastData = data;
    if (!data) return;

    const processedData = this.processData(data);

    // Удаляем старый график
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }

    const ctx = document.getElementById('timelineChartCanvas');
    if (!ctx) return;

    // Создаем новый
    this.chart = new Chart(ctx.getContext('2d'), {
      type: 'bar',
      data: {
        labels: this.options.timeSlots, // <-- Теперь тут будут динамические часы
        datasets: [
          {
            label: 'Активность',
            data: processedData.minutes,
            backgroundColor: processedData.colors,
            borderColor: 'transparent',
            borderWidth: 0,
            borderRadius: 4,
            borderSkipped: false,
            barPercentage: 0.8,
            categoryPercentage: 0.9,
          },
        ],
      },
      options: this.getChartOptions(),
    });

    if (this.options.currentMode === 'percentage') {
      this.chart.options.scales.y.max = 100;
    } else {
      this.chart.options.scales.y.max = this.options.maxMinutes;
    }
    this.chart.update();
  }

  /**
   * Обработка данных для отображения (processData)
   */
  processData(data) {
    const minutes = [];
    const colors = [];

    this.options.timeSlots.forEach(timeSlot => {
      // Берем данные для конкретного часа
      const slotData = data[timeSlot];

      // Извлекаем активность. Важно: проверяем существование и приводим к числу
      let activeMinutes = 0;

      if (slotData && typeof slotData.active !== 'undefined') {
        activeMinutes = parseInt(slotData.active);
      }

      minutes.push(activeMinutes);

      // Цветовое кодирование
      if (activeMinutes >= 45) {
        colors.push(this.options.colorScheme.high || '#48bb78');
      } else if (activeMinutes >= 15) {
        colors.push(this.options.colorScheme.medium || '#4299e1');
      } else if (activeMinutes > 0) {
        colors.push(this.options.colorScheme.low || '#ed8936');
      } else {
        colors.push(this.options.colorScheme.grid || '#f0f0f0');
      }
    });

    return { minutes, colors };
  }

  /**
   * Загрузка данных из API (Исправленная версия)
   */
  async loadData(date) {
    // 1. Проверяем структуру
    const existingCanvas = document.getElementById('timelineChartCanvas');
    if (!existingCanvas) {
      this.setupContainer();
    }

    try {
      this.showLoading(true); // Включаем спиннер (удаляет canvas)

      // 2. Получаем данные
      const apiData = await this.fetchTimelineData(date);

      // 3. Конвертируем данные
      const chartData = this.convertApiDataToChartFormat(apiData);

      // 4. ВАЖНО: Сначала убираем спиннер и возвращаем canvas!
      this.showLoading(false);

      // 5. Теперь canvas на месте, можно рисовать
      this.updateChart(chartData);
    } catch (error) {
      console.error('Ошибка загрузки данных временной шкалы:', error);
      this.showError('Не удалось загрузить данные');
    }
  }

  /**
   * Получение данных из API через глобальный клиент
   */
  async fetchTimelineData(date) {
    try {
      // Используем глобальный API клиент
      if (typeof window.api !== 'undefined') {
        const data = await window.api.getTimeline(date);
        return data;
      } else {
        throw new Error('API клиент не инициализирован');
      }
    } catch (error) {
      console.error('Ошибка получения данных из API:', error);
      throw error;
    }
  }

  /**
   * Генерация тестовых данных
   */
  generateTestData() {
    const data = {};
    const projects = ['Разработка', 'Встречи', 'Аналитика', 'Планирование'];

    this.options.timeSlots.forEach(timeSlot => {
      const hour = parseInt(timeSlot.split(':')[0]);

      // Различная активность в зависимости от времени
      let activityMultiplier = 1;
      if (hour >= 9 && hour <= 12) activityMultiplier = 1.2; // Утро - более продуктивно
      if (hour >= 14 && hour <= 17) activityMultiplier = 0.8; // После обеда - менее продуктивно
      if (hour >= 18) activityMultiplier = 0.3; // Вечер - низкая активность

      const maxActivity = 60 * activityMultiplier;
      const active = Math.round(Math.random() * maxActivity);

      data[timeSlot] = {
        active: active,
        total: 60,
        project: projects[Math.floor(Math.random() * projects.length)],
      };
    });

    return data;
  }

  /**
   * Парсинг ответа API
   */
  parseApiResponse(response) {
    // Адаптируйте под структуру вашего API
    if (response.timeline) {
      return this.convertApiTimelineToChartData(response.timeline);
    }
    return response;
  }

  /**
   * Конвертация API данных в формат для графика
   */
  convertApiTimelineToChartData(apiData) {
    // Реализуйте конвертацию под ваш API формат
    const chartData = {};

    this.options.timeSlots.forEach(timeSlot => {
      chartData[timeSlot] = {
        active: Math.round(Math.random() * 60), // Заглушка
        total: 60,
      };
    });

    return chartData;
  }

  /**
   * Конвертация данных API в формат для Chart.js
   * (Динамическое обновление временной шкалы)
   */
  convertApiDataToChartFormat(apiData) {
    const chartData = {};

    // 1. Обработка нового формата JSON (hourly_data)
    if (
      apiData &&
      Array.isArray(apiData.hourly_data) &&
      apiData.hourly_data.length > 0
    ) {
      // ВАЖНО: Обновляем список временных слотов на основе данных сервера!
      // Теперь график сам подстроится под диапазон (например, 08:00 - 20:00)
      this.options.timeSlots = apiData.hourly_data.map(item => item.hour);

      // Инициализируем структуру под новые слоты
      this.options.timeSlots.forEach(timeSlot => {
        chartData[timeSlot] = {
          active: 0,
          total: 60,
          project: 'Нет активности',
        };
      });

      // Заполняем данными
      apiData.hourly_data.forEach(item => {
        if (chartData[item.hour]) {
          chartData[item.hour].active = item.active_minutes;

          if (item.active_minutes > 0) {
            chartData[
              item.hour
            ].project = `Активность: ${item.active_minutes} мин`;
          }
        }
      });

      return chartData;
    }

    // 2. Fallback для старых форматов (если вдруг raw_output)
    // Тут оставляем старые слоты (8-18) по умолчанию
    if (apiData && apiData.raw_output) {
      return this.parseRawOutput(apiData.raw_output);
    }

    return chartData;
  }

  /**
   * Извлечение временного слота из временной метки
   */
  extractTimeSlot(timestamp) {
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) return null;

      const hour = date.getHours();
      const timeSlot = `${hour.toString().padStart(2, '0')}:00`;

      // Проверяем, находится ли час в диапазоне 8-18
      if (hour >= 8 && hour < 18) {
        return timeSlot;
      }
      return null;
    } catch (error) {
      console.warn('Ошибка парсинга временной метки:', timestamp);
      return null;
    }
  }

  /**
   * Парсинг текстового вывода (raw_output)
   */
  parseRawOutput(rawOutput) {
    const chartData = {};

    // Инициализация всех временных слотов
    this.options.timeSlots.forEach(timeSlot => {
      chartData[timeSlot] = {
        active: 0,
        total: 60,
        project: 'Нет активности',
      };
    });

    try {
      // Простой парсинг текста с поиском паттернов времени
      const lines = rawOutput.split('\n');
      const timePattern = /(\d{2}):(\d{2})\s*-?\s*(\d{2}):(\d{2})/g;
      const projectPattern = /([A-Za-zА-Яа-я0-9\s]+?)(?=\s+\d+м|$)/g;

      let currentTimeSlot = null;

      lines.forEach(line => {
        const timeMatch = timePattern.exec(line);
        if (timeMatch) {
          const startHour = parseInt(timeMatch[1]);
          if (startHour >= 8 && startHour < 18) {
            currentTimeSlot = `${startHour.toString().padStart(2, '0')}:00`;
          }
        }

        // Поиск информации о проекте
        if (currentTimeSlot && chartData[currentTimeSlot]) {
          const projectMatch = projectPattern.exec(line);
          if (projectMatch) {
            const projectName = projectMatch[1].trim();
            if (projectName.length > 0 && projectName !== '0м') {
              chartData[currentTimeSlot].project = projectName;
            }
          }

          // Поиск продолжительности
          const durationMatch = line.match(/(\d+)м/);
          if (durationMatch) {
            const minutes = parseInt(durationMatch[1]);
            chartData[currentTimeSlot].active = Math.max(
              chartData[currentTimeSlot].active,
              minutes
            );
          }
        }
      });
    } catch (error) {
      console.error('Ошибка парсинга raw_output:', error);
    }

    return chartData;
  }

  /**
   * Показать/скрыть индикатор загрузки
   */
  showLoading(show) {
    const canvasContainer = this.container.querySelector(
      '.timeline-chart-container'
    );
    if (show && canvasContainer) {
      canvasContainer.innerHTML = `
        <div class="loading-overlay">
          <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
          </div>
          <div class="loading-text">Загрузка данных...</div>
        </div>
      `;
    } else if (!show) {
      // Восстанавливаем canvas если он был заменен на loading
      const existingCanvas = this.container.querySelector(
        '#timelineChartCanvas'
      );
      if (!existingCanvas && canvasContainer) {
        canvasContainer.innerHTML =
          '<canvas id="timelineChartCanvas"></canvas>';
        this.createEmptyChart(); // Пересоздаем график
      }
    }
  }

  /**
   * Показать ошибку
   */
  showError(message) {
    const canvasContainer = this.container.querySelector(
      '.timeline-chart-container'
    );
    if (canvasContainer) {
      canvasContainer.innerHTML = `
        <div class="error-message">
          <i class="fas fa-exclamation-triangle"></i>
          <div class="error-text">${message}</div>
        </div>
      `;
    } else {
      // Fallback - показываем ошибку в самом контейнере
      this.container.innerHTML = `
        <div class="timeline-chart-wrapper">
          <div class="timeline-chart-header">
            <h4><i class="fas fa-chart-bar"></i> Временная активность</h4>
          </div>
          <div class="timeline-chart-container">
            <div class="error-message">
              <i class="fas fa-exclamation-triangle"></i>
              <div class="error-text">${message}</div>
            </div>
          </div>
        </div>
      `;
    }
  }

  /**
   * Уничтожение компонента
   */
  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }
}

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TimelineChart;
}
