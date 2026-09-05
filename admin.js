/**
 * IT ADMIN CONTROL PORTAL - JAVASCRIPT CONTROLLER
 * Full CRUD, JWT Session Auth, and Real-Time Telemetry Sync
 */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  const API_BASE = '';
  let authToken = localStorage.getItem('admin_jwt_token') || '';
  let projectsCache = [];
  let skillsCache = [];
  let inquiriesCache = [];
  let attendanceCache = [];

  // DOM Elements
  const loginOverlay = document.getElementById('login-overlay');
  const adminApp = document.getElementById('admin-app');
  const loginForm = document.getElementById('admin-login-form');
  const logoutBtn = document.getElementById('logout-btn');
  const refreshDataBtn = document.getElementById('refresh-data-btn');
  const navItems = document.querySelectorAll('.nav-item');
  const tabPanes = document.querySelectorAll('.admin-tab-pane');
  const pageHeading = document.getElementById('page-heading');
  const pageSubheading = document.getElementById('page-subheading');

  // Modals
  const projectModal = document.getElementById('project-modal');
  const projectForm = document.getElementById('project-form');
  const skillModal = document.getElementById('skill-modal');
  const skillForm = document.getElementById('skill-form');

  // =========================================================================
  // 1. TOAST NOTIFICATIONS
  // =========================================================================
  window.showToast = function(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  };

  // =========================================================================
  // 2. AUTHENTICATION & API REQUEST WRAPPER
  // =========================================================================
  async function apiRequest(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(authToken ? { 'Authorization': `Bearer ${authToken}` } : {})
    };

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: { ...headers, ...(options.headers || {}) }
      });

      if (res.status === 401) {
        // Unauthorized
        handleLogout('Session expired. Please log in again.');
        return null;
      }

      return await res.json();
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      showToast(`Network error: ${err.message}`, 'error');
      return null;
    }
  }

  // Handle Login
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('login-username').value.trim();
      const password = document.getElementById('login-password').value.trim();
      const loginBtn = document.getElementById('login-btn');

      if (loginBtn) {
        loginBtn.disabled = true;
        loginBtn.innerText = 'Authenticating...';
      }

      const res = await apiRequest('/api/admin/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      });

      if (loginBtn) {
        loginBtn.disabled = false;
        loginBtn.innerText = 'Authenticate Session';
      }

      if (res && res.success && res.token) {
        authToken = res.token;
        localStorage.setItem('admin_jwt_token', authToken);
        showToast('Login successful! Welcome Admin.', 'success');
        showDashboard();
      } else {
        showToast(res ? res.message : 'Invalid credentials', 'error');
      }
    });
  }

  function handleLogout(msg = 'Logged out successfully.') {
    authToken = '';
    localStorage.removeItem('admin_jwt_token');
    loginOverlay.style.display = 'flex';
    adminApp.style.display = 'none';
    if (msg) showToast(msg, 'info');
  }

  if (logoutBtn) logoutBtn.addEventListener('click', () => handleLogout());

  // Check initial session
  async function checkSession() {
    if (!authToken) {
      loginOverlay.style.display = 'flex';
      adminApp.style.display = 'none';
      return;
    }

    const res = await apiRequest('/api/admin/verify');
    if (res && res.authenticated) {
      showDashboard();
    } else {
      handleLogout();
    }
  }

  function showDashboard() {
    loginOverlay.style.display = 'none';
    adminApp.style.display = 'flex';
    loadAllData();
  }

  // =========================================================================
  // 3. TAB NAVIGATION
  // =========================================================================
  const TAB_HEADINGS = {
    overview: { title: 'Dashboard Overview', desc: 'System metrics, service status, and live operational stats.' },
    projects: { title: 'Projects Manager', desc: 'Add, update, reorder, and configure case studies and tech stacks.' },
    skills: { title: 'Skills & Tech Stack', desc: 'Manage categorized technical proficiencies and tooling.' },
    inquiries: { title: 'Recruiter Inquiries', desc: 'Manage contact form leads, change statuses, and export.' },
    attendance: { title: 'Biometric Attendance Logs', desc: 'Audit facial recognition records and timestamped events.' },
    settings: { title: 'Profile & Security Settings', desc: 'Update candidate headline, contact details, and admin password.' }
  };

  window.switchTab = function(tabName) {
    navItems.forEach(item => {
      if (item.getAttribute('data-tab') === tabName) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    tabPanes.forEach(pane => {
      if (pane.id === `tab-${tabName}`) {
        pane.classList.add('active');
      } else {
        pane.classList.remove('active');
      }
    });

    if (TAB_HEADINGS[tabName]) {
      pageHeading.textContent = TAB_HEADINGS[tabName].title;
      pageSubheading.textContent = TAB_HEADINGS[tabName].desc;
    }
  };

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const tab = item.getAttribute('data-tab');
      window.switchTab(tab);
    });
  });

  // =========================================================================
  // 4. DATA LOADERS & SYNC
  // =========================================================================
  async function loadAllData() {
    await Promise.all([
      loadStats(),
      loadProjects(),
      loadSkills(),
      loadInquiries(),
      loadAttendance(),
      loadProfileConfig()
    ]);
  }

  if (refreshDataBtn) {
    refreshDataBtn.addEventListener('click', async () => {
      refreshDataBtn.classList.add('rotating');
      await loadAllData();
      refreshDataBtn.classList.remove('rotating');
      showToast('Dashboard data synchronized.', 'success');
    });
  }

  // A. Load Dashboard Stats
  async function loadStats() {
    const data = await apiRequest('/api/admin/stats');
    if (!data || !data.success) return;

    const m = data.metrics;
    document.getElementById('stat-projects').textContent = m.total_projects;
    document.getElementById('stat-skills').textContent = m.total_skills;
    document.getElementById('stat-inquiries').textContent = m.total_inquiries;
    document.getElementById('stat-attendance').textContent = m.total_attendance_logs;

    document.getElementById('badge-projects-count').textContent = m.total_projects;
    document.getElementById('badge-inquiries-count').textContent = m.new_inquiries;

    // Overview Inquiries Preview
    const inqContainer = document.getElementById('overview-inquiries-list');
    if (data.recent_messages && data.recent_messages.length > 0) {
      inqContainer.innerHTML = data.recent_messages.map(msg => `
        <div class="activity-item">
          <div class="activity-meta">
            <h4>${escapeHtml(msg.name)} <span class="status-badge ${msg.status}">${msg.status}</span></h4>
            <p>${escapeHtml(msg.email)} &bull; ${escapeHtml(msg.subject)}</p>
          </div>
          <span class="activity-time">${msg.created_at.split(' ')[0]}</span>
        </div>
      `).join('');
    } else {
      inqContainer.innerHTML = '<p class="empty-state">No inquiries received yet.</p>';
    }

    // Overview Attendance Preview
    const attContainer = document.getElementById('overview-attendance-list');
    if (data.recent_attendance && data.recent_attendance.length > 0) {
      attContainer.innerHTML = data.recent_attendance.map(att => `
        <div class="activity-item">
          <div class="activity-meta">
            <h4>${escapeHtml(att.student_name)} (${escapeHtml(att.student_id)})</h4>
            <p>Confidence: ${Math.round(att.confidence_score * 100)}% &bull; Device: ${escapeHtml(att.device_id)}</p>
          </div>
          <span class="status-badge ${att.status.includes('PRESENT') ? 'PRESENT' : 'REJECTED'}">
            ${att.status.includes('PRESENT') ? 'PRESENT' : 'REJECTED'}
          </span>
        </div>
      `).join('');
    } else {
      attContainer.innerHTML = '<p class="empty-state">No biometric attendance logged yet.</p>';
    }
  }

  // B. Load Projects
  async function loadProjects() {
    const data = await apiRequest('/api/admin/projects');
    if (!data || !data.success) return;
    projectsCache = data.projects;
    renderProjectsTable(projectsCache);
  }

  function renderProjectsTable(projects) {
    const tbody = document.getElementById('projects-table-body');
    if (!projects || projects.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No projects found. Click "Add New Project" to create one.</td></tr>';
      return;
    }

    tbody.innerHTML = projects.map(p => `
      <tr>
        <td><strong>#${p.display_order}</strong></td>
        <td>
          <div style="font-weight: 600; color: #fff;">${escapeHtml(p.title)}</div>
          <small style="color: #64748b; font-family: monospace;">/${escapeHtml(p.slug)}</small>
        </td>
        <td><span class="status-badge ARCHIVED">${escapeHtml(p.category)}</span></td>
        <td>
          ${p.technologies.slice(0, 3).map(t => `<span class="tech-tag">${escapeHtml(t)}</span>`).join('')}
          ${p.technologies.length > 3 ? `<span class="tech-tag">+${p.technologies.length - 3}</span>` : ''}
        </td>
        <td>
          <span class="status-badge ${p.is_featured ? 'RESPONDED' : 'READ'}">${p.is_featured ? 'Yes' : 'No'}</span>
        </td>
        <td>
          <div class="action-btns">
            <button class="btn btn-sm btn-outline" onclick="editProject(${p.id})">Edit</button>
            <button class="btn btn-sm btn-ghost" style="color: #f43f5e;" onclick="deleteProject(${p.id}, '${escapeHtml(p.title)}')">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  // C. Load Skills
  async function loadSkills() {
    const data = await apiRequest('/api/admin/skills');
    if (!data || !data.success) return;
    skillsCache = data.skills;
    renderSkillsTable(skillsCache);
  }

  function renderSkillsTable(skills) {
    const tbody = document.getElementById('skills-table-body');
    if (!skills || skills.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No skills found.</td></tr>';
      return;
    }

    tbody.innerHTML = skills.map(s => `
      <tr>
        <td>#${s.display_order}</td>
        <td><strong>${escapeHtml(s.name)}</strong></td>
        <td><span class="status-badge ARCHIVED">${escapeHtml(s.category)}</span></td>
        <td>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="flex: 1; height: 6px; background: #1e293b; border-radius: 3px; max-width: 100px;">
              <div style="width: ${s.proficiency_pct}%; height: 100%; background: #38bdf8; border-radius: 3px;"></div>
            </div>
            <span>${s.proficiency_pct}%</span>
          </div>
        </td>
        <td>
          <div class="action-btns">
            <button class="btn btn-sm btn-outline" onclick="editSkill(${s.id})">Edit</button>
            <button class="btn btn-sm btn-ghost" style="color: #f43f5e;" onclick="deleteSkill(${s.id}, '${escapeHtml(s.name)}')">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  // D. Load Inquiries
  async function loadInquiries(filterStatus = '') {
    const url = filterStatus && filterStatus !== 'ALL' 
      ? `/api/admin/contacts?status=${filterStatus}`
      : '/api/admin/contacts';

    const data = await apiRequest(url);
    if (!data || !data.success) return;
    inquiriesCache = data.messages;
    renderInquiriesTable(inquiriesCache);
  }

  function renderInquiriesTable(messages) {
    const tbody = document.getElementById('inquiries-table-body');
    if (!messages || messages.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No inquiries match this filter.</td></tr>';
      return;
    }

    tbody.innerHTML = messages.map(m => `
      <tr>
        <td style="font-family: monospace; font-size: 11px;">${m.created_at}</td>
        <td><strong>${escapeHtml(m.name)}</strong></td>
        <td><a href="mailto:${escapeHtml(m.email)}" style="color: #38bdf8;">${escapeHtml(m.email)}</a></td>
        <td>
          <div style="font-weight: 600;">${escapeHtml(m.subject)}</div>
          <div style="color: #94a3b8; font-size: 12px; max-width: 320px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            ${escapeHtml(m.message)}
          </div>
        </td>
        <td>
          <select class="form-input" style="padding: 4px 8px; font-size: 11px; width: auto;" onchange="updateInquiryStatus(${m.id}, this.value)">
            <option value="NEW" ${m.status === 'NEW' ? 'selected' : ''}>NEW</option>
            <option value="READ" ${m.status === 'READ' ? 'selected' : ''}>READ</option>
            <option value="RESPONDED" ${m.status === 'RESPONDED' ? 'selected' : ''}>RESPONDED</option>
            <option value="ARCHIVED" ${m.status === 'ARCHIVED' ? 'selected' : ''}>ARCHIVED</option>
          </select>
        </td>
        <td>
          <div class="action-btns">
            <a href="mailto:${escapeHtml(m.email)}?subject=Re:%20${encodeURIComponent(m.subject)}&body=Hi%20${encodeURIComponent(m.name)},%0D%0A%0D%0AThank%20you%20for%20contacting%20me..." class="btn btn-sm btn-outline">Reply</a>
            <button class="btn btn-sm btn-ghost" style="color: #f43f5e;" onclick="deleteInquiry(${m.id})">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  // E. Load Attendance
  async function loadAttendance() {
    const data = await apiRequest('/api/attendance/records?limit=50');
    if (!data || !data.success) return;
    attendanceCache = data.records;
    renderAttendanceTable(attendanceCache);
  }

  function renderAttendanceTable(records) {
    const tbody = document.getElementById('attendance-table-body');
    if (!records || records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No biometric attendance records logged yet.</td></tr>';
      return;
    }

    tbody.innerHTML = records.map(r => `
      <tr>
        <td style="font-family: monospace; font-size: 11px;">${r.timestamp}</td>
        <td><strong>${escapeHtml(r.student_id)}</strong></td>
        <td>${escapeHtml(r.student_name)}</td>
        <td>${Math.round(r.confidence_score * 100)}%</td>
        <td>
          <span class="status-badge ${r.status.includes('PRESENT') ? 'PRESENT' : 'REJECTED'}">
            ${r.status.includes('PRESENT') ? 'MARKED PRESENT' : 'REJECTED'}
          </span>
        </td>
        <td><code>${escapeHtml(r.device_id)}</code></td>
      </tr>
    `).join('');
  }

  // F. Load Profile Configurations
  async function loadProfileConfig() {
    const data = await apiRequest('/api/admin/profile');
    if (!data || !data.success) return;

    const p = data.profile;
    for (const [key, val] of Object.entries(p)) {
      const input = document.getElementById(`cfg-${key}`);
      if (input) input.value = val;
    }
  }

  // =========================================================================
  // 5. PROJECTS CRUD HANDLERS
  // =========================================================================
  const openAddProjectBtn = document.getElementById('open-add-project-modal');
  const closeProjectModalBtn = document.getElementById('close-project-modal');

  window.openProjectModal = function() {
    projectForm.reset();
    document.getElementById('proj-id').value = '';
    document.getElementById('project-modal-heading').textContent = 'Add New Project';
    projectModal.style.display = 'flex';
  };

  window.closeProjectModal = function() {
    projectModal.style.display = 'none';
  };

  if (openAddProjectBtn) openAddProjectBtn.addEventListener('click', window.openProjectModal);
  if (closeProjectModalBtn) closeProjectModalBtn.addEventListener('click', window.closeProjectModal);

  window.editProject = function(id) {
    const p = projectsCache.find(item => item.id === id);
    if (!p) return;

    document.getElementById('proj-id').value = p.id;
    document.getElementById('proj-title').value = p.title;
    document.getElementById('proj-slug').value = p.slug;
    document.getElementById('proj-category').value = p.category;
    document.getElementById('proj-order').value = p.display_order;
    document.getElementById('proj-overview').value = p.overview;
    document.getElementById('proj-problem').value = p.problem;
    document.getElementById('proj-solution').value = p.solution;
    document.getElementById('proj-features').value = (p.features || []).join('\n');
    document.getElementById('proj-technologies').value = (p.technologies || []).join(', ');
    document.getElementById('proj-repo').value = p.repo_url || '';
    document.getElementById('proj-live').value = p.live_url || '';

    document.getElementById('project-modal-heading').textContent = `Edit Project: ${p.title}`;
    projectModal.style.display = 'flex';
  };

  window.deleteProject = async function(id, title) {
    if (!confirm(`Are you sure you want to delete the project "${title}"?`)) return;
    const res = await apiRequest(`/api/admin/projects/${id}`, { method: 'DELETE' });
    if (res && res.success) {
      showToast('Project deleted successfully.', 'success');
      loadProjects();
      loadStats();
    }
  };

  if (projectForm) {
    projectForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('proj-id').value;
      const payload = {
        title: document.getElementById('proj-title').value.trim(),
        slug: document.getElementById('proj-slug').value.trim(),
        category: document.getElementById('proj-category').value.trim(),
        display_order: parseInt(document.getElementById('proj-order').value, 10) || 0,
        overview: document.getElementById('proj-overview').value.trim(),
        problem: document.getElementById('proj-problem').value.trim(),
        solution: document.getElementById('proj-solution').value.trim(),
        features: document.getElementById('proj-features').value.trim().split('\n').filter(Boolean),
        technologies: document.getElementById('proj-technologies').value.trim().split(',').map(s => s.trim()).filter(Boolean),
        repo_url: document.getElementById('proj-repo').value.trim(),
        live_url: document.getElementById('proj-live').value.trim()
      };

      const url = id ? `/api/admin/projects/${id}` : '/api/admin/projects';
      const method = id ? 'PUT' : 'POST';

      const res = await apiRequest(url, { method, body: JSON.stringify(payload) });
      if (res && res.success) {
        showToast(id ? 'Project updated successfully!' : 'Project created successfully!', 'success');
        closeProjectModal();
        loadProjects();
        loadStats();
      } else {
        showToast(res ? res.message : 'Failed to save project.', 'error');
      }
    });
  }

  // =========================================================================
  // 6. SKILLS CRUD HANDLERS
  // =========================================================================
  const openAddSkillBtn = document.getElementById('open-add-skill-modal');
  const closeSkillModalBtn = document.getElementById('close-skill-modal');

  window.openSkillModal = function() {
    skillForm.reset();
    document.getElementById('skill-id').value = '';
    document.getElementById('skill-modal-heading').textContent = 'Add Technical Skill';
    skillModal.style.display = 'flex';
  };

  window.closeSkillModal = function() {
    skillModal.style.display = 'none';
  };

  if (openAddSkillBtn) openAddSkillBtn.addEventListener('click', window.openSkillModal);
  if (closeSkillModalBtn) closeSkillModalBtn.addEventListener('click', window.closeSkillModal);

  window.editSkill = function(id) {
    const s = skillsCache.find(item => item.id === id);
    if (!s) return;

    document.getElementById('skill-id').value = s.id;
    document.getElementById('skill-name').value = s.name;
    document.getElementById('skill-category').value = s.category;
    document.getElementById('skill-proficiency').value = s.proficiency_pct;
    document.getElementById('skill-order').value = s.display_order;

    document.getElementById('skill-modal-heading').textContent = `Edit Skill: ${s.name}`;
    skillModal.style.display = 'flex';
  };

  window.deleteSkill = async function(id, name) {
    if (!confirm(`Remove skill "${name}"?`)) return;
    const res = await apiRequest(`/api/admin/skills/${id}`, { method: 'DELETE' });
    if (res && res.success) {
      showToast('Skill removed.', 'success');
      loadSkills();
      loadStats();
    }
  };

  if (skillForm) {
    skillForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('skill-id').value;
      const payload = {
        name: document.getElementById('skill-name').value.trim(),
        category: document.getElementById('skill-category').value,
        proficiency_pct: parseInt(document.getElementById('skill-proficiency').value, 10) || 85,
        display_order: parseInt(document.getElementById('skill-order').value, 10) || 0
      };

      const url = id ? `/api/admin/skills/${id}` : '/api/admin/skills';
      const method = id ? 'PUT' : 'POST';

      const res = await apiRequest(url, { method, body: JSON.stringify(payload) });
      if (res && res.success) {
        showToast('Skill saved successfully!', 'success');
        closeSkillModal();
        loadSkills();
        loadStats();
      }
    });
  }

  // =========================================================================
  // 7. INQUIRY STATUS & FILTER HANDLERS
  // =========================================================================
  window.updateInquiryStatus = async function(id, newStatus) {
    const res = await apiRequest(`/api/admin/contacts/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ status: newStatus })
    });
    if (res && res.success) {
      showToast(`Inquiry status updated to ${newStatus}`, 'success');
      loadStats();
    }
  };

  window.deleteInquiry = async function(id) {
    if (!confirm('Delete this inquiry record from database?')) return;
    const res = await apiRequest(`/api/admin/contacts/${id}`, { method: 'DELETE' });
    if (res && res.success) {
      showToast('Inquiry deleted.', 'success');
      loadInquiries();
      loadStats();
    }
  };

  // Filter pills
  document.querySelectorAll('.filter-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const filter = pill.getAttribute('data-filter');
      loadInquiries(filter);
    });
  });

  // =========================================================================
  // 8. PROFILE SETTINGS & PASSWORD CHANGE
  // =========================================================================
  const profileForm = document.getElementById('profile-config-form');
  if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        full_name: document.getElementById('cfg-full_name').value.trim(),
        professional_title: document.getElementById('cfg-professional_title').value.trim(),
        email: document.getElementById('cfg-email').value.trim(),
        phone: document.getElementById('cfg-phone').value.trim(),
        location: document.getElementById('cfg-location').value.trim(),
        education_cgpa: document.getElementById('cfg-education_cgpa').value.trim(),
        education_college: document.getElementById('cfg-education_college').value.trim(),
        github_url: document.getElementById('cfg-github_url').value.trim(),
        linkedin_url: document.getElementById('cfg-linkedin_url').value.trim()
      };

      const res = await apiRequest('/api/admin/profile', {
        method: 'PUT',
        body: JSON.stringify(payload)
      });

      if (res && res.success) {
        showToast('Profile configuration updated and live!', 'success');
      }
    });
  }

  const changePwForm = document.getElementById('change-password-form');
  if (changePwForm) {
    changePwForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const current_password = document.getElementById('current-password').value.trim();
      const new_password = document.getElementById('new-password').value.trim();

      const res = await apiRequest('/api/admin/change-password', {
        method: 'POST',
        body: JSON.stringify({ current_password, new_password })
      });

      if (res && res.success) {
        showToast('Admin password changed successfully!', 'success');
        changePwForm.reset();
      } else {
        showToast(res ? res.message : 'Password update failed', 'error');
      }
    });
  }

  // =========================================================================
  // 9. SEARCH BARS
  // =========================================================================
  const projSearch = document.getElementById('projects-search');
  if (projSearch) {
    projSearch.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = projectsCache.filter(p => 
        p.title.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q) ||
        (p.technologies || []).some(t => t.toLowerCase().includes(q))
      );
      renderProjectsTable(filtered);
    });
  }

  const skillSearch = document.getElementById('skills-search');
  if (skillSearch) {
    skillSearch.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = skillsCache.filter(s => 
        s.name.toLowerCase().includes(q) ||
        s.category.toLowerCase().includes(q)
      );
      renderSkillsTable(filtered);
    });
  }

  const attSearch = document.getElementById('attendance-search');
  if (attSearch) {
    attSearch.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = attendanceCache.filter(a => 
        a.student_id.toLowerCase().includes(q) ||
        a.student_name.toLowerCase().includes(q)
      );
      renderAttendanceTable(filtered);
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Initialize
  checkSession();
});
