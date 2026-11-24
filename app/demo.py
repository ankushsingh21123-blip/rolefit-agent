"""Self-contained demo page (no build step, no JavaScript framework).

A small chat UI that talks to POST /chat and renders the ranked jobs
with their plain-words reasons. Served at GET /demo.
"""

DEMO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RoleFit Agent — demo</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }
  h1 { font-size: 1.4rem; }
  .muted { color: #666; font-size: .9rem; }
  #log { border: 1px solid #ddd; border-radius: 8px; padding: 1rem; min-height: 200px; margin: 1rem 0; }
  .msg { margin: .6rem 0; line-height: 1.45; white-space: pre-wrap; }
  .msg.user { text-align: right; color: #144a75; }
  .job { border: 1px solid #e3e3e3; border-radius: 6px; padding: .6rem .8rem; margin: .5rem 0; }
  .job b { font-size: .95rem; }
  .job .meta { color: #555; font-size: .85rem; }
  .job .why { color: #2a6b34; font-size: .88rem; margin-top: .2rem; }
  form { display: flex; gap: .5rem; }
  input { flex: 1; padding: .6rem; font-size: 1rem; border: 1px solid #bbb; border-radius: 6px; }
  button { padding: .6rem 1rem; font-size: 1rem; border-radius: 6px; border: none; background: #144a75; color: #fff; cursor: pointer; }
  .try { margin: .4rem .2rem .4rem 0; padding: .3rem .6rem; font-size: .85rem; border-radius: 20px; border: 1px solid #bbb; background: #f6f6f6; cursor: pointer; }
</style>
</head>
<body>
<h1>RoleFit Agent</h1>
<p class="muted">Tell me what kind of work you want — and what you'd never take — in plain words. I remember what you say across turns and match you to roles from a demo index of 30 fictional listings.</p>
<div>
  <button class="try" data-q="I want a remote Python backend job, at least ₹40,000 a month. I never want night shifts.">remote Python backend, ₹40k+, no nights</button>
  <button class="try" data-q="I want a part-time data analyst job in Bengaluru. I know SQL and Excel.">part-time data analyst, Bengaluru</button>
  <button class="try" data-q="I'm looking for a design internship. I know Figma. Remote or Bengaluru works.">design internship, Figma</button>
</div>
<div id="log"></div>
<form id="form"><input id="input" placeholder="e.g. I want a React job in Hyderabad, part-time…" autocomplete="off"><button type="submit">Send</button></form>
<p class="muted" id="providers"></p>
<script>
  let sessionId = null;
  const log = document.getElementById('log');
  const input = document.getElementById('input');
  function add(text, cls) {
    const div = document.createElement('div');
    div.className = 'msg ' + cls;
    div.textContent = text;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }
  function addJobs(jobs) {
    jobs.forEach(j => {
      const div = document.createElement('div');
      div.className = 'job';
      const salary = '₹' + j.job.salary_min.toLocaleString('en-IN') + '–₹' + j.job.salary_max.toLocaleString('en-IN') + ' / month';
      div.innerHTML = '<b></b><div class="meta"></div><div class="why"></div>';
      div.querySelector('b').textContent = j.job.title + ' at ' + j.job.company;
      div.querySelector('.meta').textContent = j.job.location + ' · ' + j.job.work_mode + ' · ' + j.job.employment_type + ' · ' + salary + ' · score ' + j.score.toFixed(2);
      div.querySelector('.why').textContent = j.reasons.join('; ') || 'Good match';
      log.appendChild(div);
    });
  }
  async function send(text) {
    add(text, 'user');
    input.value = '';
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text, session_id: sessionId})
    });
    const data = await res.json();
    sessionId = data.session_id;
    add(data.reply, 'agent');
    addJobs(data.jobs);
    document.getElementById('providers').textContent =
      'LLM: ' + data.llm_provider + ' · embeddings: ' + data.embedding_provider + ' · store: ' + data.store;
  }
  document.getElementById('form').addEventListener('submit', e => {
    e.preventDefault();
    if (input.value.trim()) send(input.value.trim());
  });
  document.querySelectorAll('.try').forEach(b =>
    b.addEventListener('click', () => send(b.dataset.q)));
</script>
</body>
</html>
"""
