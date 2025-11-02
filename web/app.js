import {
  categories,
  criticalStates,
  dictionary,
  initialState,
  taskTemplates,
} from './data.js';

const appState = {
  currentDate: new Date(),
  scheduleItems: [],
  state: deepClone(initialState),
  notifications: [],
};

const statusStyles = {
  scheduled: 'badge warning',
  in_progress: 'badge warning',
  completed: 'badge success',
  skipped: 'badge warning',
  failed: 'badge danger',
  cancelled: 'badge danger',
  postponed: 'badge warning',
};

init();

function init() {
  const dateInput = document.getElementById('schedule-date');
  dateInput.value = formatDateInput(appState.currentDate);
  dateInput.addEventListener('change', (event) => {
    const newDate = event.target.valueAsDate;
    if (newDate) {
      appState.currentDate = newDate;
      addNotification(`対象日を${formatDateDisplay(newDate)}に切り替えました。`);
      renderScheduleList();
    }
  });

  document.getElementById('reset-day').addEventListener('click', () => {
    appState.currentDate = new Date();
    dateInput.value = formatDateInput(appState.currentDate);
    addNotification('対象日を本日に戻しました。');
    renderScheduleList();
  });

  populateTemplateFilters();
  renderStateEditor();
  renderTemplateList();
  seedInitialSchedule();
  renderScheduleList();
  renderNotificationList();
}

function populateTemplateFilters() {
  const categorySelect = document.getElementById('template-category-filter');
  categories.forEach((category) => {
    const option = document.createElement('option');
    option.value = category.id;
    option.textContent = category.label;
    categorySelect.appendChild(option);
  });
  categorySelect.addEventListener('change', renderTemplateList);

  const criticalSelect = document.getElementById('template-critical-filter');
  const criticalOptionSet = new Set();
  taskTemplates.forEach((template) => {
    const relation = template.criticalStateRelation || {};
    ['helpsRecover', 'prevents'].forEach((key) => {
      (relation[key] || []).forEach((value) => criticalOptionSet.add(value));
    });
  });
  Array.from(criticalOptionSet)
    .sort()
    .forEach((critical) => {
      const option = document.createElement('option');
      option.value = critical;
      option.textContent = critical;
      criticalSelect.appendChild(option);
    });
  criticalSelect.addEventListener('change', renderTemplateList);
}

function seedInitialSchedule() {
  if (appState.scheduleItems.length) {
    return;
  }
  const seeds = [
    { templateId: 'taichi_session', hour: 9, minute: 0 },
    { templateId: 'deep_cleaning', hour: 11, minute: 0 },
    { templateId: 'message_check_in', hour: 15, minute: 30 },
  ];
  seeds.forEach((seed) => {
    const template = taskTemplates.find((candidate) => candidate.id === seed.templateId);
    if (!template) return;
    createScheduleItem(template, seed.hour, seed.minute, template.defaultDurationMinutes);
  });
  addNotification('ドキュメントを参考にしたサンプル予定を読み込みました。');
}

function renderStateEditor() {
  const container = document.getElementById('state-editor');
  container.innerHTML = '';

  const subjectLabels = {
    user: 'ユーザー',
    environment: '環境',
    social: '社会',
  };

  Object.entries(dictionary).forEach(([subject, fields]) => {
    const section = document.createElement('section');
    section.className = 'state-section';

    const heading = document.createElement('h3');
    heading.textContent = subjectLabels[subject] || subject.toUpperCase();
    section.appendChild(heading);

    Object.entries(fields).forEach(([field, options]) => {
      const label = document.createElement('label');
      label.textContent = field;
      const input = document.createElement('input');
      input.type = 'text';
      input.value = appState.state[subject]?.[field] ?? '';
      const listId = `${subject}-${field}-options`;
      input.setAttribute('list', listId);
      input.dataset.subject = subject;
      input.dataset.field = field;

      const dataList = document.createElement('datalist');
      dataList.id = listId;
      options.forEach((value) => {
        const option = document.createElement('option');
        option.value = value;
        dataList.appendChild(option);
      });

      label.appendChild(input);
      section.appendChild(label);
      section.appendChild(dataList);
    });

    container.appendChild(section);
  });

  const actions = document.createElement('div');
  actions.className = 'state-actions';

  const snapshotButton = document.createElement('button');
  snapshotButton.className = 'secondary';
  snapshotButton.textContent = '状態スナップショットを記録';
  snapshotButton.addEventListener('click', () => {
    const snapshot = deepClone(appState.state);
    addNotification('現在の状態をスナップショットとして保存しました。');
    appState.lastSnapshot = { createdAt: new Date(), payload: snapshot };
    renderScheduleList();
  });
  actions.appendChild(snapshotButton);

  const evaluateButton = document.createElement('button');
  evaluateButton.className = 'primary';
  evaluateButton.textContent = '前提条件スキャン';
  evaluateButton.addEventListener('click', () => {
    appState.scheduleItems.forEach((item) => {
      const report = evaluatePreconditions(item.preconditions, appState.state);
      if (!report.total) {
        return;
      }
      const ratio = Math.round((report.satisfied / report.total) * 100);
      addNotification(
        `${item.title} の前提条件適合率は ${ratio}% です。${
          report.passed ? '実行に適しています。' : '代替タスクの検討が必要です。'
        }`
      );
    });
  });
  actions.appendChild(evaluateButton);

  container.appendChild(actions);

  if (!container.dataset.bound) {
    container.addEventListener('input', (event) => {
      const target = event.target;
      if (target.dataset.subject && target.dataset.field) {
        const { subject, field } = target.dataset;
        if (!appState.state[subject]) {
          appState.state[subject] = {};
        }
        appState.state[subject][field] = target.value;
      }
    });
    container.dataset.bound = 'true';
  }
}

function renderTemplateList() {
  const list = document.getElementById('template-list');
  list.innerHTML = '';
  const categoryFilter = document.getElementById('template-category-filter').value;
  const criticalFilter = document.getElementById('template-critical-filter').value;

  taskTemplates
    .filter((template) => {
      if (categoryFilter !== 'all' && template.category !== categoryFilter) {
        return false;
      }
      if (criticalFilter !== 'all') {
        const relation = template.criticalStateRelation || {};
        return ['helpsRecover', 'prevents'].some((key) =>
          (relation[key] || []).includes(criticalFilter)
        );
      }
      return true;
    })
    .forEach((template) => {
      list.appendChild(createTemplateCard(template));
    });
}

function createTemplateCard(template) {
  const card = document.createElement('article');
  card.className = 'template-card';

  const header = document.createElement('header');
  const title = document.createElement('h3');
  title.textContent = `${template.icon} ${template.title}`;
  header.appendChild(title);

  const categoryTag = document.createElement('span');
  categoryTag.className = 'schedule-tag';
  categoryTag.textContent =
    categories.find((c) => c.id === template.category)?.label || template.category;
  header.appendChild(categoryTag);

  card.appendChild(header);

  const meta = document.createElement('p');
  meta.className = 'meta';
  meta.textContent = `所要時間: ${template.defaultDurationMinutes}分 / カラー: ${template.color}`;
  card.appendChild(meta);

  const description = document.createElement('p');
  description.textContent = template.description;
  card.appendChild(description);

  const signature = document.createElement('div');
  signature.className = 'state-signature';
  signature.innerHTML = `<strong>状態シグネチャ</strong><br>${renderStateSummary(
    template.stateSignature
  )}`;
  card.appendChild(signature);

  const preconditions = document.createElement('div');
  preconditions.className = 'preconditions';
  preconditions.innerHTML = `<strong>前提条件</strong><br>${renderStateSummary(
    template.preconditions
  ) || '指定なし'}`;
  card.appendChild(preconditions);

  const critical = document.createElement('div');
  critical.className = 'critical-relations';
  critical.innerHTML = renderCriticalRelations(template.criticalStateRelation);
  card.appendChild(critical);

  const button = document.createElement('button');
  button.textContent = '予定に追加';
  button.addEventListener('click', () => addTemplateToSchedule(template));
  card.appendChild(button);

  return card;
}

function renderCriticalRelations(relation = {}) {
  const parts = [];
  if (relation.helpsRecover?.length) {
    parts.push(`回復支援: ${relation.helpsRecover.join(', ')}`);
  }
  if (relation.prevents?.length) {
    parts.push(`予防: ${relation.prevents.join(', ')}`);
  }
  return parts.length ? parts.join('<br>') : '危篤状態との関係: 設定なし';
}

function addTemplateToSchedule(template) {
  const startTime = prompt('開始時刻をHH:MM形式で入力してください', '09:00');
  if (!startTime) {
    return;
  }
  const [hourStr, minuteStr] = startTime.split(':');
  const startHour = Number(hourStr);
  const startMinute = Number(minuteStr);
  if (
    Number.isNaN(startHour) ||
    Number.isNaN(startMinute) ||
    startHour < 0 ||
    startHour > 23 ||
    startMinute < 0 ||
    startMinute > 59
  ) {
    alert('開始時刻の形式が正しくありません。');
    return;
  }

  const duration = Number(
    prompt('所要時間（分）を入力してください', template.defaultDurationMinutes)
  );
  if (!duration || Number.isNaN(duration)) {
    alert('所要時間の形式が正しくありません。');
    return;
  }

  createScheduleItem(template, startHour, startMinute, duration);
}

function inferPriority(relation = {}) {
  const related = new Set([...(relation.helpsRecover || []), ...(relation.prevents || [])]);
  const priorityMap = new Map(criticalStates.map((state) => [state.label, state.priority]));
  let priority = 'normal';
  related.forEach((label) => {
    const p = priorityMap.get(label);
    if (!p) return;
    if (p === 'urgent') {
      priority = 'urgent';
    } else if (p === 'high' && priority !== 'urgent') {
      priority = 'high';
    } else if (p === 'medium' && !['urgent', 'high'].includes(priority)) {
      priority = 'medium';
    }
  });
  return priority;
}

function renderScheduleList() {
  const container = document.getElementById('schedule-list');
  container.innerHTML = '';
  if (!appState.scheduleItems.length) {
    container.innerHTML = '<p>まだ予定がありません。テンプレートから追加してください。</p>';
    return;
  }

  const template = document.getElementById('schedule-row-template');

  appState.scheduleItems.forEach((item) => {
    const fragment = template.content.cloneNode(true);
    const article = fragment.querySelector('.schedule-item');
    article.style.borderLeft = `6px solid ${item.color}`;

    const title = fragment.querySelector('.schedule-title');
    title.textContent = `${item.icon} ${item.title}`;

    const time = fragment.querySelector('.schedule-time');
    time.textContent = formatTimeRange(item.scheduledStart, item.scheduledEnd);

    const status = fragment.querySelector('.schedule-status');
    status.className = `schedule-status ${statusStyles[item.status] || 'badge'}`;
    status.textContent = translateStatus(item.status, item.priority);

    const body = fragment.querySelector('.schedule-body');
    body.appendChild(createDetailRow('カテゴリ', categories.find((c) => c.id === item.category)?.label));
    body.appendChild(createDetailRow('説明', item.description));
    body.appendChild(createExpectedStateBlock(item.expectedState));
    body.appendChild(createPreconditionBlock(item));

    const executionBlock = createExecutionBlock(item);
    if (executionBlock) {
      body.appendChild(executionBlock);
    }

    const actions = fragment.querySelector('.schedule-actions');
    populateScheduleActions(actions, item);

    container.appendChild(fragment);
  });
}

function translateStatus(status, priority) {
  const priorityLabel =
    priority === 'urgent'
      ? '（緊急）'
      : priority === 'high'
      ? '（高優先度）'
      : priority === 'medium'
      ? '（中優先度）'
      : '';
  switch (status) {
    case 'scheduled':
      return `予定済み${priorityLabel}`;
    case 'in_progress':
      return `実行中${priorityLabel}`;
    case 'completed':
      return '完了';
    case 'skipped':
      return 'スキップ';
    case 'failed':
      return '失敗';
    case 'cancelled':
      return 'キャンセル';
    case 'postponed':
      return `延期${priorityLabel}`;
    default:
      return status;
  }
}

function createDetailRow(label, value) {
  const div = document.createElement('div');
  div.className = 'schedule-detail-grid';
  const strong = document.createElement('strong');
  strong.textContent = label;
  const span = document.createElement('span');
  span.textContent = value || '-';
  div.appendChild(strong);
  div.appendChild(span);
  return div;
}

function createExpectedStateBlock(expected) {
  const wrapper = document.createElement('div');
  wrapper.className = 'expected-state';
  const title = document.createElement('h4');
  title.textContent = '期待状態';
  wrapper.appendChild(title);
  wrapper.appendChild(renderStateList(expected));
  return wrapper;
}

function createPreconditionBlock(item) {
  const wrapper = document.createElement('div');
  wrapper.className = 'expected-state';
  const title = document.createElement('h4');
  title.textContent = '前提条件チェック';
  wrapper.appendChild(title);
  const report = evaluatePreconditions(item.preconditions, appState.state);
  const summary = document.createElement('p');
  summary.textContent = report.total
    ? `適合率 ${Math.round((report.satisfied / report.total) * 100)}%`
    : '前提条件は設定されていません。';
  wrapper.appendChild(summary);

  if (report.details.length) {
    const list = document.createElement('ul');
    report.details.forEach((detail) => {
      const li = document.createElement('li');
      li.textContent = `${detail.subject}.${detail.field}: 要求=${formatRequirement(
        detail.required
      )} / 現在=${detail.actual ?? '未設定'} ${detail.passed ? '✅' : '⚠️'}`;
      list.appendChild(li);
    });
    wrapper.appendChild(list);
  }

  if (!report.passed && report.total) {
    const alternatives = suggestAlternativeTasks(item);
    if (alternatives.length) {
      const altList = document.createElement('p');
      altList.innerHTML = `代替候補: ${alternatives
        .slice(0, 3)
        .map((alt) => `${alt.icon} ${alt.title}`)
        .join(' / ')}`;
      wrapper.appendChild(altList);
    }
  }

  return wrapper;
}

function createExecutionBlock(item) {
  if (!item.executions.length) {
    return null;
  }
  const wrapper = document.createElement('div');
  wrapper.className = 'actual-state';
  const title = document.createElement('h4');
  title.textContent = '実行ログ';
  wrapper.appendChild(title);

  item.executions
    .slice()
    .reverse()
    .forEach((execution, index) => {
      const container = document.createElement('div');
      container.className = 'schedule-detail-grid';
      const label = index === 0 ? '最新' : `履歴${index + 1}`;
      container.appendChild(createDetailRow('ラベル', label));
      container.appendChild(
        createDetailRow('ステータス', translateExecutionStatus(execution.status))
      );
      if (execution.actualStart) {
        container.appendChild(
          createDetailRow('開始', new Date(execution.actualStart).toLocaleString())
        );
      }
      if (execution.actualEnd) {
        container.appendChild(
          createDetailRow('終了', new Date(execution.actualEnd).toLocaleString())
        );
      }
      if (execution.actualStateBefore) {
        container.appendChild(createDetailRow('実行前状態', summariseState(execution.actualStateBefore)));
      }
      if (execution.actualStateAfter) {
        container.appendChild(createDetailRow('実行後状態', summariseState(execution.actualStateAfter)));
      }
      if (execution.evaluation) {
        container.appendChild(
          createDetailRow(
            '評価',
            `一致率 ${execution.evaluation.score}% / 不一致:${execution.evaluation.mismatches.join(', ')}`
          )
        );
      }
      if (execution.notes) {
        container.appendChild(createDetailRow('メモ', execution.notes));
      }
      wrapper.appendChild(container);
    });

  return wrapper;
}

function translateExecutionStatus(status) {
  switch (status) {
    case 'in_progress':
      return '実行中';
    case 'completed':
      return '完了';
    case 'skipped':
      return 'スキップ';
    case 'failed':
      return '失敗';
    case 'interrupted':
      return '中断';
    default:
      return status;
  }
}

function populateScheduleActions(container, item) {
  container.innerHTML = '';
  if (item.status === 'scheduled' || item.status === 'postponed') {
    container.appendChild(createActionButton('開始', 'primary', () => handleStart(item.id)));
    container.appendChild(createActionButton('スキップ', 'secondary', () => handleSkip(item.id)));
    container.appendChild(createActionButton('キャンセル', 'danger', () => handleCancel(item.id)));
  } else if (item.status === 'in_progress') {
    container.appendChild(createActionButton('完了', 'primary', () => handleComplete(item.id)));
    container.appendChild(createActionButton('中断', 'secondary', () => handleInterrupt(item.id)));
    container.appendChild(createActionButton('失敗', 'danger', () => handleFail(item.id)));
  } else {
    container.appendChild(createActionButton('再スケジュール', 'secondary', () => handleReschedule(item.id)));
  }
}

function createActionButton(label, style, handler) {
  const button = document.createElement('button');
  button.textContent = label;
  button.className = style;
  button.addEventListener('click', handler);
  return button;
}

function handleStart(itemId) {
  const item = appState.scheduleItems.find((schedule) => schedule.id === itemId);
  if (!item) return;
  const report = evaluatePreconditions(item.preconditions, appState.state);
  if (!report.passed && report.total) {
    addNotification(
      `${item.title} の前提条件が満たされていません。${report.details
        .filter((detail) => !detail.passed)
        .map((detail) => `${detail.subject}.${detail.field}`)
        .join(', ')} を調整してください。`
    );
    const alternatives = suggestAlternativeTasks(item);
    if (alternatives.length) {
      addNotification(
        `代替タスク候補: ${alternatives
          .slice(0, 3)
          .map((alt) => `${alt.icon} ${alt.title}`)
          .join(' / ')}`
      );
    }
    if (!confirm('前提条件を満たしていません。強行実行しますか？')) {
      return;
    }
  }

  const execution = {
    id: generateId('exec'),
    status: 'in_progress',
    actualStart: new Date(),
    actualEnd: null,
    actualStateBefore: deepClone(appState.state),
    actualStateAfter: null,
    evaluation: null,
    notes: '',
    forced: !report.passed && report.total,
  };

  item.executions.push(execution);
  item.activeExecutionId = execution.id;
  item.status = 'in_progress';
  addNotification(`${item.title} の実行を開始しました。`);
  renderScheduleList();
}

function handleComplete(itemId) {
  const item = appState.scheduleItems.find((schedule) => schedule.id === itemId);
  if (!item) return;
  const execution = item.executions.find((exec) => exec.id === item.activeExecutionId);
  if (!execution) return;

  execution.status = 'completed';
  execution.actualEnd = new Date();
  execution.actualStateAfter = deepClone(appState.state);
  execution.evaluation = evaluateOutcome(item.expectedState?.After, execution.actualStateAfter);
  execution.notes = prompt('完了メモがあれば入力してください（任意）', '') || '';
  item.status = 'completed';
  item.activeExecutionId = null;

  if (execution.evaluation) {
    addNotification(
      `${item.title} を完了しました。期待状態との一致率は ${execution.evaluation.score}% です。`
    );
  } else {
    addNotification(`${item.title} を完了しました。`);
  }
  renderScheduleList();
}

function handleSkip(itemId) {
  const item = appState.scheduleItems.find((schedule) => schedule.id === itemId);
  if (!item) return;
  const reason = prompt('スキップ理由を記録してください', '前提条件が満たされない');
  item.executions.push({
    id: generateId('exec'),
    status: 'skipped',
    actualStart: null,
    actualEnd: null,
    actualStateBefore: deepClone(appState.state),
    actualStateAfter: null,
    evaluation: null,
    notes: reason || '',
  });
  item.status = 'skipped';
  addNotification(`${item.title} をスキップしました。理由: ${reason || '未記入'}`);
  renderScheduleList();
}

function handleCancel(itemId) {
  const item = appState.scheduleItems.find((schedule) => schedule.id === itemId);
  if (!item) return;
  if (!confirm('この予定をキャンセルしますか？')) return;
  item.status = 'cancelled';
  addNotification(`${item.title} をキャンセルしました。`);
  renderScheduleList();
}

function handleInterrupt(itemId) {
  const item = appState.scheduleItems.find((schedule) => schedule.id === itemId);
  if (!item) return;
  const execution = item.executions.find((exec) => exec.id === item.activeExecutionId);
  if (!execution) return;
  execution.status = 'interrupted';
  execution.actualEnd = new Date();
  item.status = 'postponed';
  item.activeExecutionId = null;
  addNotification(`${item.title} を一時中断しました。必要であれば再開してください。`);
  renderScheduleList();
}

function handleFail(itemId) {
  const item = appState.scheduleItems.find((schedule) => schedule.id === itemId);
  if (!item) return;
  const execution = item.executions.find((exec) => exec.id === item.activeExecutionId);
  if (!execution) return;
  execution.status = 'failed';
  execution.actualEnd = new Date();
  execution.actualStateAfter = deepClone(appState.state);
  execution.notes = prompt('失敗理由を記録してください', '') || '';
  item.status = 'failed';
  item.activeExecutionId = null;
  addNotification(`${item.title} の実行が失敗として記録されました。`);
  renderScheduleList();
}

function handleReschedule(itemId) {
  const item = appState.scheduleItems.find((schedule) => schedule.id === itemId);
  if (!item) return;
  const newTime = prompt('再スケジュール後の開始時刻 (HH:MM)', formatTime(item.scheduledStart));
  if (!newTime) return;
  const [hourStr, minuteStr] = newTime.split(':');
  const startHour = Number(hourStr);
  const startMinute = Number(minuteStr);
  if (
    Number.isNaN(startHour) ||
    Number.isNaN(startMinute) ||
    startHour < 0 ||
    startHour > 23 ||
    startMinute < 0 ||
    startMinute > 59
  ) {
    alert('開始時刻の形式が正しくありません。');
    return;
  }
  const duration = (item.scheduledEnd - item.scheduledStart) / (60 * 1000);
  item.scheduledStart = new Date(appState.currentDate);
  item.scheduledStart.setHours(startHour, startMinute, 0, 0);
  item.scheduledEnd = new Date(item.scheduledStart.getTime() + duration * 60 * 1000);
  item.status = 'scheduled';
  addNotification(`${item.title} を ${formatTimeRange(item.scheduledStart, item.scheduledEnd)} に再設定しました。`);
  appState.scheduleItems.sort((a, b) => a.scheduledStart - b.scheduledStart);
  renderScheduleList();
}

function createScheduleItem(template, startHour, startMinute, durationMinutes) {
  const scheduledStart = new Date(appState.currentDate);
  scheduledStart.setHours(startHour, startMinute, 0, 0);
  const scheduledEnd = new Date(scheduledStart.getTime() + durationMinutes * 60 * 1000);

  const scheduleItem = {
    id: generateId('schedule'),
    templateId: template.id,
    title: template.title,
    icon: template.icon,
    category: template.category,
    color: template.color,
    scheduledStart,
    scheduledEnd,
    status: 'scheduled',
    expectedState: deepClone(template.stateSignature),
    preconditions: deepClone(template.preconditions || {}),
    criticalStateRelation: deepClone(template.criticalStateRelation || {}),
    description: template.description,
    executions: [],
    priority: inferPriority(template.criticalStateRelation),
  };

  appState.scheduleItems.push(scheduleItem);
  appState.scheduleItems.sort((a, b) => a.scheduledStart - b.scheduledStart);
  addNotification(
    `${template.title} を ${formatTimeRange(scheduledStart, scheduledEnd)} に追加しました。`
  );
  renderScheduleList();
}

function evaluatePreconditions(preconditions = {}, state) {
  const details = [];
  let total = 0;
  let satisfied = 0;
  Object.entries(preconditions || {}).forEach(([subject, fields]) => {
    Object.entries(fields || {}).forEach(([field, requirement]) => {
      total += 1;
      const actual = state?.[subject]?.[field];
      const passed = Array.isArray(requirement)
        ? requirement.includes(actual)
        : requirement === actual;
      if (passed) {
        satisfied += 1;
      }
      details.push({ subject, field, required: requirement, actual, passed });
    });
  });
  return { details, total, satisfied, passed: total ? satisfied === total : true };
}

function renderStateList(state) {
  const list = document.createElement('ul');
  Object.entries(state || {}).forEach(([subject, fields]) => {
    Object.entries(fields || {}).forEach(([field, value]) => {
      const li = document.createElement('li');
      li.textContent = `${subject}.${field}: ${formatRequirement(value)}`;
      list.appendChild(li);
    });
  });
  return list;
}

function renderStateSummary(state) {
  if (!state) return '';
  const parts = [];
  Object.entries(state).forEach(([subject, fields]) => {
    Object.entries(fields || {}).forEach(([field, value]) => {
      parts.push(`${subject}.${field}: ${formatRequirement(value)}`);
    });
  });
  return parts.join('<br>');
}

function formatRequirement(value) {
  if (Array.isArray(value)) {
    return value.join(' / ');
  }
  if (value && typeof value === 'object') {
    return renderStateSummary(value);
  }
  return value ?? '未設定';
}

function evaluateOutcome(expectedAfter = {}, actualState = {}) {
  const details = [];
  let total = 0;
  let matches = 0;
  Object.entries(expectedAfter || {}).forEach(([subject, fields]) => {
    Object.entries(fields || {}).forEach(([field, expectedValue]) => {
      total += 1;
      const actual = actualState?.[subject]?.[field];
      const matched = expectedValue === actual;
      if (matched) {
        matches += 1;
      } else {
        details.push(`${subject}.${field}: ${actual ?? '未設定'} → ${expectedValue}`);
      }
    });
  });
  if (!total) {
    return null;
  }
  return {
    score: Math.round((matches / total) * 100),
    mismatches: details,
  };
}

function suggestAlternativeTasks(item) {
  const scored = taskTemplates
    .filter((template) => template.id !== item.templateId)
    .map((template) => {
      const report = evaluatePreconditions(template.preconditions, appState.state);
      const score = report.total ? report.satisfied / report.total : 1;
      return { template, score, passed: report.passed };
    })
    .filter((entry) => entry.score >= 0.5);
  scored.sort((a, b) => b.score - a.score);
  return scored.map((entry) => entry.template);
}

function summariseState(state) {
  const parts = [];
  Object.entries(state || {}).forEach(([subject, fields]) => {
    Object.entries(fields || {}).forEach(([field, value]) => {
      parts.push(`${subject}.${field}=${value}`);
    });
  });
  return parts.join(', ');
}

function renderNotificationList() {
  const container = document.getElementById('notification-list');
  container.innerHTML = '';
  const template = document.getElementById('notification-template');
  appState.notifications
    .slice()
    .reverse()
    .forEach((notification) => {
      const fragment = template.content.cloneNode(true);
      fragment.querySelector('time').textContent = notification.timestamp.toLocaleTimeString();
      fragment.querySelector('p').textContent = notification.message;
      container.appendChild(fragment);
    });
}

function addNotification(message) {
  appState.notifications.push({ message, timestamp: new Date() });
  if (appState.notifications.length > 50) {
    appState.notifications.shift();
  }
  renderNotificationList();
}

function formatDateInput(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(
    date.getDate()
  ).padStart(2, '0')}`;
}

function formatDateDisplay(date) {
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
}

function formatTime(date) {
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}

function formatTimeRange(start, end) {
  return `${formatTime(start)} - ${formatTime(end)}`;
}

function deepClone(value) {
  return value ? JSON.parse(JSON.stringify(value)) : value;
}

function generateId(prefix) {
  if (
    typeof globalThis !== 'undefined' &&
    globalThis.crypto &&
    typeof globalThis.crypto.randomUUID === 'function'
  ) {
    return globalThis.crypto.randomUUID();
  }
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1_000_000)}`;
}
