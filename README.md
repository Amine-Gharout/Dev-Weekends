# DevLog - Developer's Micro-Journal & Productivity Tracker

DevLog is a lightweight, interactive Command-Line Interface (CLI) application built exclusively in pure Python. It helps developers maintain a micro-journal of their daily coding activities and easily generate categorized standup notes.

## 📋 Prerequisites

- **Python 3.x** must be installed on your machine.
- **Zero Dependencies**: There are no third-party (`pip`) packages required. It relies entirely on built-in Python libraries (`os`, `sys`, `json`, `uuid`, etc.) allowing it to run flawlessly on any fresh machine.

## 🚀 How to Run

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd <your-repository-directory>
   ```

2. **Launch the application**:
   ```bash
   python app.py
   ```

## 💻 Usage Instructions

### 1. Interactive Menu
By running the application without any arguments, you enter the interactive terminal menu loop:

```bash
python app.py
```

From the menu, you can navigate by typing the corresponding number on your keyboard:
- **1. Add a new log**: Prompt for a Title, Category (Completed, In Progress, Blocker, General Note), and Content.
- **2. View logs**: List all past logs chronologically with an option to filter by their category.
- **3. Update a log**: Edit the Category or Content of any existing record using its unique ID.
- **4. Delete a log**: Remove an existing record permanently.
- **5. Generate Daily Standup**: View a categorized summary of your actions over the last 48 hours for an easy daily standup update.

### 2. Standup Generator (CLI Flag)
You can directly bypass the interactive menu and quickly print out a clean, Markdown-formatted Daily Standup generated from logs created within the last 48 hours.

Run the following command in your terminal:
```bash
python app.py --standup
```
This is perfect for simply copy-pasting your updates into Slack, Teams, or your daily morning meeting channels. The output is cleanly formatted into `🚀 Completed`, `⏳ In Progress`, and `⚠️ Blockers`.

## 💾 Data Storage

All data is stored locally in your root directory inside a single file named `journal.json`. 
- If the file does not exist, DevLog will gracefully create and initialize it on its first run.
- The application includes robust error-handling, meaning an empty or corrupted `journal.json` file will not crash the script, but will reset safely to begin capturing new logs.