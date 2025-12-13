/**
 * Main Application Logic for DevTodo
 */

// API Base URL
const API_BASE = '/api';

// Current state
let currentView = 'tasks';
let currentFilter = {};
let allTasks = [];
let allProjects = [];
let allTags = [];
let allIdeas = [];

// ===================================
// Initialization
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initEventListeners();
    loadInitialData();
});

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#themeToggle .material-icons');
    if (icon) {
        icon.textContent = theme === 'dark' ? 'light_mode' : 'dark_mode';
    }
}

function initEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle').onclick = toggleTheme;

    // Menu toggle (mobile)
    document.getElementById('menuBtn').onclick = toggleSidebar;

    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.onclick = () => handleNavClick(item);
    });

    // Status tabs
    document.querySelectorAll('.status-tab').forEach(tab => {
        tab.onclick = () => handleStatusTabClick(tab);
    });

    // Report tabs
    document.querySelectorAll('.report-tab').forEach(tab => {
        tab.onclick = () => handleReportTabClick(tab);
    });

    // Add buttons
    document.getElementById('addTaskBtn').onclick = () => openTaskModal();
    document.getElementById('addProjectBtn').onclick = () => openProjectModal();
    document.getElementById('addTagBtn').onclick = () => openTagModal();
    document.getElementById('addIdeaBtn').onclick = () => openIdeaModal();

    // Form submissions
    document.getElementById('taskForm').onsubmit = handleTaskSubmit;
    document.getElementById('projectForm').onsubmit = handleProjectSubmit;
    document.getElementById('tagForm').onsubmit = handleTagSubmit;
    document.getElementById('ideaForm').onsubmit = handleIdeaSubmit;

    // Modal close buttons
    document.querySelectorAll('.modal-close, [data-modal]').forEach(btn => {
        btn.onclick = (e) => {
            const modalId = e.currentTarget.dataset.modal;
            if (modalId) closeModal(modalId);
        };
    });

    // Modal overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        };
    });

    // Idea search
    let searchTimeout;
    document.getElementById('ideaSearch').oninput = (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadIdeas(e.target.value);
        }, 300);
    };
}

async function loadInitialData() {
    await Promise.all([
        loadProjects(),
        loadTags(),
        loadTasks(),
        loadIdeas()
    ]);
}

// ===================================
// Theme
// ===================================

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon(next);
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// ===================================
// Navigation
// ===================================

function handleNavClick(item) {
    // Update active state
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    item.classList.add('active');

    const view = item.dataset.view;
    const filter = item.dataset.filter;

    switchView(view, filter);

    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
        toggleSidebar();
    }
}

function switchView(view, filter = '') {
    currentView = view;

    // Hide all views
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });

    // Show selected view
    document.getElementById(`${view}View`).style.display = 'block';

    // Update title
    const titles = {
        'tasks': filter === 'today' ? '今日' : filter === 'upcoming' ? '今後の予定' : 'すべてのタスク',
        'ideas': 'アイデアボックス',
        'reports': 'レポート'
    };
    document.getElementById('viewTitle').textContent = titles[view] || 'すべてのタスク';

    // Load view data
    if (view === 'tasks') {
        currentFilter = { filter };
        renderTasks();
    } else if (view === 'ideas') {
        renderIdeas();
    } else if (view === 'reports') {
        loadWeeklyReport();
    }
}

function handleStatusTabClick(tab) {
    document.querySelectorAll('.status-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    currentFilter.status = tab.dataset.status;
    renderTasks();
}

function handleReportTabClick(tab) {
    document.querySelectorAll('.report-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    const reportType = tab.dataset.report;
    if (reportType === 'weekly') {
        loadWeeklyReport();
    } else {
        loadMonthlyReport();
    }
}

function filterByProject(projectId) {
    document.querySelectorAll('.project-item').forEach(p => p.classList.remove('active'));
    document.querySelector(`.project-item[data-id="${projectId}"]`)?.classList.add('active');

    currentFilter = { project_id: projectId };
    switchView('tasks');
    renderTasks();
}

function filterByTag(tagId) {
    document.querySelectorAll('.tag-item').forEach(t => t.classList.remove('active'));
    document.querySelector(`.tag-item[data-id="${tagId}"]`)?.classList.add('active');

    currentFilter = { tag_id: tagId };
    switchView('tasks');
    renderTasks();
}

// ===================================
// Tasks CRUD
// ===================================

async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE}/tasks`);
        allTasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
        showSnackbar('タスクの読み込みに失敗しました');
    }
}

function renderTasks() {
    const container = document.getElementById('taskList');
    const emptyState = document.getElementById('emptyTasks');

    // Filter tasks
    let filtered = [...allTasks];

    if (currentFilter.status) {
        filtered = filtered.filter(t => t.status === currentFilter.status);
    }

    if (currentFilter.project_id) {
        filtered = filtered.filter(t => t.project_id == currentFilter.project_id);
    }

    if (currentFilter.tag_id) {
        filtered = filtered.filter(t =>
            t.tags && t.tags.some(tag => tag.id == currentFilter.tag_id)
        );
    }

    if (currentFilter.filter === 'today') {
        const today = new Date().toISOString().split('T')[0];
        filtered = filtered.filter(t => t.due_date === today);
    }

    if (currentFilter.filter === 'upcoming') {
        const today = new Date();
        filtered = filtered.filter(t => t.due_date && new Date(t.due_date) >= today);
        filtered.sort((a, b) => new Date(a.due_date) - new Date(b.due_date));
    }

    // Render
    container.innerHTML = '';

    if (filtered.length === 0) {
        emptyState.style.display = 'flex';
    } else {
        emptyState.style.display = 'none';
        filtered.forEach(task => {
            container.appendChild(createTaskCard(task));
        });
    }
}

async function toggleTaskStatus(taskId, checked) {
    const status = checked ? 'done' : 'todo';

    try {
        await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });

        await loadTasks();
        showSnackbar(checked ? 'タスクを完了しました' : 'タスクを未完了に戻しました');
    } catch (error) {
        console.error('Error updating task:', error);
        showSnackbar('更新に失敗しました');
    }
}

function openTaskModal(task = null) {
    const modal = document.getElementById('taskModal');
    const title = document.getElementById('taskModalTitle');
    const form = document.getElementById('taskForm');

    // Reset form
    form.reset();
    document.getElementById('taskId').value = '';
    initColorPicker('taskColorPicker', '#6750A4');

    // Populate project select
    const projectSelect = document.getElementById('taskProject');
    projectSelect.innerHTML = '<option value="">なし</option>';
    allProjects.forEach(p => {
        projectSelect.innerHTML += `<option value="${p.id}">${escapeHtml(p.name)}</option>`;
    });

    // Populate tag selector
    const tagSelector = document.getElementById('taskTagSelector');
    tagSelector.innerHTML = '';
    allTags.forEach(tag => {
        tagSelector.appendChild(createTagChip(tag, false));
    });

    if (task) {
        title.textContent = 'タスクを編集';
        document.getElementById('taskId').value = task.id;
        document.getElementById('taskTitle').value = task.title;
        document.getElementById('taskDescription').value = task.description || '';
        document.getElementById('taskProject').value = task.project_id || '';
        document.getElementById('taskDueDate').value = task.due_date || '';
        document.getElementById('taskStatus').value = task.status;
        initColorPicker('taskColorPicker', task.color || '#6750A4');

        // Select tags
        if (task.tags) {
            task.tags.forEach(tag => {
                const chip = tagSelector.querySelector(`[data-id="${tag.id}"]`);
                if (chip) chip.classList.add('selected');
            });
        }
    } else {
        title.textContent = 'タスクを追加';
    }

    openModal('taskModal');
}

async function editTask(taskId) {
    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`);
        const task = await response.json();
        openTaskModal(task);
    } catch (error) {
        console.error('Error loading task:', error);
        showSnackbar('タスクの読み込みに失敗しました');
    }
}

async function handleTaskSubmit(e) {
    e.preventDefault();

    const taskId = document.getElementById('taskId').value;
    const data = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        project_id: document.getElementById('taskProject').value || null,
        due_date: document.getElementById('taskDueDate').value || null,
        status: document.getElementById('taskStatus').value,
        color: getSelectedColor('taskColorPicker'),
        tag_ids: getSelectedTagIds('taskTagSelector')
    };

    try {
        if (taskId) {
            await fetch(`${API_BASE}/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showSnackbar('タスクを更新しました');
        } else {
            await fetch(`${API_BASE}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showSnackbar('タスクを作成しました');
        }

        closeModal('taskModal');
        await loadTasks();
        await loadProjects(); // Update project counts
    } catch (error) {
        console.error('Error saving task:', error);
        showSnackbar('保存に失敗しました');
    }
}

function confirmDeleteTask(taskId) {
    document.getElementById('confirmMessage').textContent = 'このタスクを削除しますか？';
    document.getElementById('confirmBtn').onclick = () => deleteTask(taskId);
    openModal('confirmModal');
}

async function deleteTask(taskId) {
    try {
        await fetch(`${API_BASE}/tasks/${taskId}`, { method: 'DELETE' });
        closeModal('confirmModal');
        await loadTasks();
        await loadProjects();
        showSnackbar('タスクを削除しました');
    } catch (error) {
        console.error('Error deleting task:', error);
        showSnackbar('削除に失敗しました');
    }
}

// ===================================
// Projects CRUD
// ===================================

async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE}/projects`);
        allProjects = await response.json();
        renderProjects();
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

function renderProjects() {
    const container = document.getElementById('projectList');
    container.innerHTML = '';

    allProjects.forEach(project => {
        container.appendChild(createProjectItem(project));
    });
}

function openProjectModal(project = null) {
    const modal = document.getElementById('projectModal');
    const title = document.getElementById('projectModalTitle');
    const form = document.getElementById('projectForm');

    form.reset();
    document.getElementById('projectId').value = '';
    initColorPicker('projectColorPicker', '#6750A4');

    if (project) {
        title.textContent = 'プロジェクトを編集';
        document.getElementById('projectId').value = project.id;
        document.getElementById('projectName').value = project.name;
        document.getElementById('projectDescription').value = project.description || '';
        initColorPicker('projectColorPicker', project.color || '#6750A4');
    } else {
        title.textContent = 'プロジェクトを追加';
    }

    openModal('projectModal');
}

async function handleProjectSubmit(e) {
    e.preventDefault();

    const projectId = document.getElementById('projectId').value;
    const data = {
        name: document.getElementById('projectName').value,
        description: document.getElementById('projectDescription').value,
        color: getSelectedColor('projectColorPicker')
    };

    try {
        if (projectId) {
            await fetch(`${API_BASE}/projects/${projectId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showSnackbar('プロジェクトを更新しました');
        } else {
            await fetch(`${API_BASE}/projects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showSnackbar('プロジェクトを作成しました');
        }

        closeModal('projectModal');
        await loadProjects();
    } catch (error) {
        console.error('Error saving project:', error);
        showSnackbar('保存に失敗しました');
    }
}

async function editProject(projectId) {
    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}`);
        const project = await response.json();
        openProjectModal(project);
    } catch (error) {
        console.error('Error loading project:', error);
        showSnackbar('プロジェクトの読み込みに失敗しました');
    }
}

function confirmDeleteProject(projectId) {
    document.getElementById('confirmMessage').textContent = 'このプロジェクトを削除しますか？関連するタスクのプロジェクト設定は解除されます。';
    document.getElementById('confirmBtn').onclick = () => deleteProject(projectId);
    openModal('confirmModal');
}

async function deleteProject(projectId) {
    try {
        await fetch(`${API_BASE}/projects/${projectId}`, { method: 'DELETE' });
        closeModal('confirmModal');
        await loadProjects();
        await loadTasks();
        showSnackbar('プロジェクトを削除しました');
    } catch (error) {
        console.error('Error deleting project:', error);
        showSnackbar('削除に失敗しました');
    }
}

// ===================================
// Tags CRUD
// ===================================

async function loadTags() {
    try {
        const response = await fetch(`${API_BASE}/tags`);
        allTags = await response.json();
        renderTags();
    } catch (error) {
        console.error('Error loading tags:', error);
    }
}

function renderTags() {
    const container = document.getElementById('tagList');
    container.innerHTML = '';

    allTags.forEach(tag => {
        container.appendChild(createTagItem(tag));
    });
}

function openTagModal(tag = null) {
    const modal = document.getElementById('tagModal');
    const title = document.getElementById('tagModalTitle');
    const form = document.getElementById('tagForm');

    form.reset();
    document.getElementById('tagId').value = '';
    initColorPicker('tagColorPicker', '#6750A4');

    if (tag) {
        title.textContent = 'タグを編集';
        document.getElementById('tagId').value = tag.id;
        document.getElementById('tagName').value = tag.name;
        initColorPicker('tagColorPicker', tag.color || '#6750A4');
    } else {
        title.textContent = 'タグを追加';
    }

    openModal('tagModal');
}

async function handleTagSubmit(e) {
    e.preventDefault();

    const tagId = document.getElementById('tagId').value;
    const data = {
        name: document.getElementById('tagName').value,
        color: getSelectedColor('tagColorPicker')
    };

    try {
        if (tagId) {
            await fetch(`${API_BASE}/tags/${tagId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showSnackbar('タグを更新しました');
        } else {
            await fetch(`${API_BASE}/tags`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showSnackbar('タグを作成しました');
        }

        closeModal('tagModal');
        await loadTags();
    } catch (error) {
        console.error('Error saving tag:', error);
        showSnackbar('保存に失敗しました');
    }
}

async function editTag(tagId) {
    try {
        const response = await fetch(`${API_BASE}/tags/${tagId}`);
        const tag = await response.json();
        openTagModal(tag);
    } catch (error) {
        console.error('Error loading tag:', error);
        showSnackbar('タグの読み込みに失敗しました');
    }
}

function confirmDeleteTag(tagId) {
    document.getElementById('confirmMessage').textContent = 'このタグを削除しますか？タスクからこのタグは削除されます。';
    document.getElementById('confirmBtn').onclick = () => deleteTag(tagId);
    openModal('confirmModal');
}

async function deleteTag(tagId) {
    try {
        await fetch(`${API_BASE}/tags/${tagId}`, { method: 'DELETE' });
        closeModal('confirmModal');
        await loadTags();
        await loadTasks();
        showSnackbar('タグを削除しました');
    } catch (error) {
        console.error('Error deleting tag:', error);
        showSnackbar('削除に失敗しました');
    }
}

// ===================================
// Ideas CRUD
// ===================================

async function loadIdeas(search = '') {
    try {
        let url = `${API_BASE}/ideas`;
        if (search) {
            url += `?search=${encodeURIComponent(search)}`;
        }

        const response = await fetch(url);
        allIdeas = await response.json();
        renderIdeas();
    } catch (error) {
        console.error('Error loading ideas:', error);
        showSnackbar('アイデアの読み込みに失敗しました');
    }
}

function renderIdeas() {
    const container = document.getElementById('ideaList');
    const emptyState = document.getElementById('emptyIdeas');

    container.innerHTML = '';

    if (allIdeas.length === 0) {
        emptyState.style.display = 'flex';
    } else {
        emptyState.style.display = 'none';
        allIdeas.forEach(idea => {
            container.appendChild(createIdeaCard(idea));
        });
    }
}

function openIdeaModal(idea = null) {
    const modal = document.getElementById('ideaModal');
    const title = document.getElementById('ideaModalTitle');
    const form = document.getElementById('ideaForm');

    form.reset();
    document.getElementById('ideaId').value = '';
    initColorPicker('ideaColorPicker', '#6750A4');

    if (idea) {
        title.textContent = 'アイデアを編集';
        document.getElementById('ideaId').value = idea.id;
        document.getElementById('ideaTitle').value = idea.title;
        document.getElementById('ideaContent').value = idea.content || '';
        initColorPicker('ideaColorPicker', idea.color || '#6750A4');
    } else {
        title.textContent = 'アイデアを追加';
    }

    openModal('ideaModal');
}

async function editIdea(ideaId) {
    try {
        const response = await fetch(`${API_BASE}/ideas/${ideaId}`);
        const idea = await response.json();
        openIdeaModal(idea);
    } catch (error) {
        console.error('Error loading idea:', error);
        showSnackbar('アイデアの読み込みに失敗しました');
    }
}

async function handleIdeaSubmit(e) {
    e.preventDefault();

    const ideaId = document.getElementById('ideaId').value;
    const data = {
        title: document.getElementById('ideaTitle').value,
        content: document.getElementById('ideaContent').value,
        color: getSelectedColor('ideaColorPicker')
    };

    try {
        if (ideaId) {
            await fetch(`${API_BASE}/ideas/${ideaId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showSnackbar('アイデアを更新しました');
        } else {
            await fetch(`${API_BASE}/ideas`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showSnackbar('アイデアを作成しました');
        }

        closeModal('ideaModal');
        await loadIdeas();
    } catch (error) {
        console.error('Error saving idea:', error);
        showSnackbar('保存に失敗しました');
    }
}

function confirmDeleteIdea(ideaId) {
    document.getElementById('confirmMessage').textContent = 'このアイデアを削除しますか？';
    document.getElementById('confirmBtn').onclick = () => deleteIdea(ideaId);
    openModal('confirmModal');
}

async function deleteIdea(ideaId) {
    try {
        await fetch(`${API_BASE}/ideas/${ideaId}`, { method: 'DELETE' });
        closeModal('confirmModal');
        await loadIdeas();
        showSnackbar('アイデアを削除しました');
    } catch (error) {
        console.error('Error deleting idea:', error);
        showSnackbar('削除に失敗しました');
    }
}

async function convertIdeaToTask(ideaId) {
    try {
        await fetch(`${API_BASE}/ideas/${ideaId}/convert`, { method: 'POST' });
        await loadIdeas();
        await loadTasks();
        showSnackbar('アイデアをタスクに変換しました');
    } catch (error) {
        console.error('Error converting idea:', error);
        showSnackbar('変換に失敗しました');
    }
}
