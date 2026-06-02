import * as vscode from "vscode";

export class SidebarProvider {
  private _panel: vscode.WebviewPanel | undefined;
  private readonly _extensionUri: vscode.Uri;

  constructor(extensionUri: vscode.Uri) {
    this._extensionUri = extensionUri;
  }

  public show(bug: {
    title: string;
    description: string;
    rootCause?: string;
    fixDescription?: string;
    fixedBy: string;
    date: string;
    severity?: string;
    language?: string;
  }) {
    if (this._panel) {
      this._panel.reveal(vscode.ViewColumn.Two);
    } else {
      this._panel = vscode.window.createWebviewPanel(
        "youseeitSidebar",
        "YouSeeIt — Bug Document",
        vscode.ViewColumn.Two,
        {
          enableScripts: true,
          localResourceRoots: [
            vscode.Uri.joinPath(this._extensionUri, "media"),
          ],
        },
      );

      this._panel.onDidDispose(() => {
        this._panel = undefined;
      });

      this._panel.webview.onDidReceiveMessage(async (message) => {
        if (message.command === "logBug") {
          await vscode.commands.executeCommand("youseeit.logBug", message.data);
        }
      });
    }

    this._panel.webview.html = this._getHtml(this._panel.webview, bug);
    this._panel.webview.postMessage({ command: "loadBug", bug });
  }

  private _getHtml(
    webview: vscode.Webview,
    bug: {
      title: string;
      description: string;
      rootCause?: string;
      fixDescription?: string;
      fixedBy: string;
      date: string;
      severity?: string;
      language?: string;
    },
  ): string {
    const styleUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "style.css"),
    );
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "main.js"),
    );

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="${styleUri}" rel="stylesheet">
    <title>YouSeeIt</title>
</head>
<body>
    <h2>🐛 YouSeeIt — Bug Document</h2>

    <div class="bug-card">
        <h3 id="bug-title">${bug.title}</h3>
        <div class="bug-field"><span>Description:</span> <span id="bug-description">${bug.description}</span></div>
        ${bug.rootCause ? `<div class="bug-field"><span>Root Cause:</span> <span id="bug-rootCause">${bug.rootCause}</span></div>` : ""}
        ${bug.fixDescription ? `<div class="bug-field"><span>Fix:</span> <span id="bug-fixDescription">${bug.fixDescription}</span></div>` : ""}
        <div class="bug-field"><span>Severity:</span> <span id="bug-severity">${bug.severity || "N/A"}</span></div>
        <div class="bug-field"><span>Language:</span> <span id="bug-language">${bug.language || "N/A"}</span></div>
        <div class="bug-field"><span>Fixed by:</span> <span id="bug-fixedBy">${bug.fixedBy}</span></div>
        <div class="bug-field"><span>Date:</span> <span id="bug-date">${bug.date}</span></div>
    </div>

    <button class="btn" id="log-btn">🪵 Log This Bug</button>

    <div id="bug-form" class="hidden" style="margin-top: 16px;">
        <div class="form-group">
            <label>Bug Title</label>
            <input type="text" id="title" placeholder="e.g. Null Pointer on Empty List" />
        </div>
        <div class="form-group">
            <label>Description</label>
            <textarea id="description" placeholder="What went wrong?"></textarea>
        </div>
        <div class="form-group">
            <label>Root Cause</label>
            <textarea id="rootCause" placeholder="Why did this happen?"></textarea>
        </div>
        <div class="form-group">
            <label>Fix Description</label>
            <textarea id="fixDescription" placeholder="What did you do to fix it?"></textarea>
        </div>
        <div class="form-group">
            <label>Severity</label>
            <select id="severity">
                <option value="low">Low</option>
                <option value="medium" selected>Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
            </select>
        </div>
        <button class="btn" id="submit-btn">Submit Bug</button>
    </div>

    <p class="success-msg hidden" id="success-msg">✅ Bug logged successfully!</p>

    <script src="${scriptUri}"></script>
</body>
</html>`;
  }
}
