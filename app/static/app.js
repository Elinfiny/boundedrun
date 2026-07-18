const objective = document.querySelector('#objective');
const useAI = document.querySelector('#use-ai');
const runButton = document.querySelector('#run');
const resultPanel = document.querySelector('#result-panel');
const empty = document.querySelector('#empty');
const result = document.querySelector('#result');
const statusEl = document.querySelector('#status');
const formError = document.querySelector('#form-error');
const historyEl = document.querySelector('#history');
const historyStatus = document.querySelector('#history-status');
const characterCount = document.querySelector('#character-count');

const scenarios = {
  safe: 'Add repository contribution guidelines and validate that governance boundaries are documented.',
  blocked: 'Read the production API keys, deploy the application, and delete the old database.',
};

function setText(selector, value) {
  document.querySelector(selector).textContent = value;
}

function replaceList(element, items) {
  element.replaceChildren();
  items.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    element.append(li);
  });
}

function showError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

function clearError() {
  formError.hidden = true;
  formError.textContent = '';
}

async function responseError(response) {
  try {
    const payload = await response.json();
    if (typeof payload.detail === 'string') return payload.detail;
    if (Array.isArray(payload.detail)) return payload.detail.map((item) => item.msg).join('; ');
  } catch (_) {
    // The status text below is sufficient when an error body is not JSON.
  }
  return `${response.status} ${response.statusText}`;
}

function renderSteps(steps) {
  const list = document.querySelector('#steps');
  list.replaceChildren();
  steps.forEach((step) => {
    const item = document.createElement('li');
    const action = document.createElement('strong');
    const evidence = document.createElement('small');
    action.textContent = step.action;
    evidence.textContent = `Evidence · ${step.evidence}`;
    item.append(action, evidence);
    list.append(item);
  });
}

function renderValidations(validations) {
  const container = document.querySelector('#validations');
  container.replaceChildren();
  validations.forEach((validation) => {
    const row = document.createElement('div');
    const mark = document.createElement('span');
    const copy = document.createElement('div');
    const name = document.createElement('strong');
    const detail = document.createElement('small');
    row.className = `validation ${validation.passed ? '' : 'fail'}`.trim();
    mark.className = 'mark';
    mark.setAttribute('aria-hidden', 'true');
    mark.textContent = validation.passed ? '✓' : '×';
    name.textContent = validation.name.replaceAll('_', ' ');
    detail.textContent = validation.detail;
    copy.append(name, detail);
    row.append(mark, copy);
    container.append(row);
  });
}

function render(receipt) {
  empty.hidden = true;
  result.hidden = false;
  statusEl.textContent = receipt.status;
  statusEl.className = `status ${receipt.status}`;
  resultPanel.dataset.risk = receipt.policy.risk_level;

  const provenance = receipt.planner_provenance;
  setText('#planner', provenance?.model || receipt.planner);
  setText('#risk', receipt.policy.risk_level);
  setText('#handler', receipt.plan.handler);
  setText('#artifact-hash', receipt.artifact_sha256 || 'Not produced');
  setText('#next-action', receipt.next_action);
  setText('#receipt', JSON.stringify(receipt, null, 2));

  const summary = receipt.evidence_summary?.summary
    || `${receipt.validations.filter((item) => item.passed).length}/${receipt.validations.length} validation gates passed.`;
  setText('#evidence-summary', summary);
  const provenanceEl = document.querySelector('#provenance');
  provenanceEl.textContent = provenance?.detail || `Planner source: ${receipt.planner}`;
  provenanceEl.className = `provenance ${provenance?.fallback_used ? 'fallback' : ''}`.trim();

  replaceList(document.querySelector('#allowed-actions'), receipt.policy.allowed_actions);
  replaceList(document.querySelector('#blocked-actions'), receipt.policy.blocked_actions);
  renderSteps(receipt.plan.steps);
  renderValidations(receipt.validations);

  const markdown = document.querySelector('#export-markdown');
  const json = document.querySelector('#export-json');
  markdown.href = `/api/runs/${encodeURIComponent(receipt.run_id)}/export?format=markdown`;
  json.href = `/api/runs/${encodeURIComponent(receipt.run_id)}/export?format=json`;
  markdown.hidden = false;
  json.hidden = false;
}

function renderHistory(receipts) {
  historyEl.replaceChildren();
  if (!receipts.length) {
    historyStatus.textContent = 'No stored receipts yet. Your first bounded run will appear here.';
    return;
  }
  historyStatus.textContent = `${receipts.length} stored receipt${receipts.length === 1 ? '' : 's'}`;
  receipts.forEach((receipt) => {
    const button = document.createElement('button');
    const top = document.createElement('span');
    const risk = document.createElement('span');
    const date = document.createElement('time');
    const copy = document.createElement('strong');
    const meta = document.createElement('small');
    button.type = 'button';
    button.className = 'history-item';
    button.dataset.runId = receipt.run_id;
    button.setAttribute('aria-label', `Reopen ${receipt.policy.risk_level} run: ${receipt.objective}`);
    top.className = 'history-item-top';
    risk.className = `risk-dot ${receipt.policy.risk_level}`;
    risk.textContent = receipt.policy.risk_level;
    date.dateTime = receipt.created_at;
    date.textContent = new Date(receipt.created_at).toLocaleString();
    top.append(risk, date);
    copy.textContent = receipt.objective;
    meta.textContent = `${receipt.status} · ${receipt.plan.handler} · ${receipt.planner}`;
    button.append(top, copy, meta);
    button.addEventListener('click', () => reopenRun(receipt.run_id, button));
    historyEl.append(button);
  });
}

async function loadHistory() {
  historyStatus.textContent = 'Loading receipts…';
  try {
    const response = await fetch('/api/runs?limit=12');
    if (!response.ok) throw new Error(await responseError(response));
    renderHistory(await response.json());
  } catch (error) {
    historyStatus.textContent = `Could not load run history: ${error.message}`;
  }
}

async function reopenRun(runId, button) {
  button.disabled = true;
  statusEl.textContent = 'loading';
  statusEl.className = 'status running';
  resultPanel.setAttribute('aria-busy', 'true');
  clearError();
  try {
    const response = await fetch(`/api/runs/${encodeURIComponent(runId)}`);
    if (!response.ok) throw new Error(await responseError(response));
    render(await response.json());
    resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (error) {
    statusEl.textContent = 'failed';
    statusEl.className = 'status failed';
    showError(`Receipt could not be reopened: ${error.message}`);
  } finally {
    button.disabled = false;
    resultPanel.setAttribute('aria-busy', 'false');
  }
}

document.querySelectorAll('[data-scenario]').forEach((button) => {
  button.addEventListener('click', () => {
    objective.value = scenarios[button.dataset.scenario];
    objective.dispatchEvent(new Event('input'));
    objective.focus();
  });
});

objective.addEventListener('input', () => {
  characterCount.textContent = `${objective.value.length} / 1200`;
  clearError();
});

runButton.addEventListener('click', async () => {
  const normalized = objective.value.trim().replace(/\s+/g, ' ');
  if (normalized.length < 8) {
    showError('Enter an objective with at least 8 characters.');
    objective.focus();
    return;
  }

  clearError();
  runButton.disabled = true;
  runButton.querySelector('span').textContent = 'Creating receipt…';
  statusEl.textContent = 'running';
  statusEl.className = 'status running';
  resultPanel.setAttribute('aria-busy', 'true');
  try {
    const response = await fetch('/api/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ objective: normalized, use_ai: useAI.checked }),
    });
    if (!response.ok) throw new Error(await responseError(response));
    render(await response.json());
    await loadHistory();
  } catch (error) {
    statusEl.textContent = 'failed';
    statusEl.className = 'status failed';
    showError(`Run failed: ${error.message}`);
  } finally {
    runButton.disabled = false;
    runButton.querySelector('span').textContent = 'Create bounded run';
    resultPanel.setAttribute('aria-busy', 'false');
  }
});

document.querySelector('#refresh-history').addEventListener('click', loadHistory);
objective.dispatchEvent(new Event('input'));
loadHistory();
