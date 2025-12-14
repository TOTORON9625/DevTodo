/**
 * Supabase Client with Authentication
 */

const SUPABASE_URL = 'https://wssphvcahiujcvdobxgy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indzc3BodmNhaGl1amN2ZG9ieGd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MTQ1NTAsImV4cCI6MjA4MTI5MDU1MH0.G8QeL5BPm49fwwlsNgNVdttBOGYvYvEVJpxcTATHqwE';

// Supabase Client
const supabase = {
    url: SUPABASE_URL,
    key: SUPABASE_ANON_KEY,
    accessToken: null,
    currentUser: null,

    // ===================================
    // Authentication
    // ===================================

    init() {
        // Check for stored session
        const session = localStorage.getItem('supabase_session');
        if (session) {
            try {
                const parsed = JSON.parse(session);
                this.accessToken = parsed.access_token;
                this.currentUser = parsed.user;
            } catch (e) {
                localStorage.removeItem('supabase_session');
            }
        }
    },

    async signUp(email, password) {
        const response = await fetch(`${this.url}/auth/v1/signup`, {
            method: 'POST',
            headers: {
                'apikey': this.key,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error.message || 'サインアップに失敗しました');
        }

        // Check if email confirmation is required
        if (data.user && !data.session) {
            return { needsConfirmation: true, user: data.user };
        }

        if (data.session) {
            this.setSession(data.session, data.user);
        }

        return data;
    },

    async signIn(email, password) {
        const response = await fetch(`${this.url}/auth/v1/token?grant_type=password`, {
            method: 'POST',
            headers: {
                'apikey': this.key,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error_description || data.error.message || 'ログインに失敗しました');
        }

        this.setSession(data, data.user);
        return data;
    },

    async signOut() {
        if (this.accessToken) {
            try {
                await fetch(`${this.url}/auth/v1/logout`, {
                    method: 'POST',
                    headers: {
                        'apikey': this.key,
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                });
            } catch (e) {
                // Ignore errors
            }
        }

        this.accessToken = null;
        this.currentUser = null;
        localStorage.removeItem('supabase_session');
    },

    setSession(session, user) {
        this.accessToken = session.access_token;
        this.currentUser = user || session.user;
        localStorage.setItem('supabase_session', JSON.stringify({
            access_token: session.access_token,
            refresh_token: session.refresh_token,
            user: this.currentUser
        }));
    },

    isAuthenticated() {
        return !!this.accessToken && !!this.currentUser;
    },

    getUser() {
        return this.currentUser;
    },

    // ===================================
    // API Request with Auth
    // ===================================

    async request(table, method = 'GET', body = null, query = '') {
        if (!this.accessToken) {
            throw new Error('認証が必要です');
        }

        const url = `${this.url}/rest/v1/${table}${query}`;
        const options = {
            method,
            headers: {
                'apikey': this.key,
                'Authorization': `Bearer ${this.accessToken}`,
                'Content-Type': 'application/json',
                'Prefer': method === 'POST' ? 'return=representation' : 'return=representation'
            }
        };

        if (body && (method === 'POST' || method === 'PATCH')) {
            // Add user_id to new records
            if (method === 'POST' && this.currentUser) {
                body.user_id = this.currentUser.id;
            }
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);

        if (!response.ok) {
            const error = await response.text();
            console.error('Supabase error:', error);
            throw new Error(`Supabase error: ${error}`);
        }

        if (method === 'DELETE') {
            return { success: true };
        }

        return response.json();
    },

    // ===================================
    // Projects
    // ===================================
    async getProjects() {
        const projects = await this.request('projects', 'GET', null, '?order=created_at.desc');

        for (const project of projects) {
            const tasks = await this.request('tasks', 'GET', null, `?project_id=eq.${project.id}&select=id,status`);
            project.task_count = tasks.length;
            project.completed_count = tasks.filter(t => t.status === 'done').length;
        }

        return projects;
    },

    async getProject(id) {
        const result = await this.request('projects', 'GET', null, `?id=eq.${id}`);
        return result[0];
    },

    async createProject(data) {
        const result = await this.request('projects', 'POST', data);
        return result[0];
    },

    async updateProject(id, data) {
        const result = await this.request('projects', 'PATCH', data, `?id=eq.${id}`);
        return result[0];
    },

    async deleteProject(id) {
        return this.request('projects', 'DELETE', null, `?id=eq.${id}`);
    },

    // ===================================
    // Tags
    // ===================================
    async getTags() {
        const tags = await this.request('tags', 'GET', null, '?order=name.asc');

        for (const tag of tags) {
            const taskTags = await this.request('task_tags', 'GET', null, `?tag_id=eq.${tag.id}&select=task_id`);
            tag.usage_count = taskTags.length;
        }

        return tags;
    },

    async getTag(id) {
        const result = await this.request('tags', 'GET', null, `?id=eq.${id}`);
        return result[0];
    },

    async createTag(data) {
        const result = await this.request('tags', 'POST', data);
        return result[0];
    },

    async updateTag(id, data) {
        const result = await this.request('tags', 'PATCH', data, `?id=eq.${id}`);
        return result[0];
    },

    async deleteTag(id) {
        return this.request('tags', 'DELETE', null, `?id=eq.${id}`);
    },

    // ===================================
    // Tasks
    // ===================================
    async getTasks(filters = {}) {
        let query = '?order=priority.desc,created_at.desc';

        if (filters.status) {
            query += `&status=eq.${filters.status}`;
        }
        if (filters.project_id) {
            query += `&project_id=eq.${filters.project_id}`;
        }

        const tasks = await this.request('tasks', 'GET', null, query);

        for (const task of tasks) {
            if (task.project_id) {
                const project = await this.getProject(task.project_id);
                task.project_name = project ? project.name : null;
            }

            const taskTags = await this.request('task_tags', 'GET', null, `?task_id=eq.${task.id}&select=tag_id`);
            if (taskTags.length > 0) {
                const tagIds = taskTags.map(tt => tt.tag_id).join(',');
                task.tags = await this.request('tags', 'GET', null, `?id=in.(${tagIds})`);
            } else {
                task.tags = [];
            }
        }

        return tasks;
    },

    async getTask(id) {
        const result = await this.request('tasks', 'GET', null, `?id=eq.${id}`);
        const task = result[0];

        if (task) {
            const taskTags = await this.request('task_tags', 'GET', null, `?task_id=eq.${id}&select=tag_id`);
            if (taskTags.length > 0) {
                const tagIds = taskTags.map(tt => tt.tag_id).join(',');
                task.tags = await this.request('tags', 'GET', null, `?id=in.(${tagIds})`);
            } else {
                task.tags = [];
            }
        }

        return task;
    },

    async createTask(data) {
        const tagIds = data.tag_ids || [];
        delete data.tag_ids;

        const result = await this.request('tasks', 'POST', data);
        const task = result[0];

        for (const tagId of tagIds) {
            await this.request('task_tags', 'POST', { task_id: task.id, tag_id: tagId });
        }

        return task;
    },

    async updateTask(id, data) {
        const tagIds = data.tag_ids;
        delete data.tag_ids;

        if (data.status === 'done') {
            const currentTask = await this.getTask(id);
            if (currentTask && currentTask.status !== 'done') {
                data.completed_at = new Date().toISOString();
            }
        }

        const result = await this.request('tasks', 'PATCH', data, `?id=eq.${id}`);

        if (tagIds !== undefined) {
            await this.request('task_tags', 'DELETE', null, `?task_id=eq.${id}`);

            for (const tagId of tagIds) {
                await this.request('task_tags', 'POST', { task_id: id, tag_id: tagId });
            }
        }

        return result[0];
    },

    async deleteTask(id) {
        return this.request('tasks', 'DELETE', null, `?id=eq.${id}`);
    },

    // ===================================
    // Ideas
    // ===================================
    async getIdeas(search = '') {
        let query = '?order=is_pinned.desc,updated_at.desc';

        if (search) {
            query += `&or=(title.ilike.*${search}*,content.ilike.*${search}*)`;
        }

        return this.request('ideas', 'GET', null, query);
    },

    async getIdea(id) {
        const result = await this.request('ideas', 'GET', null, `?id=eq.${id}`);
        return result[0];
    },

    async createIdea(data) {
        const result = await this.request('ideas', 'POST', data);
        return result[0];
    },

    async updateIdea(id, data) {
        const result = await this.request('ideas', 'PATCH', data, `?id=eq.${id}`);
        return result[0];
    },

    async deleteIdea(id) {
        return this.request('ideas', 'DELETE', null, `?id=eq.${id}`);
    },

    async convertIdeaToTask(id) {
        const idea = await this.getIdea(id);
        if (!idea) throw new Error('Idea not found');

        const task = await this.createTask({
            title: idea.title,
            description: idea.content,
            color: idea.color,
            status: 'todo'
        });

        await this.deleteIdea(id);
        return task;
    },

    // ===================================
    // Reports
    // ===================================
    async getWeeklyReport() {
        const now = new Date();
        const weekStart = new Date(now);
        weekStart.setDate(now.getDate() - now.getDay() + 1);
        weekStart.setHours(0, 0, 0, 0);

        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekStart.getDate() + 6);
        weekEnd.setHours(23, 59, 59, 999);

        const weekStartStr = weekStart.toISOString().split('T')[0];
        const weekEndStr = weekEnd.toISOString().split('T')[0];

        const completedTasks = await this.request('tasks', 'GET', null,
            `?completed_at=gte.${weekStartStr}&completed_at=lte.${weekEndStr}T23:59:59&order=completed_at.desc`);

        const createdTasks = await this.request('tasks', 'GET', null,
            `?created_at=gte.${weekStartStr}&created_at=lte.${weekEndStr}T23:59:59`);

        const inProgressTasks = await this.request('tasks', 'GET', null, `?status=eq.in_progress`);

        const allTasks = await this.request('tasks', 'GET', null, '');
        const statusCounts = {};
        allTasks.forEach(t => {
            statusCounts[t.status] = (statusCounts[t.status] || 0) + 1;
        });

        const dailyData = [];
        const dayNames = ['月', '火', '水', '木', '金', '土', '日'];
        for (let i = 0; i < 7; i++) {
            const day = new Date(weekStart);
            day.setDate(weekStart.getDate() + i);
            const dayStr = day.toISOString().split('T')[0];

            const count = completedTasks.filter(t =>
                t.completed_at && t.completed_at.startsWith(dayStr)
            ).length;

            dailyData.push({
                date: dayStr,
                day_name: dayNames[i],
                count
            });
        }

        return {
            period: { start: weekStartStr, end: weekEndStr },
            completed_tasks: completedTasks,
            completed_count: completedTasks.length,
            created_count: createdTasks.length,
            in_progress_count: inProgressTasks.length,
            status_counts: statusCounts,
            daily_data: dailyData
        };
    },

    async getMonthlyReport(year, month) {
        year = year || new Date().getFullYear();
        month = month || new Date().getMonth() + 1;

        const monthStart = new Date(year, month - 1, 1);
        const monthEnd = new Date(year, month, 0);

        const monthStartStr = monthStart.toISOString().split('T')[0];
        const monthEndStr = monthEnd.toISOString().split('T')[0];

        const completedTasks = await this.request('tasks', 'GET', null,
            `?completed_at=gte.${monthStartStr}&completed_at=lte.${monthEndStr}T23:59:59`);

        const createdTasks = await this.request('tasks', 'GET', null,
            `?created_at=gte.${monthStartStr}&created_at=lte.${monthEndStr}T23:59:59`);

        const projects = await this.getProjects();
        const projectStats = projects.map(p => ({
            id: p.id,
            name: p.name,
            color: p.color,
            completed_count: completedTasks.filter(t => t.project_id === p.id).length
        }));

        const tags = await this.getTags();
        const tagStats = [];
        for (const tag of tags) {
            const taskTags = await this.request('task_tags', 'GET', null, `?tag_id=eq.${tag.id}&select=task_id`);
            const taskIds = taskTags.map(tt => tt.task_id);
            const completedCount = completedTasks.filter(t => taskIds.includes(t.id)).length;
            tagStats.push({
                id: tag.id,
                name: tag.name,
                color: tag.color,
                completed_count: completedCount
            });
        }

        const colorStats = {};
        completedTasks.forEach(t => {
            const color = t.color || '#6750A4';
            colorStats[color] = (colorStats[color] || 0) + 1;
        });

        return {
            period: { year, month, start: monthStartStr, end: monthEndStr },
            completed_count: completedTasks.length,
            created_count: createdTasks.length,
            project_stats: projectStats,
            tag_stats: tagStats,
            color_stats: Object.entries(colorStats).map(([color, count]) => ({ color, count }))
        };
    }
};

// Initialize on load
supabase.init();
