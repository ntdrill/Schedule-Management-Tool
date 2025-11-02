const STORAGE_KEY = 'schedule-management-data-v1';
const userId = 'demo-user';

const defaultTemplates = [
  {
    id: crypto.randomUUID(),
    type: 'measurement_session',
    title: '自律神経モニタリング',
    category: 'wellbeing',
    defaultDuration: 480,
    color: '#34a853',
    icon: '🛰️',
    preconditions: parseStateText('user.デバイス=装着済み'),
    afterEffects: parseStateText('environment.静寂=維持'),
    measurementSettings: {
      sensor: 'HRV',
      frequency: 'continuous',
      reminder: 'スマートウォッチを装着してください',
      maxHours: 8
    },
    checklistItems: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: crypto.randomUUID(),
    type: 'task',
    title: '太極拳セッション',
    category: 'exercise',
    defaultDuration: 90,
    color: '#f6ad55',
    icon: '🧘',
    preconditions: parseStateText('user.コンディション=副交感優位\nenvironment.気温=快適'),
    afterEffects: parseStateText('user.目標=解離感解消\nuser.呼吸=深い'),
    measurementSettings: {},
    checklistItems: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: crypto.randomUUID(),
    type: 'checklist',
    title: '起床チェック',
    category: 'routine',
    defaultDuration: 15,
    color: '#6c5ce7',
    icon: '⏰',
    preconditions: parseStateText('user.睡眠=覚醒直後'),
    afterEffects: parseStateText('user.覚醒度=把握\nsocial.共有=家族通知'),
    measurementSettings: {},
    checklistItems: [
      { id: crypto.randomUUID(), label: '起床時間を記録', type: 'time' },
      { id: crypto.randomUUID(), label: '体調スコア', type: 'number' },
      { id: crypto.randomUUID(), label: '夢の内容メモ', type: 'text' }
    ],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
];

const defaultSchedules = (templates) => {
  const today = new Date();
  today.setMinutes(0, 0, 0);
  const startOfDay = new Date(today);
  startOfDay.setHours(8, 0, 0, 0);
  const measurementTemplate = templates.find(t => t.type === 'measurement_session');
  const taichiTemplate = templates.find(t => t.title.includes('太極拳'));
  const checklistTemplate = templates.find(t => t.type === 'checklist');

  if (!measurementTemplate || !taichiTemplate || !checklistTemplate) {
    return [];
  }

  const measurementStart = new Date(startOfDay);
  const measurementEnd = new Date(startOfDay);
  measurementEnd.setHours(16, 0, 0, 0);

  const taichiStart = new Date(startOfDay);
  taichiStart.setHours(9, 30, 0, 0);
  const taichiEnd = new Date(taichiStart);
  taichiEnd.setMinutes(taichiStart.getMinutes() + taichiTemplate.defaultDuration);

  const checklistStart = new Date(startOfDay);
  checklistStart.setHours(8, 10, 0, 0);
  const checklistEnd = new Date(checklistStart);
  checklistEnd.setMinutes(checklistStart.getMinutes() + checklistTemplate.defaultDuration);

  return [
    createScheduleFromTemplate(measurementTemplate, measurementStart, measurementEnd, {
      expectedBefore: measurementTemplate.preconditions,
      expectedAfter: measurementTemplate.afterEffects,
      note: '日中の自律神経モニタリング'
    }),
    createScheduleFromTemplate(taichiTemplate, taichiStart, taichiEnd, {
      expectedBefore: taichiTemplate.preconditions,
      expectedAfter: taichiTemplate.afterEffects,
      note: '測定モード下での運動セッション'
    }),
    createScheduleFromTemplate(checklistTemplate, checklistStart, checklistEnd, {
      expectedBefore: checklistTemplate.preconditions,
      expectedAfter: checklistTemplate.afterEffects,
      note: '起床後の確認リスト'
    })
  ];
};

function loadState() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return {
      templates: [...defaultTemplates],
      schedules: defaultSchedules(defaultTemplates),
      executions: []
    };
  }
  try {
    const parsed = JSON.parse(raw);
    return {
      templates: parsed.templates ?? [],
      schedules: parsed.schedules ?? [],
      executions: parsed.executions ?? []
    };
  } catch (error) {
    console.error('Failed to parse storage', error);
    return {
      templates: [...defaultTemplates],
      schedules: defaultSchedules(defaultTemplates),
      executions: []
    };
  }
}

function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function parseStateText(text) {
  if (!text) return {};
  const lines = text
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean);
  const result = {};
  for (const line of lines) {
    const [lhs, rhs] = line.split('=').map(part => part?.trim());
    if (!lhs || rhs === undefined) continue;
    const [subject, ...keys] = lhs.split('.');
    if (!subject) continue;
    const finalKey = keys.pop();
    const target = keys.reduce((acc, key) => {
      if (!key) return acc;
      if (!acc[key]) acc[key] = {};
      return acc[key];
    }, (result[subject] = result[subject] || {}));
    if (finalKey) {
      target[finalKey] = rhs;
    } else {
      result[subject] = rhs;
    }
  }
  return result;
}

function stringifyState(state) {
  return JSON.stringify(state, null, 2);
}

function createScheduleFromTemplate(template, start, end, { expectedBefore, expectedAfter, note }) {
  return {
    id: crypto.randomUUID(),
    userId,
    type: template.type,
    templateId: template.id,
    title: template.title,
    category: template.category,
    color: template.color,
    icon: template.icon,
    scheduledStart: start.toISOString(),
    scheduledEnd: end.toISOString(),
    expectedState: {
      before: expectedBefore ?? template.preconditions ?? {},
      after: expectedAfter ?? template.afterEffects ?? {}
    },
    status: 'scheduled',
    note: note ?? '',
    typeSpecific: {
      measurementSettings: template.measurementSettings ?? {},
      checklistItems: template.checklistItems ?? []
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
}

function createExecutionRecord(schedule, formData) {
  const actualBefore = parseStateText(formData.actualBefore);
  const actualAfter = parseStateText(formData.actualAfter);
  const evaluation = evaluateStateDifference(schedule.expectedState, {
    before: actualBefore,
    after: actualAfter
  });
  return {
    id: crypto.randomUUID(),
    userId,
    scheduledEventId: schedule.id,
    actualStart: new Date(formData.actualStart).toISOString(),
    actualEnd: new Date(formData.actualEnd).toISOString(),
    actualState: { before: actualBefore, after: actualAfter },
    status: formData.status,
    completionNote: formData.note,
    evaluationResult: evaluation,
    followUpActions: evaluation.followUp,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
}

function evaluateStateDifference(expected, actual) {
  const differences = [];
  let mismatchScore = 0;
  const subjects = new Set([
    ...Object.keys(expected?.before || {}),
    ...Object.keys(expected?.after || {}),
    ...Object.keys(actual?.before || {}),
    ...Object.keys(actual?.after || {})
  ]);
  subjects.forEach(subject => {
    const expectedBefore = expected?.before?.[subject] ?? {};
    const actualBefore = actual?.before?.[subject] ?? {};
    const expectedAfter = expected?.after?.[subject] ?? {};
    const actualAfter = actual?.after?.[subject] ?? {};
    const beforeDiffs = diffObjects(expectedBefore, actualBefore, `${subject}.Before`);
    const afterDiffs = diffObjects(expectedAfter, actualAfter, `${subject}.After`);
    differences.push(...beforeDiffs.differences, ...afterDiffs.differences);
    mismatchScore += beforeDiffs.score + afterDiffs.score;
  });
  const summary = differences.length
    ? `${differences.length} 件の差分を検出 (スコア ${mismatchScore})`
    : '期待状態と実際の状態は整合しています';
  const followUp = differences
    .filter(diff => diff.type === 'missingAfter')
    .map(diff => `フォローアップ: ${diff.path} が未達成。代替タスクまたはリカバリーアクションを検討。`);
  return { summary, differences, mismatchScore, followUp };
}

function diffObjects(expectedObj, actualObj, pathPrefix) {
  const differences = [];
  let score = 0;
  if (typeof expectedObj !== 'object' || expectedObj === null) {
    return { differences, score };
  }
  Object.entries(expectedObj).forEach(([key, expectedValue]) => {
    const path = `${pathPrefix}.${key}`;
    const actualValue = actualObj?.[key];
    if (typeof expectedValue === 'object') {
      const nested = diffObjects(expectedValue, actualValue ?? {}, path);
      differences.push(...nested.differences);
      score += nested.score;
    } else if (actualValue === undefined) {
      differences.push({ path, type: 'missingAfter', message: `${path} が記録されていません` });
      score += 2;
    } else if (String(actualValue) !== String(expectedValue)) {
      differences.push({ path, type: 'mismatch', message: `${path} が期待値 ${expectedValue} と異なり ${actualValue}` });
      score += 1;
    }
  });
  return { differences, score };
}

function renderTemplates(state) {
  const list = document.getElementById('template-list');
  list.innerHTML = '';
  state.templates.forEach(template => {
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <h3><span>${template.icon || '📦'} ${template.title}</span><span class="badge">${template.type}</span></h3>
      <div class="metadata">
        <span>カテゴリ: ${template.category || '未設定'}</span>
        <span>所要時間: ${template.defaultDuration}分</span>
        <span>更新: ${formatDate(template.updatedAt)}</span>
      </div>
      <details>
        <summary>状態シグネチャ</summary>
        <div>
          <strong>Before</strong>
          <pre class="state-block">${stringifyState(template.preconditions)}</pre>
          <strong>After</strong>
          <pre class="state-block">${stringifyState(template.afterEffects)}</pre>
        </div>
      </details>
      ${template.type === 'measurement_session' ? renderMeasurementInfo(template.measurementSettings) : ''}
      ${template.type === 'checklist' ? renderChecklistInfo(template.checklistItems) : ''}
    `;
    list.appendChild(card);
  });
}

function renderMeasurementInfo(settings = {}) {
  if (!Object.keys(settings).length) return '';
  return `
    <details>
      <summary>測定モード設定</summary>
      <pre class="state-block">${stringifyState(settings)}</pre>
    </details>
  `;
}

function renderChecklistInfo(items = []) {
  if (!items.length) return '';
  return `
    <details>
      <summary>チェックリスト項目 (${items.length}件)</summary>
      <ul>
        ${items.map(item => `<li>${item.label} (${item.type})</li>`).join('')}
      </ul>
    </details>
  `;
}

function renderScheduleOptions(state) {
  const select = document.querySelector('#schedule-form select[name="templateId"]');
  select.innerHTML = state.templates
    .map(template => `<option value="${template.id}">${template.icon || '📦'} ${template.title}</option>`)
    .join('');
}

function renderExecutionOptions(state) {
  const select = document.querySelector('#execution-form select[name="scheduledEventId"]');
  const options = state.schedules
    .map(schedule => `<option value="${schedule.id}">${formatDate(schedule.scheduledStart, true)} ${schedule.title}</option>`)
    .join('');
  select.innerHTML = `<option value="" disabled selected>選択してください</option>${options}`;
}

function renderSchedules(state) {
  const list = document.getElementById('schedule-list');
  list.innerHTML = '';
  const grouped = groupSchedulesByDate(state.schedules);
  Object.entries(grouped).forEach(([date, schedules]) => {
    const dayCard = document.createElement('article');
    dayCard.className = 'card';
    dayCard.innerHTML = `<h3>${date}</h3>`;
    schedules
      .sort((a, b) => new Date(a.scheduledStart) - new Date(b.scheduledStart))
      .forEach(schedule => {
        const exec = state.executions.find(e => e.scheduledEventId === schedule.id);
        const row = document.createElement('section');
        row.innerHTML = `
          <div class="metadata">
            <span>${schedule.icon || '🗓️'} ${schedule.title}</span>
            <span>${formatDate(schedule.scheduledStart, true)} - ${formatDate(schedule.scheduledEnd, true)}</span>
            <span class="status-chip">${schedule.status}</span>
          </div>
          <details>
            <summary>詳細</summary>
            <div class="metadata"><span>カテゴリ: ${schedule.category || '未設定'}</span></div>
            <strong>期待状態 Before</strong>
            <pre class="state-block">${stringifyState(schedule.expectedState.before)}</pre>
            <strong>期待状態 After</strong>
            <pre class="state-block">${stringifyState(schedule.expectedState.after)}</pre>
            ${schedule.note ? `<p>メモ: ${schedule.note}</p>` : ''}
            ${exec ? renderExecutionInline(exec) : '<p>実行記録はまだありません。</p>'}
          </details>
        `;
        dayCard.appendChild(row);
      });
    list.appendChild(dayCard);
  });
}

function renderExecutionInline(execution) {
  return `
    <div class="metadata">
      <span>実行ステータス: ${execution.status}</span>
      <span>${formatDate(execution.actualStart, true)} - ${formatDate(execution.actualEnd, true)}</span>
    </div>
    <details>
      <summary>実行状態と評価</summary>
      <strong>実行前</strong>
      <pre class="state-block">${stringifyState(execution.actualState.before)}</pre>
      <strong>実行後</strong>
      <pre class="state-block">${stringifyState(execution.actualState.after)}</pre>
      <p>${execution.evaluationResult.summary}</p>
      ${execution.evaluationResult.differences.length ? `<pre class="state-block">${stringifyState(execution.evaluationResult.differences)}</pre>` : ''}
      ${execution.followUpActions?.length ? `<ul>${execution.followUpActions.map(f => `<li>${f}</li>`).join('')}</ul>` : ''}
      ${execution.completionNote ? `<p>ノート: ${execution.completionNote}</p>` : ''}
    </details>
  `;
}

function renderExecutions(state) {
  const list = document.getElementById('execution-list');
  list.innerHTML = '';
  state.executions
    .sort((a, b) => new Date(b.actualStart) - new Date(a.actualStart))
    .forEach(exec => {
      const schedule = state.schedules.find(s => s.id === exec.scheduledEventId);
      const card = document.createElement('article');
      card.className = 'card';
      card.innerHTML = `
        <h3><span>${schedule?.icon || '✅'} ${schedule?.title || '不明な予定'}</span><span class="badge">${exec.status}</span></h3>
        <div class="metadata">
          <span>${formatDate(exec.actualStart, true)} - ${formatDate(exec.actualEnd, true)}</span>
          <span>評価スコア: ${exec.evaluationResult.mismatchScore}</span>
        </div>
        <p>${exec.evaluationResult.summary}</p>
        ${exec.evaluationResult.differences.length ? `<pre class="state-block">${stringifyState(exec.evaluationResult.differences)}</pre>` : ''}
        ${exec.followUpActions?.length ? `<ul>${exec.followUpActions.map(f => `<li>${f}</li>`).join('')}</ul>` : ''}
        ${exec.completionNote ? `<p>ノート: ${exec.completionNote}</p>` : ''}
      `;
      list.appendChild(card);
    });
}

function groupSchedulesByDate(schedules) {
  const groups = {};
  schedules.forEach(schedule => {
    const date = new Date(schedule.scheduledStart);
    const key = date.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' });
    if (!groups[key]) groups[key] = [];
    groups[key].push(schedule);
  });
  return groups;
}

function renderTimeline(state, selectedDate) {
  const timeline = document.getElementById('timeline');
  timeline.innerHTML = '';
  const hoursLayer = document.createElement('div');
  hoursLayer.className = 'timeline-hours';
  Array.from({ length: 24 }).forEach((_, hour) => {
    const span = document.createElement('span');
    span.textContent = `${String(hour).padStart(2, '0')}:00`;
    hoursLayer.appendChild(span);
  });
  const grid = document.createElement('div');
  grid.className = 'timeline-grid';
  const measurementLayer = document.createElement('div');
  measurementLayer.className = 'measurement-layer';
  const eventLayer = document.createElement('div');
  eventLayer.className = 'event-layer';

  const daySchedules = state.schedules.filter(schedule => {
    const date = new Date(schedule.scheduledStart);
    return date.getFullYear() === selectedDate.getFullYear() &&
      date.getMonth() === selectedDate.getMonth() &&
      date.getDate() === selectedDate.getDate();
  });

  if (!daySchedules.length) {
    const empty = document.createElement('p');
    empty.style.padding = '1rem';
    empty.textContent = 'この日に予定は登録されていません。';
    timeline.append(grid, hoursLayer, empty);
    return;
  }

  const measurements = daySchedules.filter(s => s.type === 'measurement_session');
  measurements.forEach(measurement => {
    const block = document.createElement('div');
    block.className = 'measurement-block';
    positionBlock(block, measurement);
    block.style.backgroundColor = hexToRgba(measurement.color || '#34a853', 0.18);
    block.style.borderColor = hexToRgba(measurement.color || '#34a853', 0.35);
    block.innerHTML = `
      <span class="title">${measurement.icon || '🛰️'} ${measurement.title}</span>
      <span class="metadata">${formatDate(measurement.scheduledStart, true)} - ${formatDate(measurement.scheduledEnd, true)}</span>
    `;
    measurementLayer.appendChild(block);
  });

  const otherEvents = daySchedules.filter(s => s.type !== 'measurement_session');
  const positioned = assignColumns(otherEvents);
  const columnCount = Math.max(1, positioned.reduce((max, item) => Math.max(max, item.column), -Infinity) + 1);
  positioned.forEach(item => {
    const block = document.createElement('div');
    block.className = 'event-block';
    block.style.background = hexToRgba(item.schedule.color || '#2d9cdb', 0.85);
    block.style.border = `1px solid ${hexToRgba(item.schedule.color || '#2d9cdb', 1)}`;
    positionBlock(block, item.schedule);
    const widthPercent = 100 / columnCount;
    block.style.width = `calc(${widthPercent}% - 1.5rem)`;
    const leftPercent = widthPercent * item.column;
    block.style.left = `calc(${leftPercent}% + 1rem)`;
    block.innerHTML = `
      <div class="title">${item.schedule.icon || '🗓️'} ${item.schedule.title}</div>
      <span class="status-chip">${item.schedule.status}</span>
      <span class="metadata">${formatDate(item.schedule.scheduledStart, true)} - ${formatDate(item.schedule.scheduledEnd, true)}</span>
    `;
    eventLayer.appendChild(block);
  });

  timeline.append(grid, hoursLayer, measurementLayer, eventLayer);
}

function positionBlock(element, schedule) {
  const start = new Date(schedule.scheduledStart);
  const end = new Date(schedule.scheduledEnd);
  const minutesStart = (start.getHours() * 60 + start.getMinutes());
  const minutesEnd = (end.getHours() * 60 + end.getMinutes());
  const duration = Math.max(minutesEnd - minutesStart, 15);
  const timeline = document.getElementById('timeline');
  const fallbackHeight = 420;
  const totalHeight = Math.max((timeline?.clientHeight || 0) - 32, fallbackHeight - 32);
  const minuteHeight = totalHeight / (24 * 60);
  element.style.top = `${minutesStart * minuteHeight + 16}px`;
  element.style.height = `${duration * minuteHeight - 8}px`;
}

function assignColumns(events) {
  const columns = [];
  return events
    .sort((a, b) => new Date(a.scheduledStart) - new Date(b.scheduledStart))
    .map(schedule => {
      const start = new Date(schedule.scheduledStart).getTime();
      const end = new Date(schedule.scheduledEnd).getTime();
      let column = 0;
      while (true) {
        if (!columns[column] || columns[column] <= start) {
          columns[column] = end;
          break;
        }
        column += 1;
      }
      return { schedule, column };
    });
}

function hexToRgba(hex, alpha = 1) {
  const sanitized = hex.replace('#', '');
  const bigint = parseInt(sanitized, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function formatDate(value, includeTime = false) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '未設定';
  const base = date.toLocaleDateString('ja-JP', { year: 'numeric', month: 'short', day: 'numeric', weekday: 'short' });
  if (!includeTime) return base;
  const time = date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
  return `${base} ${time}`;
}

function handleTemplateSubmit(event, state) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const type = formData.get('type');
  const template = {
    id: crypto.randomUUID(),
    type,
    title: formData.get('title'),
    category: formData.get('category'),
    defaultDuration: Number(formData.get('defaultDuration')) || 60,
    color: formData.get('color') || '#2d9cdb',
    icon: formData.get('icon'),
    preconditions: parseStateText(formData.get('preconditions')),
    afterEffects: parseStateText(formData.get('afterEffects')),
    measurementSettings: type === 'measurement_session' ? parseStateText(formData.get('measurementSettings')) : {},
    checklistItems: type === 'checklist' ? parseChecklistItems(formData.get('checklistItems')) : [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  state.templates.push(template);
  saveState(state);
  event.target.reset();
  renderTemplates(state);
  renderScheduleOptions(state);
}

function parseChecklistItems(text) {
  if (!text) return [];
  return text
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean)
    .map(line => {
      const [label, typePart] = line.split('=').map(part => part.trim());
      return {
        id: crypto.randomUUID(),
        label,
        type: typePart || 'text'
      };
    });
}

function handleScheduleSubmit(event, state) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const templateId = formData.get('templateId');
  const template = state.templates.find(t => t.id === templateId);
  if (!template) return;
  const start = new Date(formData.get('scheduledStart'));
  const end = new Date(formData.get('scheduledEnd'));
  const schedule = createScheduleFromTemplate(template, start, end, {
    expectedBefore: mergeStates(template.preconditions, parseStateText(formData.get('expectedBefore'))),
    expectedAfter: mergeStates(template.afterEffects, parseStateText(formData.get('expectedAfter'))),
    note: formData.get('note')
  });
  state.schedules.push(schedule);
  saveState(state);
  event.target.reset();
  renderSchedules(state);
  renderExecutionOptions(state);
  const selectedDate = document.getElementById('timeline-date').value ? new Date(document.getElementById('timeline-date').value) : new Date(schedule.scheduledStart);
  document.getElementById('timeline-date').value = selectedDate.toISOString().slice(0, 10);
  renderTimeline(state, selectedDate);
}

function mergeStates(base, override) {
  const result = JSON.parse(JSON.stringify(base || {}));
  function merge(target, source) {
    Object.entries(source || {}).forEach(([key, value]) => {
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        target[key] = target[key] || {};
        merge(target[key], value);
      } else {
        target[key] = value;
      }
    });
  }
  merge(result, override || {});
  return result;
}

function handleExecutionSubmit(event, state) {
  event.preventDefault();
  const formData = Object.fromEntries(new FormData(event.target).entries());
  const schedule = state.schedules.find(s => s.id === formData.scheduledEventId);
  if (!schedule) return;
  const execution = createExecutionRecord(schedule, formData);
  state.executions = state.executions.filter(exec => exec.scheduledEventId !== schedule.id);
  state.executions.push(execution);
  schedule.updatedAt = new Date().toISOString();
  saveState(state);
  event.target.reset();
  renderSchedules(state);
  renderExecutions(state);
  renderTimeline(state, new Date(schedule.scheduledStart));
}

function setupTimelineDate(state) {
  const input = document.getElementById('timeline-date');
  const firstSchedule = state.schedules[0];
  const today = firstSchedule ? new Date(firstSchedule.scheduledStart) : new Date();
  input.value = today.toISOString().slice(0, 10);
  input.addEventListener('change', () => {
    const selected = new Date(input.value);
    renderTimeline(state, selected);
  });
  renderTimeline(state, today);
}

function setupScheduleForm(state) {
  const form = document.getElementById('schedule-form');
  const startInput = form.querySelector('input[name="scheduledStart"]');
  const endInput = form.querySelector('input[name="scheduledEnd"]');
  const templateSelect = form.querySelector('select[name="templateId"]');

  const updateEndTime = () => {
    const startValue = startInput.value;
    if (!startValue) return;
    const template = state.templates.find(t => t.id === templateSelect.value);
    const duration = template?.defaultDuration ?? 60;
    const startDate = new Date(startValue);
    if (Number.isNaN(startDate.getTime())) return;
    const endDate = new Date(startDate.getTime() + duration * 60 * 1000);
    endInput.value = endDate.toISOString().slice(0, 16);
  };

  startInput.addEventListener('change', updateEndTime);
  templateSelect.addEventListener('change', updateEndTime);

  if (templateSelect.value && startInput.value) {
    updateEndTime();
  }
}

function init() {
  const state = loadState();
  renderTemplates(state);
  renderScheduleOptions(state);
  renderSchedules(state);
  renderExecutionOptions(state);
  renderExecutions(state);
  setupTimelineDate(state);
  setupScheduleForm(state);

  document.getElementById('template-form').addEventListener('submit', (event) => handleTemplateSubmit(event, state));
  document.getElementById('schedule-form').addEventListener('submit', (event) => handleScheduleSubmit(event, state));
  document.getElementById('execution-form').addEventListener('submit', (event) => handleExecutionSubmit(event, state));
}

window.addEventListener('DOMContentLoaded', init);
