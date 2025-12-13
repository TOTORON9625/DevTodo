/**
 * Reports Module for DevTodo
 */

let weeklyChart = null;
let monthlyChart = null;

// 週次レポートを読み込み
async function loadWeeklyReport() {
    try {
        const response = await fetch('/api/reports/weekly');
        const data = await response.json();

        renderWeeklyReport(data);
    } catch (error) {
        console.error('Error loading weekly report:', error);
        showSnackbar('レポートの読み込みに失敗しました');
    }
}

// 月次レポートを読み込み
async function loadMonthlyReport(year, month) {
    try {
        let url = '/api/reports/monthly';
        if (year && month) {
            url += `?year=${year}&month=${month}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        renderMonthlyReport(data);
    } catch (error) {
        console.error('Error loading monthly report:', error);
        showSnackbar('レポートの読み込みに失敗しました');
    }
}

// 週次レポートをレンダリング
function renderWeeklyReport(data) {
    const container = document.getElementById('reportContent');

    container.innerHTML = `
        <div class="report-header">
            <h3 class="report-period">
                ${data.period.start} 〜 ${data.period.end}
            </h3>
        </div>
        
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value">${data.completed_count}</div>
                <div class="stat-label">完了タスク</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.created_count}</div>
                <div class="stat-label">作成タスク</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.in_progress_count}</div>
                <div class="stat-label">進行中</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${calculateCompletionRate(data)}%</div>
                <div class="stat-label">完了率</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h4 class="chart-title">日別完了タスク数</h4>
            <div class="chart-wrapper">
                <canvas id="weeklyChart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <h4 class="chart-title">ステータス分布</h4>
            <div class="chart-wrapper">
                <canvas id="statusChart"></canvas>
            </div>
        </div>
        
        ${data.completed_tasks.length > 0 ? `
            <div class="chart-container">
                <h4 class="chart-title">完了済みタスク一覧</h4>
                <div class="completed-tasks-list">
                    ${data.completed_tasks.map(task => `
                        <div class="completed-task-item">
                            <span class="material-icons" style="color: var(--status-done); font-size: 18px;">check_circle</span>
                            <span>${escapeHtml(task.title)}</span>
                            <span class="completed-date">${formatDate(task.completed_at)}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;

    // 日別チャートを描画
    renderWeeklyDailyChart(data.daily_data);

    // ステータスチャートを描画
    renderStatusChart(data.status_counts);
}

// 月次レポートをレンダリング
function renderMonthlyReport(data) {
    const container = document.getElementById('reportContent');

    const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月',
        '7月', '8月', '9月', '10月', '11月', '12月'];

    container.innerHTML = `
        <div class="report-header">
            <h3 class="report-period">
                ${data.period.year}年 ${monthNames[data.period.month - 1]}
            </h3>
            <div class="month-nav">
                <button class="icon-btn" onclick="navigateMonth(-1)">
                    <span class="material-icons">chevron_left</span>
                </button>
                <button class="icon-btn" onclick="navigateMonth(1)">
                    <span class="material-icons">chevron_right</span>
                </button>
            </div>
        </div>
        
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value">${data.completed_count}</div>
                <div class="stat-label">完了タスク</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.created_count}</div>
                <div class="stat-label">作成タスク</div>
            </div>
        </div>
        
        ${data.project_stats.length > 0 ? `
            <div class="chart-container">
                <h4 class="chart-title">プロジェクト別完了数</h4>
                <div class="chart-wrapper">
                    <canvas id="projectChart"></canvas>
                </div>
            </div>
        ` : ''}
        
        ${data.tag_stats.length > 0 ? `
            <div class="chart-container">
                <h4 class="chart-title">タグ別完了数</h4>
                <div class="chart-wrapper">
                    <canvas id="tagChart"></canvas>
                </div>
            </div>
        ` : ''}
        
        ${data.color_stats.length > 0 ? `
            <div class="chart-container">
                <h4 class="chart-title">色別分布</h4>
                <div class="chart-wrapper">
                    <canvas id="colorChart"></canvas>
                </div>
            </div>
        ` : ''}
    `;

    // プロジェクトチャートを描画
    if (data.project_stats.length > 0) {
        renderProjectChart(data.project_stats);
    }

    // タグチャートを描画
    if (data.tag_stats.length > 0) {
        renderTagChart(data.tag_stats);
    }

    // 色チャートを描画
    if (data.color_stats.length > 0) {
        renderColorChart(data.color_stats);
    }
}

// 完了率を計算
function calculateCompletionRate(data) {
    const total = Object.values(data.status_counts).reduce((a, b) => a + b, 0);
    const done = data.status_counts.done || 0;
    return total > 0 ? Math.round((done / total) * 100) : 0;
}

// 週別日次チャートを描画
function renderWeeklyDailyChart(dailyData) {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;

    if (weeklyChart) {
        weeklyChart.destroy();
    }

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#E6E1E5' : '#1C1B1F';
    const gridColor = isDark ? '#49454F' : '#CAC4D0';

    weeklyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dailyData.map(d => d.day_name),
            datasets: [{
                label: '完了タスク',
                data: dailyData.map(d => d.count),
                backgroundColor: '#6750A4',
                borderRadius: 8,
                barThickness: 40
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: textColor
                    },
                    grid: {
                        color: gridColor
                    }
                },
                x: {
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// ステータスチャートを描画
function renderStatusChart(statusCounts) {
    const ctx = document.getElementById('statusChart');
    if (!ctx) return;

    const statusLabels = {
        'todo': 'Todo',
        'in_progress': '進行中',
        'done': '完了',
        'archived': 'アーカイブ'
    };

    const statusColors = {
        'todo': '#79747E',
        'in_progress': '#1976D2',
        'done': '#388E3C',
        'archived': '#9E9E9E'
    };

    const labels = Object.keys(statusCounts).map(k => statusLabels[k] || k);
    const data = Object.values(statusCounts);
    const colors = Object.keys(statusCounts).map(k => statusColors[k] || '#6750A4');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            },
            cutout: '60%'
        }
    });
}

// プロジェクトチャートを描画
function renderProjectChart(projectStats) {
    const ctx = document.getElementById('projectChart');
    if (!ctx) return;

    const filteredStats = projectStats.filter(p => p.completed_count > 0);

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#E6E1E5' : '#1C1B1F';

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: filteredStats.map(p => p.name),
            datasets: [{
                label: '完了タスク',
                data: filteredStats.map(p => p.completed_count),
                backgroundColor: filteredStats.map(p => p.color || '#6750A4'),
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: textColor
                    }
                },
                y: {
                    ticks: {
                        color: textColor
                    }
                }
            }
        }
    });
}

// タグチャートを描画
function renderTagChart(tagStats) {
    const ctx = document.getElementById('tagChart');
    if (!ctx) return;

    const filteredStats = tagStats.filter(t => t.completed_count > 0);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: filteredStats.map(t => t.name),
            datasets: [{
                data: filteredStats.map(t => t.completed_count),
                backgroundColor: filteredStats.map(t => t.color || '#6750A4'),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            },
            cutout: '60%'
        }
    });
}

// 色チャートを描画
function renderColorChart(colorStats) {
    const ctx = document.getElementById('colorChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: colorStats.map(c => '■'),
            datasets: [{
                data: colorStats.map(c => c.count),
                backgroundColor: colorStats.map(c => c.color),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            cutout: '60%'
        }
    });
}

// 現在の月報データ
let currentReportYear = new Date().getFullYear();
let currentReportMonth = new Date().getMonth() + 1;

// 月を移動
function navigateMonth(direction) {
    currentReportMonth += direction;

    if (currentReportMonth > 12) {
        currentReportMonth = 1;
        currentReportYear++;
    } else if (currentReportMonth < 1) {
        currentReportMonth = 12;
        currentReportYear--;
    }

    loadMonthlyReport(currentReportYear, currentReportMonth);
}
