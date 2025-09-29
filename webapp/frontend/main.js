const classListEl = document.querySelector('#class-list');
const classFilterEl = document.querySelector('#class-filter');
const classSelectEl = document.querySelector('#behavior-class');
const classDetailsEl = document.querySelector('#class-details');

const behaviorForm = document.querySelector('#behavior-form');
const resetFormBtn = document.querySelector('#reset-form');
const behaviorTableBody = document.querySelector('#behavior-table tbody');

const validateBtn = document.querySelector('#validate-btn');
const exportBtn = document.querySelector('#export-btn');
const exportFileBtn = document.querySelector('#export-file-btn');
const validationReportEl = document.querySelector('#validation-report');
const exportOutputEl = document.querySelector('#export-output');
const exportPathEl = document.querySelector('#export-path');

const prefixTableBody = document.querySelector('#prefix-table tbody');
const prefixForm = document.querySelector('#prefix-form');
const prefixNameEl = document.querySelector('#prefix-name');
const prefixIriEl = document.querySelector('#prefix-iri');

let behaviorClasses = [];
let prefixes = {};

async function loadBehaviorClasses() {
  const response = await fetch('/api/behavior-classes');
  behaviorClasses = await response.json();
  renderClassList();
  renderClassOptions();
}

function renderClassList() {
  const filterText = classFilterEl.value.trim().toLowerCase();
  classListEl.innerHTML = '';
  const items = behaviorClasses.filter((item) => {
    if (!filterText) return true;
    return (item.label || '').toLowerCase().includes(filterText) || item.iri.toLowerCase().includes(filterText);
  });
  items.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'class-card';
    const title = document.createElement('h3');
    title.textContent = item.label || item.iri;
    const subtitle = document.createElement('p');
    subtitle.textContent = item.iri;
    card.appendChild(title);
    card.appendChild(subtitle);
    if (item.description) {
      const desc = document.createElement('p');
      desc.textContent = item.description;
      card.appendChild(desc);
    }
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'Use in form';
    button.addEventListener('click', () => {
      classSelectEl.value = item.iri;
      updateClassDetails();
      behaviorForm.scrollIntoView({ behavior: 'smooth' });
    });
    card.appendChild(button);
    classListEl.appendChild(card);
  });
}

function renderClassOptions() {
  classSelectEl.innerHTML = '';
  behaviorClasses.forEach((item) => {
    const option = document.createElement('option');
    option.value = item.iri;
    option.textContent = item.label ? `${item.label} (${item.iri})` : item.iri;
    classSelectEl.appendChild(option);
  });
  updateClassDetails();
}

function updateClassDetails() {
  const iri = classSelectEl.value;
  const selected = behaviorClasses.find((item) => item.iri === iri);
  if (!selected) {
    classDetailsEl.innerHTML = '';
    return;
  }
  classDetailsEl.innerHTML = '';
  if (selected.comment) {
    const comment = document.createElement('p');
    comment.textContent = selected.comment;
    classDetailsEl.appendChild(comment);
  }
  if (selected.category) {
    const category = document.createElement('p');
    category.innerHTML = `<strong>Category:</strong> ${selected.category}`;
    classDetailsEl.appendChild(category);
  }
}

async function loadBehaviors() {
  const response = await fetch('/api/behaviors');
  const data = await response.json();
  renderBehaviorTable(data);
}

function renderBehaviorTable(entries) {
  behaviorTableBody.innerHTML = '';
  entries.forEach((entry) => {
    const row = document.createElement('tr');
    const cells = [
      entry.identifier,
      entry.behavior_class,
      entry.has_start,
      entry.has_end || '',
      entry.performed_by,
      entry.has_target || '',
    ];
    cells.forEach((value) => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.appendChild(cell);
    });

    const actionsCell = document.createElement('td');
    const editBtn = document.createElement('button');
    editBtn.type = 'button';
    editBtn.textContent = 'Edit';
    editBtn.className = 'secondary';
    editBtn.addEventListener('click', () => populateForm(entry));

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.textContent = 'Delete';
    deleteBtn.className = 'danger';
    deleteBtn.addEventListener('click', () => deleteBehavior(entry.uid));

    actionsCell.appendChild(editBtn);
    actionsCell.appendChild(deleteBtn);
    row.appendChild(actionsCell);
    behaviorTableBody.appendChild(row);
  });
}

function populateForm(entry) {
  document.querySelector('#behavior-uid').value = entry.uid;
  document.querySelector('#identifier').value = entry.identifier;
  classSelectEl.value = entry.behavior_class;
  document.querySelector('#performed-by').value = entry.performed_by;
  document.querySelector('#has-start').value = entry.has_start;
  document.querySelector('#has-end').value = entry.has_end || '';
  document.querySelector('#has-target').value = entry.has_target || '';
  const duration = entry.has_duration;
  document.querySelector('#has-duration').value = duration !== null && duration !== undefined ? duration : '';
  const confidence = entry.confidence;
  document.querySelector('#confidence').value = confidence !== null && confidence !== undefined ? confidence : '';
  const distance = entry.distance_to_target;
  document.querySelector('#distance-to-target').value = distance !== null && distance !== undefined ? distance : '';
  const heading = entry.heading_to_target;
  document.querySelector('#heading-to-target').value = heading !== null && heading !== undefined ? heading : '';
  document.querySelector('#evidence').value = entry.evidence || '';
  updateClassDetails();
}

function resetForm() {
  behaviorForm.reset();
  document.querySelector('#behavior-uid').value = '';
  updateClassDetails();
}

function collectFormData() {
  const payload = {
    identifier: document.querySelector('#identifier').value.trim(),
    behavior_class: classSelectEl.value,
    performed_by: document.querySelector('#performed-by').value.trim(),
    has_start: document.querySelector('#has-start').value.trim(),
    has_end: document.querySelector('#has-end').value.trim() || null,
    has_target: document.querySelector('#has-target').value.trim() || null,
    has_duration: document.querySelector('#has-duration').value ? parseFloat(document.querySelector('#has-duration').value) : null,
    confidence: document.querySelector('#confidence').value ? parseFloat(document.querySelector('#confidence').value) : null,
    distance_to_target: document.querySelector('#distance-to-target').value ? parseFloat(document.querySelector('#distance-to-target').value) : null,
    heading_to_target: document.querySelector('#heading-to-target').value ? parseFloat(document.querySelector('#heading-to-target').value) : null,
    evidence: document.querySelector('#evidence').value.trim() || null,
  };
  return payload;
}

behaviorForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = collectFormData();
  const uid = document.querySelector('#behavior-uid').value;
  const method = uid ? 'PUT' : 'POST';
  const url = uid ? `/api/behaviors/${uid}` : '/api/behaviors';
  const response = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const problem = await response.json().catch(() => ({}));
    alert(problem.detail || 'Unable to save behavior');
    return;
  }
  resetForm();
  await loadBehaviors();
});

resetFormBtn.addEventListener('click', () => {
  resetForm();
});

async function deleteBehavior(uid) {
  if (!confirm('Delete this behavior?')) return;
  const response = await fetch(`/api/behaviors/${uid}`, { method: 'DELETE' });
  if (!response.ok) {
    alert('Failed to delete behavior');
    return;
  }
  await loadBehaviors();
}

classFilterEl.addEventListener('input', renderClassList);
classSelectEl.addEventListener('change', updateClassDetails);

validateBtn.addEventListener('click', async () => {
  const response = await fetch('/api/validate', { method: 'POST' });
  if (!response.ok) {
    validationReportEl.textContent = 'Validation failed to execute.';
    return;
  }
  const result = await response.json();
  validationReportEl.textContent = `Conforms: ${result.conforms}\n\n${result.report}`;
});

exportBtn.addEventListener('click', async () => {
  const response = await fetch('/api/export');
  if (!response.ok) {
    exportOutputEl.value = 'Export failed.';
    return;
  }
  const result = await response.json();
  exportOutputEl.value = result.ttl;
  exportPathEl.textContent = '';
});

exportFileBtn.addEventListener('click', async () => {
  const response = await fetch('/api/export/file');
  if (!response.ok) {
    exportPathEl.textContent = 'Export to file failed.';
    return;
  }
  const result = await response.json();
  exportPathEl.textContent = `Export written to ${result.path}`;
});

async function loadPrefixes() {
  const response = await fetch('/api/prefixes');
  prefixes = await response.json();
  renderPrefixes();
}

function renderPrefixes() {
  prefixTableBody.innerHTML = '';
  Object.entries(prefixes).forEach(([prefix, iri]) => {
    const row = document.createElement('tr');
    const prefixCell = document.createElement('td');
    prefixCell.textContent = prefix;
    const iriCell = document.createElement('td');
    iriCell.textContent = iri;
    const actionsCell = document.createElement('td');
    if (!['mbo', 'ex'].includes(prefix)) {
      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'danger';
      removeBtn.textContent = 'Remove';
      removeBtn.addEventListener('click', () => removePrefix(prefix));
      actionsCell.appendChild(removeBtn);
    }
    row.appendChild(prefixCell);
    row.appendChild(iriCell);
    row.appendChild(actionsCell);
    prefixTableBody.appendChild(row);
  });
}

prefixForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = {
    prefix: prefixNameEl.value.trim(),
    iri: prefixIriEl.value.trim(),
  };
  const response = await fetch('/api/prefixes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    alert(detail.detail || 'Failed to set prefix');
    return;
  }
  prefixNameEl.value = '';
  prefixIriEl.value = '';
  await loadPrefixes();
});

async function removePrefix(prefix) {
  const response = await fetch(`/api/prefixes/${prefix}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    alert(detail.detail || 'Unable to remove prefix');
    return;
  }
  await loadPrefixes();
}

async function bootstrap() {
  await Promise.all([loadBehaviorClasses(), loadBehaviors(), loadPrefixes()]);
}

bootstrap();
