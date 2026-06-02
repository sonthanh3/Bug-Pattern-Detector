import * as vscode from "vscode";
import { SidebarProvider } from "./sidebarProvider";
import { checkFile, learnBug, getBug, BugMatch } from "./checkService";
import { execSync } from "child_process";

function getGitUsername(): string {
  try {
    return execSync("git config user.name").toString().trim();
  } catch {
    return "Unknown";
  }
}

export function activate(context: vscode.ExtensionContext) {
  console.log("YouSeeIt is now active.");

  // ─── DiagnosticCollection ───
  const diagnostics = vscode.languages.createDiagnosticCollection("youseeit");
  context.subscriptions.push(diagnostics);

  // ─── Sidebar provider ───
  const sidebarProvider = new SidebarProvider(context.extensionUri);

  // ─── Debounce timer ───
  let debounceTimer: ReturnType<typeof setTimeout> | undefined;

  // ─── Track current matches for hover ───
  let currentMatches: BugMatch[] = [];

  // ─── Apply diagnostics from backend response ───
  function applyMatches(document: vscode.TextDocument, matches: BugMatch[]) {
    const diagList: vscode.Diagnostic[] = matches
      .map((match) => {
        if (document.lineCount <= match.line) {
          return null;
        }
        const lineText = document.lineAt(match.line).text;
        const range = new vscode.Range(
          match.line,
          0,
          match.line,
          lineText.length,
        );
        const diagnostic = new vscode.Diagnostic(
          range,
          `YouSeeIt: ${match.title} — ${match.description}`,
          vscode.DiagnosticSeverity.Warning,
        );
        diagnostic.source = "YouSeeIt";
        return diagnostic;
      })
      .filter((d): d is vscode.Diagnostic => d !== null);

    diagnostics.set(document.uri, diagList);
  }

  // ─── Call backend on save with debounce ───
  const saveListener = vscode.workspace.onDidSaveTextDocument(
    async (document) => {
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }
      debounceTimer = setTimeout(async () => {
        const content = document.getText();
        const matches = await checkFile(content);
        currentMatches = matches;
        applyMatches(document, matches);
      }, 2000);
    },
  );
  context.subscriptions.push(saveListener);

  // ─── Hover tooltip ───
  context.subscriptions.push(
    vscode.languages.registerHoverProvider(
      { scheme: "file" },
      {
        provideHover(document, position) {
          const match = currentMatches.find((m) => m.line === position.line);
          if (match) {
            const tooltip = new vscode.MarkdownString();
            tooltip.appendMarkdown(`### 🐛 YouSeeIt Warning\n\n`);
            tooltip.appendMarkdown(`**Bug:** ${match.title}\n\n`);
            tooltip.appendMarkdown(
              `**What happened:** ${match.description}\n\n`,
            );
            tooltip.appendMarkdown(`**Fixed by:** ${match.fixedBy}\n\n`);
            tooltip.appendMarkdown(`**Date:** ${match.date}\n\n`);
            tooltip.appendMarkdown(`**Confidence:** ${match.confidence}%\n\n`);
            tooltip.appendMarkdown(
              `[📄 View full document](command:youseeit.openSidebar)`,
            );
            tooltip.isTrusted = true;
            return new vscode.Hover(tooltip);
          }
        },
      },
    ),
  );

  // ─── Open sidebar with real bug data from database ───
  context.subscriptions.push(
    vscode.commands.registerCommand("youseeit.openSidebar", async () => {
      const match = currentMatches[0];
      if (match) {
        // Fetch full bug document from GET /bugs/:id
        const bugDoc = await getBug(match.bugId);
        if (bugDoc) {
          sidebarProvider.show({
            title: bugDoc.title,
            description: bugDoc.description,
            rootCause: bugDoc.root_cause,
            fixDescription: bugDoc.fix_description,
            fixedBy: bugDoc.resolved_by,
            date: bugDoc.resolved_at,
            severity: bugDoc.severity,
            language: bugDoc.language,
          });
        } else {
          // Fallback to match data
          sidebarProvider.show({
            title: match.title,
            description: match.description,
            fixedBy: match.fixedBy,
            date: match.date,
          });
        }
      } else {
        vscode.window.showInformationMessage("No bug matches found yet.");
      }
    }),
  );

  // ─── Handle Log This Bug form submission ───
  context.subscriptions.push(
    vscode.commands.registerCommand("youseeit.logBug", async (payload: any) => {
      const editor = vscode.window.activeTextEditor;
      const fixedBy = getGitUsername();
      const filePath = editor?.document.fileName;
      const language = editor?.document.languageId;

      const message = await learnBug({
        ...payload,
        fixedBy,
        filePath,
        language,
      });

      vscode.window.showInformationMessage(`✅ ${message}`);
    }),
  );

  // ─── Hello World command ───
  context.subscriptions.push(
    vscode.commands.registerCommand("youseeit.helloWorld", () => {
      vscode.window.showInformationMessage("YouSeeIt is watching your code.");
    }),
  );
}

export function deactivate() {}
