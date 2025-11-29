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
        active: '#10b981', // Emerald для активности
        low: '#f59e0b', // Amber для низкой активности
        medium: '#3b82f6', // Blue для средней активности
        high: '#10b981', // Emerald для высокой активности
        grid: 'rgba(0,0,0,0.08)',
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
        
        <!-- НАЧАЛО КОНТЕЙНЕРА -->
        <div class="timeline-chart-container" style="position: relative; width: 100%; height: 300px; min-width: 0;">
            <!-- Канвас должен быть ВНУТРИ -->
            <canvas id="timelineChartCanvas"></canvas>
        </div> 
        <!-- КОНЕЦ КОНТЕЙНЕРА (закрывающий div строго после canvas) -->

        <div class="timeline-chart-footer" style="border-top: none;">
          <div class="chart-legend-enhanced">
            <div class="legend-enhanced-item">
              <div class="legend-enhanced-color project"></div>
              <span><strong>Проектная работа</strong> (сплошная заливка)</span>
            </div>
            <div class="legend-enhanced-item">
              <div class="legend-enhanced-color background"></div>
              <span><strong>Фоновая активность</strong> (штриховка)</span>
            </div>
            <div class="legend-enhanced-item">
              <span class="legend-color" style="background: #10b981;"></span>
              <span>Высокая активность (45-60 мин)</span>
            </div>
            <div class="legend-enhanced-item">
              <span class="legend-color" style="background: #3b82f6;"></span>
              <span>Средняя активность (15-45 мин)</span>
            </div>
            <div class="legend-enhanced-item">
              <span class="legend-color" style="background: #f59e0b;"></span>
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
      resizeDelay: 100, // Мгновенная реакция (можно поставить 100 для оптимизации)
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
          displayColors: true,
          callbacks: {
            title: context => {
              return `Время: ${context[0].label}`;
            },
            label: context => {
              const data = context.raw;
              const datasetLabel = context.dataset.label;
              if (this.options.currentMode === 'percentage') {
                return `${datasetLabel}: ${Math.round(data)}%`;
              } else {
                return `${datasetLabel}: ${data} мин`;
              }
            },
            afterBody: context => {
              // НОВАЯ логика тултипов с поддержкой Task Swimlanes (F4)
              const dataPoint = context[0];
              const totalMinutes = dataPoint.dataset.data[dataPoint.dataIndex];
              const projectDatasetIndex = dataPoint.datasetIndex === 0 ? 1 : 0; // Индекс проекта
              const projectMinutes =
                dataPoint.chart.data.datasets[projectDatasetIndex].data[
                  dataPoint.dataIndex
                ];
              const backgroundMinutes = totalMinutes - projectMinutes;

              // Получаем задачи для этого временного слота
              const slotIndex = dataPoint.dataIndex;
              const tasks =
                this.lastData[this.options.timeSlots[slotIndex]]?.tasks || [];

              const tooltipLines = [
                '',
                `Общая активность: ${totalMinutes} мин`,
                `Проектная работа: ${projectMinutes} мин`,
                `Фоновая активность: ${backgroundMinutes} мин`,
              ];

              // Добавляем разбивку по задачам если есть
              if (tasks.length > 0) {
                tooltipLines.push('');
                tooltipLines.push('Проекты:');

                tasks.forEach(task => {
                  const emoji = this.getTaskEmoji(task.title);
                  const color =
                    task.color || this.getProjectColor(task.id, task.title);
                  tooltipLines.push(
                    `${emoji} ${task.title}: ${task.minutes} мин`
                  );
                });
              }

              return tooltipLines;
            },
          },
        },
      },
      scales: {
        x: {
          stacked: true,
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
        y: {
          stacked: true,
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
        // НОВАЯ ОСЬ
        y_tasks: {
          display: false,
          min: 0,
          max: 40, // Если поставить 20 - полоска будет толще. Если 60 - тоньше.
          grid: { display: false },
        },
      },
      animation: {
        duration: 800,
        easing: 'easeInOutCubic',
      },
    };
  }

  /**
   * Подготавливает данные для Task Strips (F3)
   * Создает плавающие полоски для отображения проектов
   * @param {Object} processedData - Обработанные данные графика
   * @returns {Object} Данные для dataset полосок задач
   */
  prepareTaskStripsData(processedData) {
    const taskStripsData = [];
    const taskStripColors = [];

    // Фиксированная высота полоски (5 пикселей от оси X)
    const stripHeight = 5;

    this.options.timeSlots.forEach((timeSlot, index) => {
      const slotTasks = processedData.tasks[index] || [];

      if (slotTasks.length === 0) {
        // Если нет задач, создаем пустую полоску
        taskStripsData.push([0, 2]);
        taskStripColors.push('transparent');
      } else {
        // Находим позицию для полоски (чуть ниже оси X)
        const stripStart = -stripHeight - 2; // 2px отступ от оси
        const stripEnd = 2; // 2px отступ от оси

        // Если несколько задач, показываем только первую (основную)
        const mainTask = slotTasks[0];
        taskStripsData.push([stripStart, stripEnd]);

        // Генерируем цвет для полоски
        const color = this.getProjectColor(
          mainTask.id,
          mainTask.title,
          mainTask.color
        );
        taskStripColors.push(color);
      }
    });

    return {
      data: taskStripsData,
      colors: taskStripColors,
    };
  }

  /**
   * Обновление данных графика
   * Реализует гибридный вид: сплошные полоски задач снизу + раздельные столбики активности сверху
   */
  updateChart(data) {
    this.lastData = data;
    if (!data) return;

    const processed = this.processData(data);
    const ctx = document.getElementById('timelineChartCanvas').getContext('2d');

    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }

    // 1. Подготовка данных для верхних столбиков (Фон = Всего - Проект)
    const bgData = processed.totalMinutes.map((total, i) =>
      Math.max(0, total - processed.projectMinutes[i])
    );

    // 2. Подготовка данных для нижних полосок (Tasks Strips)
    // Формируем массив Floating Bars: [нижняя_граница, верхняя_граница]
    const taskStripsData = [];
    const taskStripsColors = [];

    this.options.timeSlots.forEach((slot, index) => {
      const tasks = processed.tasks[index] || [];

      if (tasks.length > 0) {
        // Рисуем полоску от -2 до 0 (по оси y_tasks)
        // Это создаст тонкую линию под основной осью X
        taskStripsData.push([2, 4]);

        // Определяем цвет полоски по основному проекту часа
        const mainTask = tasks[0];
        const color = mainTask.color || this.stringToColor(mainTask.title);
        taskStripsColors.push(color);
      } else {
        // Если задач нет, пустая точка
        taskStripsData.push(null);
        taskStripsColors.push('transparent');
      }
    });

    // 3. Генерация паттернов и улучшенных цветов
    const enhancedProjectColors = processed.colors.map(c =>
      this.enhanceColorForPremium(c)
    );
    const bgPatterns = processed.colors.map(c => this.createHatchPattern(c));

    // 4. Создание графика
    this.chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: this.options.timeSlots,
        datasets: [
          // === СЛОЙ 1: ЗАДАЧИ (Сплошная линия снизу) ===
          {
            label: 'Tasks',
            data: taskStripsData,
            backgroundColor: taskStripsColors,
            borderColor: 'transparent',
            borderWidth: 0,

            // МАГИЯ СПЛОШНОЙ ЛИНИИ:
            barPercentage: 1.0, // Занимать 100% ширины слота
            categoryPercentage: 1.0, // Занимать 100% ширины категории
            borderSkipped: false, // Рисовать все границы
            borderRadius: 0, // Без скруглений для идеальной стыковки

            yAxisID: 'y_tasks', // Привязка к скрытой нижней оси
            order: 1, // Рисуется первым (визуально снизу)
          },

          // === СЛОЙ 2: ПРОЕКТНАЯ РАБОТА (Столбики) ===
          {
            label: 'Проектная работа',
            data: processed.projectMinutes,
            backgroundColor: enhancedProjectColors,
            borderColor: 'transparent',
            borderWidth: 0,

            // Настройки для раздельных столбиков:
            barPercentage: 0.8, // Отступы между часами
            categoryPercentage: 0.9,
            // Скругление только внизу (где стык со стрипом)
            borderRadius: {
              topLeft: 0,
              topRight: 0,
              bottomLeft: 4,
              bottomRight: 4,
            },
            borderSkipped: false,

            yAxisID: 'y', // Привязка к основной оси
            order: 2,
          },

          // === СЛОЙ 3: ФОНОВАЯ АКТИВНОСТЬ (Столбики) ===
          {
            label: 'Фоновая активность',
            data: bgData,
            backgroundColor: bgPatterns,
            borderColor: 'transparent',
            borderWidth: 0,

            // Настройки для раздельных столбиков:
            barPercentage: 0.8,
            categoryPercentage: 0.9,
            // Скругление только сверху
            borderRadius: {
              topLeft: 4,
              topRight: 4,
              bottomLeft: 0,
              bottomRight: 0,
            },
            borderSkipped: false,

            yAxisID: 'y', // Привязка к основной оси
            order: 3,
          },
        ],
      },
      options: this.getChartOptions(),
    });

    // Обновляем максимум оси Y в зависимости от режима
    if (this.options.currentMode === 'percentage') {
      this.chart.options.scales.y.max = 100;
    } else {
      this.chart.options.scales.y.max = this.options.maxMinutes;
    }

    this.chart.update();
  }

  /**
   * Создает CanvasPattern для штриховки (Hatch Pattern)
   * Chart.js не понимает CSS gradients, поэтому рисуем паттерн вручную на микро-канвасе
   */
  createHatchPattern(color) {
    // Создаем виртуальный canvas 10x10 пикселей
    const shape = document.createElement('canvas');
    shape.width = 10;
    shape.height = 10;
    const c = shape.getContext('2d');

    // Получаем RGB компоненты цвета
    const enhancedColor = this.enhanceColorForPremium(color);
    const hex = enhancedColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);

    // 1. Рисуем легкий полупрозрачный фон
    c.fillStyle = `rgba(${r}, ${g}, ${b}, 0.15)`;
    c.fillRect(0, 0, 10, 10);

    // 2. Рисуем диагональную линию (штрих)
    c.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.5)`; // Цвет полоски чуть темнее фона
    c.lineWidth = 1.5; // Толщина полоски
    c.beginPath();
    // Рисуем линию из левого нижнего в правый верхний угол
    c.moveTo(0, 10);
    c.lineTo(10, 0);
    c.stroke();

    // Возвращаем паттерн
    const ctx = document.getElementById('timelineChartCanvas').getContext('2d');
    return ctx.createPattern(shape, 'repeat');
  }

  /**
   * Обработка данных для отображения (processData) с поддержкой Task Swimlanes
   */
  processData(data) {
    const totalMinutes = [];
    const projectMinutes = [];
    const colors = [];
    const tasks = []; // НОВОЕ: массив задач для каждого часа

    this.options.timeSlots.forEach(timeSlot => {
      // Берем данные для конкретного часа
      const slotData = data[timeSlot];

      // Извлекаем активность. Важно: проверяем существование и приводим к числу
      let activeMinutes = 0;
      let projMinutes = 0;
      let slotTasks = []; // НОВОЕ: задачи для этого часа

      if (slotData && typeof slotData.active !== 'undefined') {
        activeMinutes = parseInt(slotData.active);
        projMinutes = parseInt(slotData.project || slotData.active);
        slotTasks = slotData.tasks || []; // НОВОЕ: извлекаем задачи
      }

      totalMinutes.push(activeMinutes);
      projectMinutes.push(projMinutes);
      tasks.push(slotTasks); // НОВОЕ: добавляем задачи

      // Цветовое кодирование для общего времени с премиальной палитрой
      if (activeMinutes >= 45) {
        colors.push(this.options.colorScheme.high || '#10b981'); // Emerald
      } else if (activeMinutes >= 15) {
        colors.push(this.options.colorScheme.medium || '#3b82f6'); // Blue
      } else if (activeMinutes > 0) {
        colors.push(this.options.colorScheme.low || '#f59e0b'); // Amber
      } else {
        colors.push(this.options.colorScheme.grid || '#f0f0f0');
      }
    });

    return { totalMinutes, projectMinutes, colors, tasks };
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
          project: 0,
          total: 60,
          projectName: 'Нет активности',
          tasks: [], // НОВОЕ: массив задач для Task Swimlanes
        };
      });

      // Заполняем данными + НОВАЯ логика Task Swimlanes
      apiData.hourly_data.forEach(item => {
        if (chartData[item.hour]) {
          chartData[item.hour].active = item.active_minutes;
          chartData[item.hour].project = item.project_minutes || 0;
          chartData[item.hour].tasks = item.tasks || []; // НОВОЕ: массив задач

          if (item.active_minutes > 0) {
            const projectPercent =
              item.project_minutes > 0
                ? Math.round((item.project_minutes / item.active_minutes) * 100)
                : 0;
            chartData[
              item.hour
            ].projectName = `Проектная: ${item.project_minutes} мин (${projectPercent}%)`;
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
        project: 0,
        total: 60,
        projectName: 'Нет активности',
        tasks: [], // НОВОЕ: массив задач для обратной совместимости
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
              chartData[currentTimeSlot].projectName = projectName;
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
            // В raw_output нет разделения на проект и фон, поэтому все считается проектом
            chartData[currentTimeSlot].project = Math.max(
              chartData[currentTimeSlot].project,
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
   * Показать/скрыть индикатор загрузки (Безопасная версия)
   */
  showLoading(show) {
    const container = this.container.querySelector('.timeline-chart-container');
    if (!container) return;

    // Ищем уже существующий оверлей
    const existingOverlay = container.querySelector('.loading-overlay');

    if (show) {
      // Если нужно показать, а оверлея нет - создаем
      if (!existingOverlay) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        // Добавляем стили прямо здесь, чтобы не зависеть от CSS файла
        overlay.style.cssText = `
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(255, 255, 255, 0.8);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          z-index: 10;
          border-radius: 8px;
          backdrop-filter: blur(2px);
        `;

        overlay.innerHTML = `
          <div class="loading-spinner" style="font-size: 2rem; color: #3b82f6; margin-bottom: 10px;">
            <i class="fas fa-spinner fa-spin"></i>
          </div>
          <div class="loading-text" style="color: #64748b; font-size: 0.9rem; font-weight: 500;">Загрузка данных...</div>
        `;

        container.appendChild(overlay);
      }
    } else {
      // Если нужно скрыть - удаляем оверлей
      if (existingOverlay) {
        existingOverlay.remove();
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

  /**
   * Создает полупрозрачную версию цвета
   * @param {string} color - Hex цвет (например, '#48bb78')
   * @param {number} alpha - Прозрачность (0.0 - 1.0)
   * @returns {string} RGBA цвет
   */
  createSemiTransparentColor(color, alpha = 0.3) {
    // Убираем # если есть
    const hex = color.replace('#', '');

    // Преобразуем в RGB
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);

    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  /**
   * Улучшает цвет для премиального вида
   * @param {string} color - Базовый цвет
   * @returns {string} Улучшенный цвет
   */
  enhanceColorForPremium(color) {
    // Преобразуем в более премиальные оттенки
    switch (color.toLowerCase()) {
      case '#48bb78': // Зеленый -> Emerald
        return '#10b981';
      case '#4299e1': // Синий -> Blue
        return '#3b82f6';
      case '#ed8936': // Оранжевый -> Amber
        return '#f59e0b';
      default:
        return color;
    }
  }

  /**
   * Создает CanvasPattern для штриховки (Hatch Pattern)
   * Chart.js не понимает CSS gradients, поэтому рисуем паттерн вручную
   */
  createHatchPattern(color) {
    // Создаем виртуальный canvas для паттерна
    const shape = document.createElement('canvas');
    shape.width = 10;
    shape.height = 10;
    const c = shape.getContext('2d');

    // Получаем RGB цвет
    const enhancedColor = this.enhanceColorForPremium(color);
    const hex = enhancedColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);

    // Рисуем фон (очень прозрачный)
    c.fillStyle = `rgba(${r}, ${g}, ${b}, 0.1)`;
    c.fillRect(0, 0, 10, 10);

    // Рисуем диагональную линию
    c.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.4)`; // Цвет штриха
    c.lineWidth = 1;
    c.beginPath();
    c.moveTo(0, 10);
    c.lineTo(10, 0);
    c.stroke();

    // Возвращаем паттерн, который понимает Chart.js
    // Важно: this.chart.ctx может быть еще не готов, поэтому берем контекст canvas
    const ctx = document.getElementById('timelineChartCanvas').getContext('2d');
    return ctx.createPattern(shape, 'repeat');
  }

  /**
   * Генерирует стабильный цвет из строки (F2)
   * Обеспечивает консистентность цветов для одних и тех же проектов
   * @param {string} str - Строка для генерации цвета (название проекта или ID)
   * @returns {string} Hex цвет
   */
  stringToColor(str) {
    if (!str) return '#6B7280'; // Серый по умолчанию

    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      // Простая хэш-функция
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }

    // Преобразуем в 24-битное число
    const color = (hash & 0x00ffffff).toString(16).toUpperCase();

    // Дополняем до 6 символов и добавляем префикс #
    return '#' + '00000'.substring(0, 6 - color.length) + color;
  }

  /**
   * Получает цвет для проекта с fallback на автогенерацию (F2)
   * @param {string} projectId - ID проекта
   * @param {string} projectTitle - Название проекта
   * @param {string} fallbackColor - Цвет из БД (опционально)
   * @returns {string} Hex цвет
   */
  getProjectColor(projectId, projectTitle, fallbackColor) {
    // Используем цвет из БД если доступен
    if (fallbackColor && fallbackColor !== '#4CAF50') {
      return fallbackColor;
    }

    // Fallback: автогенерация на основе ID или названия
    const source = projectId || projectTitle || 'default';
    return this.stringToColor(source);
  }
  /**
   * Получает эмодзи для задачи на основе названия (F4)
   * @param {string} taskTitle - Название задачи/проекта
   * @returns {string} Эмодзи символ
   */
  getTaskEmoji(taskTitle) {
    if (!taskTitle) return '🔸';

    const title = taskTitle.toLowerCase();

    // Простая логика назначения эмодзи
    if (title.includes('human') || title.includes('разработка')) return '👨‍💻';
    if (title.includes('встреча') || title.includes('meeting')) return '👥';
    if (title.includes('анализ') || title.includes('analysis')) return '📊';
    if (title.includes('тест') || title.includes('test')) return '🧪';
    if (title.includes('документ') || title.includes('doc')) return '📄';
    if (title.includes('дизайн') || title.includes('design')) return '🎨';
    if (title.includes('код') || title.includes('code')) return '💻';

    // По умолчанию цветной кружок
    return '🔸';
  }
}

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TimelineChart;
}
