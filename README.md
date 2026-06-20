# Bug Pattern Detector

A VS Code extension that allow AI to learn and doc bug pattern into log and warn the next SDE in future if that bug happens agian. SDE will have clear reference to solve. 

## Features

- Red underline on lines matching known bug patterns
- Hover tooltip showing bug title, description, fixer, and confidence score
- Sidebar panel with full bug document
- "Log This Bug" form to teach the system new bugs
- AI-powered similarity search using sentence-transformers

## How It Works

1. Senior developer fixes a bug and clicks "Log This Bug"
2. The system learns the bug pattern using AI embeddings
3. When any developer writes similar code, a red underline appears
4. Hovering shows the bug details and a link to the full document

## Requirements

- Backend server running on http://127.0.0.1:8000
- PostgreSQL database with bugs table

## Extension Settings

previously named as 'You See It'

- Backend URL: `http://127.0.0.1:8000`
