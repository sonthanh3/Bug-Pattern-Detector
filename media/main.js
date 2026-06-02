const vscode = acquireVsCodeApi();

const logBtn = document.getElementById("log-btn");
const form = document.getElementById("bug-form");
const submitBtn = document.getElementById("submit-btn");
const successMsg = document.getElementById("success-msg");

// Show form when "Log This Bug" is clicked
logBtn.addEventListener("click", () => {
  form.classList.toggle("hidden");
});

// Submit form
submitBtn.addEventListener("click", () => {
  const payload = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value,
    rootCause: document.getElementById("rootCause").value,
    fixDescription: document.getElementById("fixDescription").value,
    severity: document.getElementById("severity").value,
  };

  // Send to extension (Week 5: extension forwards to POST /learn)
  vscode.postMessage({ command: "logBug", data: payload });

  form.classList.add("hidden");
  successMsg.classList.remove("hidden");

  setTimeout(() => successMsg.classList.add("hidden"), 3000);
});

// Receive bug data from extension
window.addEventListener("message", (event) => {
  const message = event.data;
  if (message.command === "loadBug") {
    const bug = message.bug;
    document.getElementById("bug-title").textContent = bug.title;
    document.getElementById("bug-description").textContent = bug.description;
    document.getElementById("bug-fixedBy").textContent = bug.fixedBy;
    document.getElementById("bug-date").textContent = bug.date;
    // Pre-fill form
    document.getElementById("title").value = bug.title;
    document.getElementById("description").value = bug.description;
  }
});
