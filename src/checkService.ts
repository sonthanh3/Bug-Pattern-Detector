import axios from "axios";

const BACKEND_URL = "http://127.0.0.1:8000";
const TEAM_TOKEN = "youseeit-dev-token";

const headers = {
  Authorization: `Bearer ${TEAM_TOKEN}`,
};

export interface BugMatch {
  line: number;
  bugId: string;
  title: string;
  description: string;
  fixedBy: string;
  date: string;
  score: number;
  confidence: number;
}

export interface BugDocument {
  id: string;
  title: string;
  description: string;
  root_cause: string;
  fix_description: string;
  severity: string;
  resolved_by: string;
  resolved_at: string;
  language: string;
  file_path: string;
  occurrence_count: number;
}

export interface LearnPayload {
  title: string;
  description: string;
  rootCause: string;
  fixDescription: string;
  severity: string;
  fixedBy: string;
  filePath?: string;
  language?: string;
}

export async function checkFile(content: string): Promise<BugMatch[]> {
  try {
    console.log("YouSeeIt: calling /check...");
    const response = await axios.post(
      `${BACKEND_URL}/check`,
      { content },
      { headers },
    );
    console.log(
      "YouSeeIt: /check response:",
      response.data.matches.length,
      "matches",
    );
    return response.data.matches;
  } catch (error) {
    console.error("YouSeeIt: backend unreachable", error);
    return [];
  }
}

export async function learnBug(payload: LearnPayload): Promise<string> {
  try {
    const response = await axios.post(`${BACKEND_URL}/learn`, payload, {
      headers,
    });
    return response.data.message;
  } catch (error) {
    console.error("YouSeeIt: failed to learn bug", error);
    return "Failed to log bug.";
  }
}

export async function getBug(bugId: string): Promise<BugDocument | null> {
  try {
    const response = await axios.get(`${BACKEND_URL}/bugs/${bugId}`, {
      headers,
    });
    return response.data;
  } catch (error) {
    console.error("YouSeeIt: failed to fetch bug", error);
    return null;
  }
}

export async function getBugs(): Promise<BugDocument[]> {
  try {
    const response = await axios.get(`${BACKEND_URL}/bugs`, { headers });
    return response.data.bugs;
  } catch (error) {
    console.error("YouSeeIt: failed to fetch bugs", error);
    return [];
  }
}
