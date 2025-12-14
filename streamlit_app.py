"""
DevTodo - Streamlit Application
個人開発者のためのタスク管理アプリ
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ===================================
# Supabase Configuration
# ===================================
SUPABASE_URL = "https://wssphvcahiujcvdobxgy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indzc3BodmNhaGl1amN2ZG9ieGd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MTQ1NTAsImV4cCI6MjA4MTI5MDU1MH0.G8QeL5BPm49fwwlsNgNVdttBOGYvYvEVJpxcTATHqwE"

# ===================================
# Page Config
# ===================================
st.set_page_config(
    page_title="DevTodo",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================================
# Custom CSS - Material Design 3 Style
# ===================================
st.markdown("""
<style>
    /* ===================================
       Material Design 3 Color System
       =================================== */
    :root {
        --md-primary: #6750A4;
        --md-secondary: #625B71;
        --md-tertiary: #7D5260;
        --md-surface: #FFFBFE;
        --md-surface-variant: #E7E0EC;
        --md-on-surface: #1C1B1F;
        --md-on-surface-variant: #49454F;
        --md-outline: #79747E;
        --md-error: #B3261E;
        --md-success: #388E3C;
        --status-todo: #79747E;
        --status-progress: #1976D2;
        --status-done: #388E3C;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 28px;
    }
    
    /* ===================================
       Global Styles
       =================================== */
    .main {
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e0f0 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #6750A4 0%, #7B1FA2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.1);
        border-radius: var(--radius-md);
        padding: 12px 16px;
        margin: 4px 0;
        transition: all 0.2s ease;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.2);
    }
    
    /* ===================================
       Cards & Containers
       =================================== */
    .task-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border-left: 4px solid var(--md-primary);
    }
    
    .task-card:hover {
        box-shadow: 0 4px 20px rgba(103, 80, 164, 0.15);
        transform: translateY(-2px);
    }
    
    .project-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .project-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    .idea-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .idea-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    /* ===================================
       Buttons
       =================================== */
    .stButton > button {
        background: var(--md-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-xl) !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: #5a4494 !important;
        box-shadow: 0 4px 12px rgba(103, 80, 164, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* ===================================
       Form Elements
       =================================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: var(--radius-md) !important;
        border-color: var(--md-outline) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--md-primary) !important;
        box-shadow: 0 0 0 2px rgba(103, 80, 164, 0.2) !important;
    }
    
    /* ===================================
       Expander
       =================================== */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--md-primary), #7B1FA2) !important;
        color: white !important;
        border-radius: var(--radius-lg) !important;
        padding: 16px !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        border-radius: 0 0 var(--radius-lg) var(--radius-lg) !important;
        padding: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }
    
    /* ===================================
       Metrics
       =================================== */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, var(--md-primary), #7B1FA2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="metric-container"] {
        background: white;
        border-radius: var(--radius-lg);
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* ===================================
       Tabs
       =================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--md-surface-variant);
        border-radius: var(--radius-lg);
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md);
        padding: 12px 24px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--md-primary) !important;
        color: white !important;
    }
    
    /* ===================================
       Hide Default Elements
       =================================== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ===================================
       Status Colors
       =================================== */
    .status-todo { border-left-color: var(--status-todo) !important; }
    .status-in_progress { border-left-color: var(--status-progress) !important; }
    .status-done { border-left-color: var(--status-done) !important; }
    
    /* ===================================
       Animations
       =================================== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stMarkdown, .element-container {
        animation: fadeIn 0.3s ease;
    }
    
    /* ===================================
       Login Page
       =================================== */
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 40px;
        background: white;
        border-radius: var(--radius-xl);
        box-shadow: 0 8px 32px rgba(103, 80, 164, 0.15);
    }
    
    .auth-logo {
        text-align: center;
        margin-bottom: 24px;
    }
    
    .auth-logo h1 {
        background: linear-gradient(135deg, var(--md-primary), #7B1FA2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ===================================
# Session State Initialization
# ===================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'supabase' not in st.session_state:
    st.session_state.supabase = None
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

# ===================================
# Supabase Client
# ===================================
def get_supabase() -> Client:
    if st.session_state.supabase is None:
        st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return st.session_state.supabase

# ===================================
# Authentication Functions
# ===================================
def login(email: str, password: str) -> bool:
    try:
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.user = response.user
        st.session_state.access_token = response.session.access_token
        st.session_state.authenticated = True
        return True
    except Exception as e:
        st.error(f"ログインエラー: {str(e)}")
        return False

def signup(email: str, password: str) -> bool:
    try:
        supabase = get_supabase()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            st.success("アカウントが作成されました！確認メールをご確認ください。")
            return True
        return False
    except Exception as e:
        st.error(f"サインアップエラー: {str(e)}")
        return False

def logout():
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
    except:
        pass
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.access_token = None

# ===================================
# Database Functions
# ===================================
def get_user_id():
    if st.session_state.user:
        return st.session_state.user.id
    return None

# Projects
def get_projects():
    supabase = get_supabase()
    response = supabase.table('projects').select('*').order('created_at', desc=True).execute()
    return response.data

def create_project(name: str, description: str, color: str):
    supabase = get_supabase()
    supabase.table('projects').insert({
        'name': name,
        'description': description,
        'color': color,
        'user_id': get_user_id()
    }).execute()

def delete_project(project_id: int):
    supabase = get_supabase()
    supabase.table('projects').delete().eq('id', project_id).execute()

# Tags
def get_tags():
    supabase = get_supabase()
    response = supabase.table('tags').select('*').order('name').execute()
    return response.data

def create_tag(name: str, color: str):
    supabase = get_supabase()
    supabase.table('tags').insert({
        'name': name,
        'color': color,
        'user_id': get_user_id()
    }).execute()

def delete_tag(tag_id: int):
    supabase = get_supabase()
    supabase.table('tags').delete().eq('id', tag_id).execute()

# Tasks
def get_tasks(status_filter=None, project_filter=None):
    supabase = get_supabase()
    query = supabase.table('tasks').select('*, projects(name, color)')
    
    if status_filter:
        query = query.eq('status', status_filter)
    if project_filter:
        query = query.eq('project_id', project_filter)
    
    response = query.order('created_at', desc=True).execute()
    return response.data

def create_task(title: str, description: str, project_id: int, due_date, color: str, status: str):
    supabase = get_supabase()
    data = {
        'title': title,
        'description': description,
        'color': color,
        'status': status,
        'user_id': get_user_id()
    }
    if project_id:
        data['project_id'] = project_id
    if due_date:
        data['due_date'] = str(due_date)
    
    supabase.table('tasks').insert(data).execute()

def update_task_status(task_id: int, status: str):
    supabase = get_supabase()
    data = {'status': status}
    if status == 'done':
        data['completed_at'] = datetime.now().isoformat()
    supabase.table('tasks').update(data).eq('id', task_id).execute()

def delete_task(task_id: int):
    supabase = get_supabase()
    supabase.table('tasks').delete().eq('id', task_id).execute()

# Ideas
def get_ideas(search: str = ""):
    supabase = get_supabase()
    query = supabase.table('ideas').select('*')
    if search:
        query = query.or_(f"title.ilike.%{search}%,content.ilike.%{search}%")
    response = query.order('updated_at', desc=True).execute()
    return response.data

def create_idea(title: str, content: str, color: str):
    supabase = get_supabase()
    supabase.table('ideas').insert({
        'title': title,
        'content': content,
        'color': color,
        'user_id': get_user_id()
    }).execute()

def delete_idea(idea_id: int):
    supabase = get_supabase()
    supabase.table('ideas').delete().eq('id', idea_id).execute()

def convert_idea_to_task(idea_id: int):
    supabase = get_supabase()
    idea = supabase.table('ideas').select('*').eq('id', idea_id).single().execute()
    if idea.data:
        create_task(
            title=idea.data['title'],
            description=idea.data['content'],
            project_id=None,
            due_date=None,
            color=idea.data['color'] or '#6750A4',
            status='todo'
        )
        delete_idea(idea_id)

# ===================================
# Color Palette
# ===================================
COLORS = {
    'Purple': '#6750A4',
    'Red': '#D32F2F',
    'Orange': '#F57C00',
    'Yellow': '#FBC02D',
    'Green': '#388E3C',
    'Blue': '#1976D2',
    'Violet': '#7B1FA2',
    'Gray': '#455A64'
}

STATUS_OPTIONS = {
    'todo': 'Todo',
    'in_progress': '進行中',
    'done': '完了',
    'archived': 'アーカイブ'
}

# ===================================
# UI Components
# ===================================
def show_login_page():
    st.markdown("## 🚀 DevTodo")
    st.markdown("#### 個人開発者のためのタスク管理アプリ")
    
    tab1, tab2 = st.tabs(["ログイン", "新規登録"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("メールアドレス", placeholder="email@example.com")
            password = st.text_input("パスワード", type="password")
            submitted = st.form_submit_button("ログイン", use_container_width=True)
            
            if submitted and email and password:
                if login(email, password):
                    st.rerun()
    
    with tab2:
        with st.form("signup_form"):
            email = st.text_input("メールアドレス", placeholder="email@example.com", key="signup_email")
            password = st.text_input("パスワード（6文字以上）", type="password", key="signup_pass")
            password_confirm = st.text_input("パスワード（確認）", type="password", key="signup_confirm")
            submitted = st.form_submit_button("アカウント作成", use_container_width=True)
            
            if submitted:
                if password != password_confirm:
                    st.error("パスワードが一致しません")
                elif len(password) < 6:
                    st.error("パスワードは6文字以上にしてください")
                elif email and password:
                    signup(email, password)

def show_task_card(task):
    status_class = f"status-{task['status']}"
    color = task.get('color', '#6750A4')
    
    with st.container():
        col1, col2, col3 = st.columns([0.5, 8, 1.5])
        
        with col1:
            done = task['status'] == 'done'
            if st.checkbox("", value=done, key=f"task_check_{task['id']}", label_visibility="collapsed"):
                if not done:
                    update_task_status(task['id'], 'done')
                    st.rerun()
            else:
                if done:
                    update_task_status(task['id'], 'todo')
                    st.rerun()
        
        with col2:
            title_style = "text-decoration: line-through; opacity: 0.6;" if done else ""
            st.markdown(f"""
                <div style="border-left: 4px solid {color}; padding-left: 12px;">
                    <strong style="{title_style}">{task['title']}</strong>
                    <br><small style="color: gray;">{task.get('description', '')[:50] if task.get('description') else ''}</small>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("🗑️", key=f"del_task_{task['id']}"):
                delete_task(task['id'])
                st.rerun()

def show_tasks_page():
    st.markdown("## 📋 タスク")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        status_filter = st.selectbox(
            "ステータス",
            options=["すべて"] + list(STATUS_OPTIONS.values()),
            key="task_status_filter"
        )
    with col2:
        projects = get_projects()
        project_options = {"すべて": None}
        project_options.update({p['name']: p['id'] for p in projects})
        selected_project = st.selectbox("プロジェクト", options=list(project_options.keys()))
    
    # Add Task
    with st.expander("➕ タスクを追加", expanded=False):
        with st.form("add_task"):
            title = st.text_input("タイトル*")
            description = st.text_area("説明", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                project_id = st.selectbox(
                    "プロジェクト",
                    options=[None] + [p['id'] for p in projects],
                    format_func=lambda x: "なし" if x is None else next((p['name'] for p in projects if p['id'] == x), "")
                )
            with col2:
                due_date = st.date_input("期限", value=None)
            
            col1, col2 = st.columns(2)
            with col1:
                color = st.selectbox("色", options=list(COLORS.keys()))
            with col2:
                status = st.selectbox("ステータス", options=list(STATUS_OPTIONS.keys()), format_func=lambda x: STATUS_OPTIONS[x])
            
            if st.form_submit_button("追加", use_container_width=True):
                if title:
                    create_task(title, description, project_id, due_date, COLORS[color], status)
                    st.success("タスクを追加しました！")
                    st.rerun()
    
    # Get tasks
    status_key = None
    if status_filter != "すべて":
        status_key = next((k for k, v in STATUS_OPTIONS.items() if v == status_filter), None)
    
    tasks = get_tasks(
        status_filter=status_key,
        project_filter=project_options.get(selected_project)
    )
    
    if tasks:
        for task in tasks:
            show_task_card(task)
    else:
        st.info("タスクがありません。「タスクを追加」から始めましょう！")

def show_projects_page():
    st.markdown("## 📁 プロジェクト")
    
    # Add Project
    with st.expander("➕ プロジェクトを追加"):
        with st.form("add_project"):
            name = st.text_input("プロジェクト名*")
            description = st.text_area("説明", height=80)
            color = st.selectbox("色", options=list(COLORS.keys()))
            
            if st.form_submit_button("追加", use_container_width=True):
                if name:
                    create_project(name, description, COLORS[color])
                    st.success("プロジェクトを追加しました！")
                    st.rerun()
    
    # List Projects
    projects = get_projects()
    if projects:
        for project in projects:
            col1, col2 = st.columns([9, 1])
            with col1:
                color = project.get('color', '#6750A4')
                st.markdown(f"""
                    <div style="border-left: 4px solid {color}; padding: 8px 12px; margin-bottom: 8px; background: #f5f5f5; border-radius: 8px;">
                        <strong>{project['name']}</strong>
                        <br><small style="color: gray;">{project.get('description', '') or ''}</small>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"del_proj_{project['id']}"):
                    delete_project(project['id'])
                    st.rerun()
    else:
        st.info("プロジェクトがありません")

def show_tags_page():
    st.markdown("## 🏷️ タグ")
    
    # Add Tag
    with st.expander("➕ タグを追加"):
        with st.form("add_tag"):
            name = st.text_input("タグ名*")
            color = st.selectbox("色", options=list(COLORS.keys()))
            
            if st.form_submit_button("追加", use_container_width=True):
                if name:
                    create_tag(name, COLORS[color])
                    st.success("タグを追加しました！")
                    st.rerun()
    
    # List Tags
    tags = get_tags()
    if tags:
        cols = st.columns(4)
        for i, tag in enumerate(tags):
            with cols[i % 4]:
                color = tag.get('color', '#6750A4')
                st.markdown(f"""
                    <div style="background: {color}20; border-left: 4px solid {color}; padding: 8px; border-radius: 8px; margin-bottom: 8px;">
                        {tag['name']}
                    </div>
                """, unsafe_allow_html=True)
                if st.button("削除", key=f"del_tag_{tag['id']}"):
                    delete_tag(tag['id'])
                    st.rerun()
    else:
        st.info("タグがありません")

def show_ideas_page():
    st.markdown("## 💡 アイデアボックス")
    
    # Search
    search = st.text_input("🔍 検索", placeholder="アイデアを検索...")
    
    # Add Idea
    with st.expander("➕ アイデアを追加"):
        with st.form("add_idea"):
            title = st.text_input("タイトル*")
            content = st.text_area("内容", height=150)
            color = st.selectbox("色", options=list(COLORS.keys()))
            
            if st.form_submit_button("追加", use_container_width=True):
                if title:
                    create_idea(title, content, COLORS[color])
                    st.success("アイデアを追加しました！")
                    st.rerun()
    
    # List Ideas
    ideas = get_ideas(search)
    if ideas:
        cols = st.columns(2)
        for i, idea in enumerate(ideas):
            with cols[i % 2]:
                color = idea.get('color', '#6750A4')
                with st.container():
                    st.markdown(f"""
                        <div style="border-left: 4px solid {color}; padding: 12px; background: #f9f9f9; border-radius: 8px; margin-bottom: 12px;">
                            <strong>{idea['title']}</strong>
                            <p style="color: gray; font-size: 0.9em;">{(idea.get('content', '') or '')[:100]}...</p>
                        </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 タスク化", key=f"convert_{idea['id']}"):
                            convert_idea_to_task(idea['id'])
                            st.success("タスクに変換しました！")
                            st.rerun()
                    with col2:
                        if st.button("🗑️ 削除", key=f"del_idea_{idea['id']}"):
                            delete_idea(idea['id'])
                            st.rerun()
    else:
        st.info("アイデアがありません")

def show_reports_page():
    st.markdown("## 📊 レポート")
    
    tasks = get_tasks()
    
    if not tasks:
        st.info("タスクがないためレポートを表示できません")
        return
    
    # Summary
    total = len(tasks)
    done = len([t for t in tasks if t['status'] == 'done'])
    in_progress = len([t for t in tasks if t['status'] == 'in_progress'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("総タスク", total)
    col2.metric("完了", done)
    col3.metric("進行中", in_progress)
    col4.metric("完了率", f"{(done/total*100):.0f}%" if total > 0 else "0%")
    
    # Status Chart
    st.markdown("### ステータス分布")
    status_counts = {}
    for task in tasks:
        status = STATUS_OPTIONS.get(task['status'], task['status'])
        status_counts[status] = status_counts.get(status, 0) + 1
    
    fig = px.pie(
        values=list(status_counts.values()),
        names=list(status_counts.keys()),
        color_discrete_sequence=['#79747E', '#1976D2', '#388E3C', '#9E9E9E']
    )
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent Completed
    st.markdown("### 最近完了したタスク")
    completed = [t for t in tasks if t['status'] == 'done'][:5]
    if completed:
        for task in completed:
            st.markdown(f"✅ {task['title']}")
    else:
        st.info("完了したタスクはありません")

# ===================================
# Main App
# ===================================
def main():
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user.email}")
        if st.button("ログアウト", use_container_width=True):
            logout()
            st.rerun()
        
        st.divider()
        
        page = st.radio(
            "メニュー",
            options=["📋 タスク", "📁 プロジェクト", "🏷️ タグ", "💡 アイデア", "📊 レポート"],
            label_visibility="collapsed"
        )
    
    # Main Content
    if page == "📋 タスク":
        show_tasks_page()
    elif page == "📁 プロジェクト":
        show_projects_page()
    elif page == "🏷️ タグ":
        show_tags_page()
    elif page == "💡 アイデア":
        show_ideas_page()
    elif page == "📊 レポート":
        show_reports_page()

if __name__ == "__main__":
    main()
