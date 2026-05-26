import json
import os
import sys
import uuid
from datetime import datetime, timedelta

DATA_FILE = "journal.json"

CATEGORIES = {
    "1": "Completed",
    "2": "In Progress",
    "3": "Blocker",
    "4": "General Note"
}


def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def load_logs():
    """Loads logs from the JSON file with robust error handling for fresh machines."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, IOError):
        # Gracefully handle corrupted or empty file
        return []


def save_logs(logs):
    """Saves logs to the JSON file safely."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4)
    except IOError as e:
        print(f"\n[ERROR] Could not save to {DATA_FILE}: {e}")


def get_category_choice():
    """Helper to prompt for and validate a category choice."""
    print("\nCategories:")
    for key, val in CATEGORIES.items():
        print(f"  {key}. {val}")

    while True:
        choice = input("Select Category (1-4): ").strip()
        if choice in CATEGORIES:
            return CATEGORIES[choice]
        print("[ERROR] Invalid choice. Please enter a number between 1 and 4.")


def add_log(logs):
    """Creates a new journal entry."""
    clear_screen()
    print("=== Create New Log ===\n")

    title = input("Title: ").strip()
    if not title:
        title = "Untitled Note"

    category = get_category_choice()

    print("\nContent (Press Enter on an empty line to finish):")
    content_lines = []
    while True:
        line = input()
        if not line.strip() and content_lines:
            # End of input on double enter, but let's just use single empty enter line as finish.
            # To be more forgiving, we will break on just an empty line.
            break
        if not line and not content_lines:
            break
        content_lines.append(line)

    content = "\n".join(content_lines).strip()
    if not content:
        content = "No content provided."

    now = datetime.now()
    log_entry = {
        "id": str(uuid.uuid4())[:8],  # 8 char ID for simplicity
        "timestamp": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "title": title,
        "category": category,
        "content": content
    }

    logs.append(log_entry)
    save_logs(logs)
    print(f"\n[SUCCESS] Log '{log_entry['id']}' added!")
    input("Press Enter to continue...")


def display_single_log(log):
    """Formats and prints a single log entry."""
    print("-" * 50)
    print(f"ID       : {log['id']}")
    print(f"Date     : {log['timestamp'][:19].replace('T', ' ')}")
    print(f"Category : {log['category']}")
    print(f"Title    : {log['title']}")
    print("Content  :")
    print(log['content'])
    print("-" * 50)


def view_logs(logs):
    """Lists logs with optional filtering."""
    clear_screen()
    print("=== View Logs ===\n")
    if not logs:
        print("No logs found. Start configuring your DevLog!")
        input("\nPress Enter to continue...")
        return

    filter_choice = input("Filter by Category? (y/N): ").strip().lower()

    target_category = None
    if filter_choice == 'y':
        target_category = get_category_choice()

    filtered_logs = [log for log in logs if log['category']
                     == target_category] if target_category else logs

    if not filtered_logs:
        print(f"\nNo logs found for category: {target_category}")
    else:
        print(f"\nShowing {len(filtered_logs)} log(s):\n")
        # Sort chronologically by timestamp
        filtered_logs.sort(key=lambda x: x['timestamp'])
        for log in filtered_logs:
            display_single_log(log)

    input("\nPress Enter to return to menu...")


def update_log(logs):
    """Updates an existing log's category or content."""
    clear_screen()
    print("=== Update Log ===\n")
    if not logs:
        print("No logs available to update.")
        input("\nPress Enter to continue...")
        return

    log_id = input("Enter the ID of the log to update: ").strip()

    target_log = None
    for log in logs:
        if log["id"] == log_id:
            target_log = log
            break

    if not target_log:
        print(f"\n[ERROR] No log found with ID '{log_id}'.")
        input("Press Enter to continue...")
        return

    display_single_log(target_log)

    print("\nWhat would you like to update?")
    print("1. Category")
    print("2. Content")
    print("3. Cancel")

    choice = input("Choice (1-3): ").strip()

    if choice == "1":
        target_log['category'] = get_category_choice()
        save_logs(logs)
        print("\n[SUCCESS] Category updated.")
    elif choice == "2":
        print("\nEnter New Content (Press Enter on an empty line to finish):")
        content_lines = []
        while True:
            line = input()
            if not line:
                break
            content_lines.append(line)
        if content_lines:
            target_log['content'] = "\n".join(content_lines).strip()
            save_logs(logs)
            print("\n[SUCCESS] Content updated.")
        else:
            print("\n[INFO] Content update aborted (no content entered).")
    elif choice == "3":
        print("\n[INFO] Update canceled.")
    else:
        print("\n[ERROR] Invalid choice. Canceled.")

    input("Press Enter to continue...")


def delete_log(logs):
    """Removes a log by ID."""
    clear_screen()
    print("=== Delete Log ===\n")
    if not logs:
        print("No logs available to delete.")
        input("\nPress Enter to continue...")
        return

    log_id = input("Enter the ID of the log to delete: ").strip()

    for i, log in enumerate(logs):
        if log["id"] == log_id:
            display_single_log(log)
            confirm = input(
                "\nAre you SURE you want to delete this log? (y/N): ").strip().lower()
            if confirm == 'y':
                logs.pop(i)
                save_logs(logs)
                print(f"\n[SUCCESS] Log '{log_id}' has been deleted.")
            else:
                print("\n[INFO] Deletion canceled.")
            input("Press Enter to continue...")
            return

    print(f"\n[ERROR] No log found with ID '{log_id}'.")
    input("Press Enter to continue...")


def generate_standup(logs, from_cli=False):
    """Generates a Daily Standup Summary for operations in the last 48 hours."""
    if not from_cli:
        clear_screen()

    print("=== 📊 Daily Standup Summary (Last 48 Hours) ===\n")

    now = datetime.now()
    cutoff_time = now - timedelta(hours=48)

    recent_logs = []
    for log in logs:
        try:
            log_time = datetime.fromisoformat(log['timestamp'])
            if log_time >= cutoff_time:
                recent_logs.append(log)
        except ValueError:
            pass  # Ignore corrupted timestamps

    if not recent_logs:
        print("No activity recorded in the last 48 hours.")
        if not from_cli:
            input("\nPress Enter to continue...")
        return

    # Categorize logs
    completed = [log for log in recent_logs if log['category'] == "Completed"]
    in_progress = [
        log for log in recent_logs if log['category'] == "In Progress"]
    blockers = [log for log in recent_logs if log['category'] == "Blocker"]

    print("🚀 Completed:")
    if not completed:
        print("  - None")
    else:
        for log in completed:
            print(f"  - {log['title']}")

    print("\n⏳ In Progress:")
    if not in_progress:
        print("  - None")
    else:
        for log in in_progress:
            print(f"  - {log['title']}")

    print("\n⚠️ Blockers:")
    if not blockers:
        print("  - None")
    else:
        for log in blockers:
            print(f"  - {log['title']}")

    print("\n" + "=" * 48)

    if not from_cli:
        input("\nPress Enter to return to menu...")


def display_menu():
    """Prints the main application menu."""
    clear_screen()
    print("=" * 35)
    print(" 🛠️  DevLog - Developer Journal 🛠️ ")
    print("=" * 35)
    print("1. ➕ Add a new log")
    print("2. 📖 View logs")
    print("3. ✏️  Update a log")
    print("4. ❌ Delete a log")
    print("5. 📊 Generate Daily Standup")
    print("6. 🚪 Exit")
    print("=" * 35)


def main():
    logs = load_logs()

    # CLI parameter check
    if len(sys.argv) > 1 and sys.argv[1] == '--standup':
        generate_standup(logs, from_cli=True)
        sys.exit(0)

    while True:
        display_menu()
        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            add_log(logs)
        elif choice == "2":
            view_logs(logs)
        elif choice == "3":
            update_log(logs)
        elif choice == "4":
            delete_log(logs)
        elif choice == "5":
            generate_standup(logs)
        elif choice == "6":
            print("\nGoodbye! Keep coding! 💻")
            break
        else:
            print("\n[ERROR] Invalid choice. Please choose a valid option.")
            input("Press Enter to try again...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Exiting DevLog smoothly... Goodbye! 💻")
        sys.exit(0)
