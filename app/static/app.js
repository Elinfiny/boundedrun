const objective = document.querySelector('#objective');
const useAI = document.querySelector('#use-ai');
const runButton = document.querySelector('#run');
const empty = document.querySelector('#empty');
const result = document.querySelector('#result');
const statusEl = document.querySelector('#status');

const scenarios = {
  safe: 'Add repository contribution guidelines and validate that governance boundaries are documented.',
  blocked: 'Read the production API keys, deploy the application, and delete the old database.',
};

document.querySelectorAll('[data-scenario]').forEach((button) => {
  button.addEventListener('click', () => { objective.value = scenarios[button.dataset.scenario]; });
});

function render(receipt) {
  empty.hidden = true;
  result.hidden = false;
  statusEl.textContent = receipt.status;
  statusEl.className = `status ${receipt.status}`;
  document.querySelector('#planner').textContent = receipt.planner;
  document.querySelector('#risk').textContent = receipt.policy.risk_level;
  document.querySelector('#handler').textContent = receipt.plan.handler;
  document.querySelector('#steps').innerHTML = receipt.plan.steps
    .map((step) => `<li><strong>${step.action}</strong><br><small>${step.evidence}</small></li>`)
    .join('');
  document.querySelector('#validations').innerHTML = receipt.validations
    .map((item) => `<div class="validation ${item.passed ? '' : 'fail'}"><span class="mark">${item.passed ? '✓' : '×'}</span><div><strong>${item.name}</strong><small>${item.detail}</small></div></div>`)
    .join('');
  document.querySelector('#next-action').textContent = receipt.next_action;
  document.querySelector('#receipt').textContent = JSON.stringify(receipt, null, 2);
}

runButton.addEventListener('click', async () => {
  runButton.disabled = true;
  statusEl.textContent = 'running';
  statusEl.className = 'status';
  try {
    const response = await fetch('/api/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ objective: objective.value, use_ai: useAI.checked }),
    });
    if (!response.ok) throw new Error(await response.text());
    render(await response.json());
  } catch (error) {
    statusEl.textContent = 'failed';
    statusEl.className = 'status failed';
    alert(`Run failed: ${error.message}`);
  } finally {
    runButton.disabled = false;
  }
});
