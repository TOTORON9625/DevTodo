/**
 * UI Components for DevTodo
 */

// タスクカードを生成
function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = `task-card ${task.status === 'done' ? 'done' : ''}`;
    card.dataset.id = task.id;
    card.style.setProperty('--task-color', task.color || '#6750A4');

    const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'done';

    card.innerHTML = `
        <div class="task-checkbox">
            <input type="checkbox" ${task.status === 'done' ? 'checked' : ''} 
                   onclick="event.stopPropagation(); toggleTaskStatus(${task.id}, this.checked)">
        </div>
        <div class="task-content">
            <h3 class="task-title">${escapeHtml(task.title)}</h3>
            ${task.description ? `<p class="task-description">${escapeHtml(task.description)}</p>` : ''}
            <div class="task-meta">
                ${task.project_name ? `
                    <span class="task-project">
                        <span class="material-icons" style="font-size: 14px;">folder</span>
                        ${escapeHtml(task.project_name)}
                    </span>
                ` : ''}
                ${task.due_date ? `
                    <span class="task-due ${isOverdue ? 'overdue' : ''}">
                        <span class="material-icons" style="font-size: 14px;">event</span>
                        ${formatDate(task.due_date)}
                    </span>
                ` : ''}
                ${task.tags && task.tags.length > 0 ? `
                    <div class="task-tags">
                        ${task.tags.map(tag => `
                            <span class="task-tag" style="--tag-color: ${tag.color}20; color: ${tag.color}">
                                ${escapeHtml(tag.name)}
                            </span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
        <div class="task-actions">
            <button class="icon-btn icon-btn-sm" onclick="event.stopPropagation(); editTask(${task.id})" title="編集">
                <span class="material-icons">edit</span>
            </button>
            <button class="icon-btn icon-btn-sm" onclick="event.stopPropagation(); confirmDeleteTask(${task.id})" title="削除">
                <span class="material-icons">delete</span>
            </button>
        </div>
    `;

    card.onclick = () => editTask(task.id);

    return card;
}

// プロジェクト項目を生成
function createProjectItem(project) {
    const item = document.createElement('div');
    item.className = 'project-item';
    item.dataset.id = project.id;

    item.innerHTML = `
        <span class="project-color" style="background: ${project.color || '#6750A4'}"></span>
        <span class="project-name">${escapeHtml(project.name)}</span>
        <span class="project-count">${project.task_count || 0}</span>
        <div class="item-actions">
            <button class="icon-btn icon-btn-sm" onclick="event.stopPropagation(); editProject(${project.id})" title="編集">
                <span class="material-icons">edit</span>
            </button>
            <button class="icon-btn icon-btn-sm" onclick="event.stopPropagation(); confirmDeleteProject(${project.id})" title="削除">
                <span class="material-icons">delete</span>
            </button>
        </div>
    `;

    item.onclick = () => filterByProject(project.id);

    return item;
}

// タグ項目を生成
function createTagItem(tag) {
    const item = document.createElement('div');
    item.className = 'tag-item';
    item.dataset.id = tag.id;

    item.innerHTML = `
        <span class="tag-color" style="background: ${tag.color || '#6750A4'}"></span>
        <span>${escapeHtml(tag.name)}</span>
        <div class="item-actions">
            <button class="icon-btn icon-btn-sm" onclick="event.stopPropagation(); editTag(${tag.id})" title="編集">
                <span class="material-icons">edit</span>
            </button>
            <button class="icon-btn icon-btn-sm" onclick="event.stopPropagation(); confirmDeleteTag(${tag.id})" title="削除">
                <span class="material-icons">delete</span>
            </button>
        </div>
    `;

    item.onclick = () => filterByTag(tag.id);

    return item;
}

// アイデアカードを生成
function createIdeaCard(idea) {
    const card = document.createElement('div');
    card.className = 'idea-card';
    card.dataset.id = idea.id;
    card.style.setProperty('--idea-color', idea.color || '#6750A4');

    card.innerHTML = `
        <div class="idea-header">
            <h3 class="idea-title">${escapeHtml(idea.title)}</h3>
            ${idea.is_pinned ? '<span class="material-icons idea-pin">push_pin</span>' : ''}
        </div>
        ${idea.content ? `<p class="idea-content">${escapeHtml(idea.content)}</p>` : ''}
        <div class="idea-footer">
            <span class="idea-date">${formatDate(idea.updated_at || idea.created_at)}</span>
            <div class="idea-actions">
                <button class="icon-btn icon-btn-sm" onclick="event.stopPropagation(); convertIdeaToTask(${idea.id})" title="タスクに変換">
                    <span class="material-icons">task</span>
                </button>
                <button class="icon-btn icon-btn-sm" onclick="event.stopPropagation(); editIdea(${idea.id})" title="編集">
                    <span class="material-icons">edit</span>
                </button>
                <button class="icon-btn icon-btn-sm" onclick="event.stopPropagation(); confirmDeleteIdea(${idea.id})" title="削除">
                    <span class="material-icons">delete</span>
                </button>
            </div>
        </div>
    `;

    card.onclick = () => editIdea(idea.id);

    return card;
}

// タグチップを生成（フォーム用）
function createTagChip(tag, selected = false) {
    const chip = document.createElement('div');
    chip.className = `tag-chip ${selected ? 'selected' : ''}`;
    chip.dataset.id = tag.id;
    chip.style.setProperty('--chip-color', tag.color);

    chip.innerHTML = `
        <span class="tag-color" style="background: ${tag.color}; width: 8px; height: 8px;"></span>
        <span>${escapeHtml(tag.name)}</span>
    `;

    chip.onclick = () => {
        chip.classList.toggle('selected');
    };

    return chip;
}

// モーダルを開く
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

// モーダルを閉じる
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// スナックバーを表示
function showSnackbar(message, duration = 3000) {
    const snackbar = document.getElementById('snackbar');
    snackbar.textContent = message;
    snackbar.classList.add('active');

    setTimeout(() => {
        snackbar.classList.remove('active');
    }, duration);
}

// HTMLエスケープ
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 日付フォーマット
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((date - now) / (1000 * 60 * 60 * 24));

    if (diff === 0) return '今日';
    if (diff === 1) return '明日';
    if (diff === -1) return '昨日';

    return date.toLocaleDateString('ja-JP', {
        month: 'short',
        day: 'numeric'
    });
}

// カラーピッカーの初期化
function initColorPicker(pickerId, selectedColor = '#6750A4') {
    const picker = document.getElementById(pickerId);
    if (!picker) return;

    const options = picker.querySelectorAll('.color-option');
    options.forEach(option => {
        option.classList.remove('selected');
        if (option.dataset.color === selectedColor) {
            option.classList.add('selected');
        }

        option.onclick = (e) => {
            e.preventDefault();
            options.forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
        };
    });
}

// 選択された色を取得
function getSelectedColor(pickerId) {
    const picker = document.getElementById(pickerId);
    if (!picker) return '#6750A4';

    const selected = picker.querySelector('.color-option.selected');
    return selected ? selected.dataset.color : '#6750A4';
}

// 選択されたタグIDを取得
function getSelectedTagIds(selectorId) {
    const selector = document.getElementById(selectorId);
    if (!selector) return [];

    const selected = selector.querySelectorAll('.tag-chip.selected');
    return Array.from(selected).map(chip => parseInt(chip.dataset.id));
}
