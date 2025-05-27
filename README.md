# AI Task Manager

An autonomous task management system that helps you track tasks, find relevant resources, and receive daily insights via email.

## Features

- Store, view, and manage tasks with a simple CLI interface
- Automatically search for helpful resources related to your tasks
- Generate insights and summaries for tasks using AI
- Daily digest email with task updates and resources
- Modular design for easy extension

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ai-task-manager.git
   cd ai-task-manager
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your API keys and settings:
   - `SERPAPI_KEY`: Your SerpAPI key for web search
   - `ANTHROPIC_API_KEY`: Your Anthropic API key (or another LLM service)
   - Email settings for the daily digest

6. Initialize the database:
   ```bash
   python scripts/setup_db.py
   ```

7. Optionally, add sample tasks:
   ```bash
   python scripts/setup_db.py --with-samples
   ```

## Usage

### Command Line Interface

The app provides a simple CLI for managing tasks:

```bash
# List all tasks
python run.py list

# Add a new task
python run.py add "Learn Docker" --description "Study Docker containers and best practices" --priority 3

# Show task details
python run.py show 1

# Update a task
python run.py update 1 --status "in_progress"

# Delete a task
python run.py delete 1

# Search for resources for a task
python run.py search 1

# Generate insights for a task
python run.py insight 1

# Update all tasks with new resources and insights
python run.py update-all

# Generate and view the daily digest
python run.py digest

# Generate and send the daily digest by email
python run.py digest --email
```

### Daily Digest Email

To receive a daily digest email with task updates:

1. Ensure your email settings are correctly configured in the `.env` file
2. Run the daily digest script manually:
   ```bash
   python scripts/daily_digest.py
   ```

3. Or set up a scheduled task to run it automatically (see Scheduling section)

## Scheduling the Daily Digest

### On Linux/Mac (cron)

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add the following line to run the digest at 8 AM every day:
   ```cron
   0 8 * * * cd /path/to/ai-task-manager && /path/to/venv/bin/python scripts/daily_digest.py
   ```

### On Windows (Task Scheduler)

1. Create a batch file called `run_digest.bat`:
   ```batch
   @echo off
   cd C:\path\to\ai-task-manager
   call venv\Scripts\activate
   python scripts\daily_digest.py
   ```

2. Open Task Scheduler and create a new basic task:
   - Name it "AI Task Manager Daily Digest"
   - Set the trigger to run daily at 8 AM
   - Set the action to "Start a program"
   - Browse to select your `run_digest.bat` file
   - Finish the wizard

## Extending the System

The modular design makes it easy to extend the system. Some ideas:

- Add more search providers beyond SerpAPI
- Integrate different LLM providers
- Create a web interface with Flask or FastAPI
- Add integrations with project management tools
- Implement reminders and notifications
- Add natural language processing for task creation

## License

MIT