"""
OWASP LLM Agent Reviewer — Web Portal
Run:  python app.py
Open: http://localhost:5000
"""

import anthropic
import os
from flask import Flask, request, Response, stream_with_context, render_template_string

from review_agent import SYSTEM_PROMPT, SUPPORTED_EXTENSIONS

app = Flask(__name__)

# ---------------------------------------------------------------------------
# HTML / CSS / JS  (single-file, no templates folder needed)
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OWASP LLM Agent Reviewer</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      background: #1a1d2e;
      border-bottom: 1px solid #2d3148;
      padding: 1rem 2rem;
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    header h1 { font-size: 1.2rem; font-weight: 600; }
    header .badge {
      background: #e53e3e;
      color: #fff;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
      letter-spacing: 0.05em;
    }
    header .readme-btn {
      margin-left: auto;
      background: none;
      border: 1px solid #2d3148;
      border-radius: 6px;
      color: #94a3b8;
      cursor: pointer;
      font-size: 0.82rem;
      padding: 4px 12px;
      transition: border-color 0.15s, color 0.15s;
    }
    header .readme-btn:hover { border-color: #4f6ef7; color: #e2e8f0; }

    /* README modal */
    .modal-overlay {
      display: none;
      position: fixed; inset: 0;
      background: rgba(0,0,0,0.65);
      z-index: 100;
      align-items: center;
      justify-content: center;
    }
    .modal-overlay.open { display: flex; }
    .modal {
      background: #1a1d2e;
      border: 1px solid #2d3148;
      border-radius: 10px;
      max-width: 640px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
      padding: 2rem;
    }
    .modal h2 { font-size: 1.1rem; margin-bottom: 1.2rem; color: #e2e8f0; }
    .modal h3 { font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.06em; color: #94a3b8; margin: 1.2rem 0 0.4rem; }
    .modal p, .modal li { font-size: 0.88rem; line-height: 1.7; color: #cbd5e1; }
    .modal ul { padding-left: 1.4rem; }
    .modal li { margin-bottom: 0.25rem; }
    .modal code {
      background: #0f1117;
      border-radius: 4px;
      padding: 1px 6px;
      font-family: Consolas, monospace;
      font-size: 0.82em;
      color: #7dd3fc;
    }
    .modal .close-btn {
      display: block;
      margin-top: 1.5rem;
      margin-left: auto;
      background: #4f6ef7;
      border: none;
      border-radius: 6px;
      color: #fff;
      cursor: pointer;
      font-size: 0.9rem;
      padding: 0.5rem 1.2rem;
    }
    .modal .close-btn:hover { background: #3b55d9; }

    main {
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0;
    }

    /* ---- LEFT PANEL ---- */
    .panel-left {
      border-right: 1px solid #2d3148;
      display: flex;
      flex-direction: column;
      padding: 1.5rem;
      gap: 1rem;
    }

    label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; }

    input[type="text"] {
      background: #1a1d2e;
      border: 1px solid #2d3148;
      border-radius: 6px;
      color: #e2e8f0;
      padding: 0.5rem 0.75rem;
      font-size: 0.9rem;
      width: 100%;
    }
    input[type="text"]:focus { outline: none; border-color: #4f6ef7; }

    textarea#code {
      flex: 1;
      background: #1a1d2e;
      border: 1px solid #2d3148;
      border-radius: 6px;
      color: #c9d1e0;
      font-family: "Fira Code", "Cascadia Code", Consolas, monospace;
      font-size: 0.82rem;
      line-height: 1.6;
      padding: 0.75rem;
      resize: none;
      min-height: 420px;
    }
    textarea#code:focus { outline: none; border-color: #4f6ef7; }

    button#submit-btn {
      background: #4f6ef7;
      border: none;
      border-radius: 6px;
      color: #fff;
      cursor: pointer;
      font-size: 0.95rem;
      font-weight: 600;
      padding: 0.65rem 1.5rem;
      transition: background 0.15s;
      align-self: flex-end;
      width: 100%;
    }
    button#submit-btn:hover:not(:disabled) { background: #3b55d9; }
    button#submit-btn:disabled { opacity: 0.55; cursor: not-allowed; }

    /* ---- RIGHT PANEL ---- */
    .panel-right {
      display: flex;
      flex-direction: column;
      padding: 1.5rem;
      gap: 0.75rem;
      overflow-y: auto;
    }

    .panel-right h2 { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; }

    #output {
      flex: 1;
      background: #1a1d2e;
      border: 1px solid #2d3148;
      border-radius: 6px;
      padding: 1rem 1.25rem;
      overflow-y: auto;
      min-height: 420px;
      font-size: 0.88rem;
      line-height: 1.7;
    }

    #output .placeholder { color: #475569; font-style: italic; }

    /* Markdown rendering inside #output */
    #output h1, #output h2 { color: #e2e8f0; margin-top: 1.2rem; margin-bottom: 0.4rem; }
    #output h3 { color: #93c5fd; margin-top: 1rem; margin-bottom: 0.3rem; }
    #output strong { color: #f0abfc; }
    #output ul, #output ol { padding-left: 1.4rem; }
    #output li { margin-bottom: 0.2rem; }
    #output code {
      background: #0f1117;
      border-radius: 4px;
      padding: 1px 5px;
      font-family: Consolas, monospace;
      font-size: 0.82em;
      color: #7dd3fc;
    }
    #output pre { background: #0f1117; border-radius: 6px; padding: 0.75rem; overflow-x: auto; margin: 0.5rem 0; }
    #output pre code { background: none; padding: 0; }
    #output hr { border: none; border-top: 1px solid #2d3148; margin: 1rem 0; }

    .status-bar {
      font-size: 0.78rem;
      color: #64748b;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .spinner {
      width: 12px; height: 12px;
      border: 2px solid #4f6ef7;
      border-top-color: transparent;
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
      display: none;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>

<header>
  <h1>OWASP LLM Agent Reviewer</h1>
  <span class="badge">Top 10 · 2025</span>
  <button class="readme-btn" onclick="document.getElementById('readme-modal').classList.add('open')">README</button>
</header>

<!-- README modal -->
<div class="modal-overlay" id="readme-modal" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="modal">
    <h2>OWASP LLM Agent Reviewer</h2>

    <h3>What it does</h3>
    <p>Paste agent source code or a config file and this tool analyses it against all ten categories of the <strong>OWASP Top 10 for Large Language Model Applications (2025 edition)</strong>. Each category receives a <code>PASS</code>, <code>FAIL</code>, <code>PARTIAL</code>, or <code>N/A</code> status with specific findings and remediation advice. The review closes with an overall risk rating and a prioritised fix list.</p>

    <h3>How to use</h3>
    <ul>
      <li>Optionally enter a <strong>filename</strong> (e.g. <code>my_agent.py</code>) — helps Claude give more precise feedback.</li>
      <li>Paste your <strong>agent code or config</strong> into the text area.</li>
      <li>Click <strong>Review Agent</strong> or press <kbd>Ctrl+Enter</kbd>.</li>
      <li>The analysis streams in real time on the right panel.</li>
    </ul>

    <h3>Supported file types</h3>
    <p><code>.py</code> · <code>.js</code> · <code>.ts</code> · <code>.json</code> · <code>.yaml</code> · <code>.yml</code> · <code>.txt</code> · <code>.md</code></p>

    <h3>OWASP categories assessed</h3>
    <ul>
      <li><strong>LLM01</strong> – Prompt Injection</li>
      <li><strong>LLM02</strong> – Sensitive Information Disclosure</li>
      <li><strong>LLM03</strong> – Supply Chain</li>
      <li><strong>LLM04</strong> – Data and Model Poisoning</li>
      <li><strong>LLM05</strong> – Improper Output Handling</li>
      <li><strong>LLM06</strong> – Excessive Agency</li>
      <li><strong>LLM07</strong> – System Prompt Leakage</li>
      <li><strong>LLM08</strong> – Vector and Embedding Weaknesses</li>
      <li><strong>LLM09</strong> – Misinformation</li>
      <li><strong>LLM10</strong> – Unbounded Consumption</li>
    </ul>

    <h3>Running locally</h3>
    <p>Requires <code>ANTHROPIC_API_KEY</code> set in the environment and <code>pip install anthropic flask</code>. Start with <code>python app.py</code>; port defaults to <code>5000</code> (override with <code>PORT</code> env var).</p>

    <button class="close-btn" onclick="document.getElementById('readme-modal').classList.remove('open')">Close</button>
  </div>
</div>

<main>
  <!-- LEFT: input -->
  <div class="panel-left">
    <div>
      <label for="filename">Filename (optional)</label>
      <input type="text" id="filename" placeholder="e.g. my_agent.py" />
    </div>

    <div style="flex:1; display:flex; flex-direction:column; gap:0.4rem;">
      <label for="code">Agent source code / config</label>
      <textarea id="code" placeholder="Paste your agent code here…
Supported: .py · .js · .ts · .json · .yaml · .yml"></textarea>
    </div>

    <div style="display:flex; gap:0.5rem;">
      <button id="submit-btn" onclick="startReview()" style="flex:1;">Review Agent</button>
      <button onclick="document.getElementById('readme-modal').classList.add('open')" style="background:none; border:1px solid #2d3148; border-radius:6px; color:#94a3b8; cursor:pointer; font-size:0.82rem; padding:0 1rem; white-space:nowrap; transition:border-color 0.15s,color 0.15s;" onmouseover="this.style.borderColor='#4f6ef7';this.style.color='#e2e8f0'" onmouseout="this.style.borderColor='#2d3148';this.style.color='#94a3b8'">README</button>
    </div>
  </div>

  <!-- RIGHT: output -->
  <div class="panel-right">
    <h2>OWASP LLM Top 10 Analysis</h2>
    <div id="output">
      <p class="placeholder">Your security analysis will appear here.</p>
    </div>
    <div class="status-bar">
      <div class="spinner" id="spinner"></div>
      <span id="status">Ready</span>
    </div>
  </div>
</main>

<script>
  let rawMarkdown = "";

  async function startReview() {
    const code = document.getElementById("code").value.trim();
    if (!code) { alert("Please paste some agent code first."); return; }

    const filename = document.getElementById("filename").value.trim() || "pasted_code";
    const btn = document.getElementById("submit-btn");
    const output = document.getElementById("output");
    const spinner = document.getElementById("spinner");
    const status = document.getElementById("status");

    btn.disabled = true;
    spinner.style.display = "inline-block";
    status.textContent = "Analysing…";
    rawMarkdown = "";
    output.innerHTML = "";

    try {
      const response = await fetch("/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, filename }),
      });

      if (!response.ok) {
        const err = await response.text();
        output.innerHTML = `<p style="color:#f87171">Error: ${err}</p>`;
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        rawMarkdown += decoder.decode(value, { stream: true });
        output.innerHTML = marked.parse(rawMarkdown);
        output.scrollTop = output.scrollHeight;
      }

      status.textContent = "Review complete";
    } catch (e) {
      output.innerHTML = `<p style="color:#f87171">Request failed: ${e.message}</p>`;
      status.textContent = "Error";
    } finally {
      btn.disabled = false;
      spinner.style.display = "none";
    }
  }

  // Ctrl+Enter to submit
  document.getElementById("code").addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "Enter") startReview();
  });
</script>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/review", methods=["POST"])
def review():
    data = request.get_json(silent=True) or {}
    code_text = data.get("code", "").strip()
    filename = data.get("filename", "pasted_code").strip() or "pasted_code"

    if not code_text:
        return "No code provided.", 400

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "ANTHROPIC_API_KEY environment variable is not set.", 500

    def generate():
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Please review the following agent code/config for OWASP LLM Top 10 compliance.\n"
                        f"Filename: {filename}\n\n"
                        f"```\n{code_text}\n```"
                    ),
                }
            ],
        ) as stream:
            for text in stream.text_stream:
                yield text

    return Response(stream_with_context(generate()), mimetype="text/plain")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting OWASP LLM Agent Reviewer on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
