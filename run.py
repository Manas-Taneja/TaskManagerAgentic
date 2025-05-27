# run.py
import os
import argparse
import logging
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from datetime import datetime

from ai_task_manager.database import TaskDatabase
from ai_task_manager.search_service import SearchService
from ai_task_manager.llm_service import LLMService
from ai_task_manager.email_service import EmailService
from ai_task_manager.task_manager import TaskManager

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_task_manager.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
console = Console()

def initialize_services():
    """Initialize all required services."""
    try:
        # Initialize database
        db = TaskDatabase()
        
        # Initialize search service
        search_service = SearchService()
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Initialize email service
        email_service = EmailService()
        
        # Initialize task manager
        task_manager = TaskManager(db, search_service, llm_service)
        
        return db, search_service, llm_service, email_service, task_manager
    
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")
        exit(1)

def display_tasks(tasks):
    """Display tasks in a table format."""
    if not tasks:
        console.print("[italic]No tasks found.[/italic]")
        return
    
    table = Table(title="Tasks")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Status", style="magenta")
    table.add_column("Priority", justify="right")
    table.add_column("Due Date")
    
    for task in tasks:
        table.add_row(
            str(task['id']),
            task['title'],
            task['status'],
            str(task['priority']),
            task['due_date'] if task.get('due_date') else "-"
        )
    
    console.print(table)

def display_task_details(task):
    """Display detailed information about a task."""
    if not task:
        console.print("[italic]Task not found.[/italic]")
        return
    
    console.print(f"\n[bold green]#{task['id']} - {task['title']}[/bold green]")
    console.print(f"[bold]Description:[/bold] {task['description']}")
    console.print(f"[bold]Status:[/bold] {task['status']}")
    console.print(f"[bold]Priority:[/bold] {task['priority']}")
    console.print(f"[bold]Due Date:[/bold] {task['due_date'] if task.get('due_date') else 'Not set'}")
    console.print(f"[bold]Created:[/bold] {task['created_at']}")
    console.print(f"[bold]Last Updated:[/bold] {task['updated_at']}")
    
    # Display resources
    console.print("\n[bold]Resources:[/bold]")
    if task.get('resources'):
        for i, resource in enumerate(task['resources'], 1):
            console.print(f"  {i}. [link={resource['url']}]{resource['title']}[/link]")
            if resource.get('description'):
                console.print(f"     {resource['description']}")
    else:
        console.print("  No resources found.")
    
    # Display insights
    console.print("\n[bold]Insights:[/bold]")
    if task.get('insights'):
        for insight in task['insights']:
            md = Markdown(insight['content'])
            console.print(md)
            console.print(f"[dim]Generated on {insight['created_at']}[/dim]")
    else:
        console.print("  No insights generated yet.")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="AI Task Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List tasks command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--priority", type=int, help="Filter by priority")
    
    # Add task command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("--description", "-d", default="", help="Task description")
    add_parser.add_argument("--status", default="pending", help="Task status")
    add_parser.add_argument("--priority", "-p", type=int, default=1, help="Task priority (1-5)")
    add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    
    # Show task command
    show_parser = subparsers.add_parser("show", help="Show task details")
    show_parser.add_argument("id", type=int, help="Task ID")
    
    # Update task command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("id", type=int, help="Task ID")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--description", "-d", help="New description")
    update_parser.add_argument("--status", help="New status")
    update_parser.add_argument("--priority", "-p", type=int, help="New priority (1-5)")
    update_parser.add_argument("--due", help="New due date (YYYY-MM-DD)")
    
    # Delete task command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task ID")
    
    # Search for resources command
    search_parser = subparsers.add_parser("search", help="Search for resources")
    search_parser.add_argument("id", type=int, help="Task ID")
    
    # Generate insight command
    insight_parser = subparsers.add_parser("insight", help="Generate insights")
    insight_parser.add_argument("id", type=int, help="Task ID")
    
    # Update all tasks command
    subparsers.add_parser("update-all", help="Update all tasks")
    
    # Generate digest command
    digest_parser = subparsers.add_parser("digest", help="Generate and show daily digest")
    digest_parser.add_argument("--email", action="store_true", help="Send digest by email")
    
    args = parser.parse_args()
    
    # Initialize services
    db, search_service, llm_service, email_service, task_manager = initialize_services()
    
    try:
        if args.command == "list":
            tasks = task_manager.list_tasks(args.status, args.priority)
            display_tasks(tasks)
        
        elif args.command == "add":
            task = task_manager.add_task(
                args.title, 
                args.description, 
                args.status, 
                args.priority, 
                args.due
            )
            console.print(f"[bold green]Task #{task['id']} added successfully![/bold green]")
            
            # Automatically search for resources and generate insights
            console.print("Searching for resources...")
            task_manager.search_and_add_resources(task['id'])
            
            console.print("Generating insights...")
            task_manager.generate_and_add_insight(task['id'])
            
            # Display the updated task
            updated_task = task_manager.get_task(task['id'])
            display_task_details(updated_task)
        
        elif args.command == "show":
            task = task_manager.get_task(args.id)
            display_task_details(task)
        
        elif args.command == "update":
            # Build update kwargs from args
            update_kwargs = {}
            if args.title:
                update_kwargs["title"] = args.title
            if args.description:
                update_kwargs["description"] = args.description
            if args.status:
                update_kwargs["status"] = args.status
            if args.priority:
                update_kwargs["priority"] = args.priority
            if args.due:
                update_kwargs["due_date"] = args.due
            
            task = task_manager.update_task(args.id, **update_kwargs)
            if task:
                console.print(f"[bold green]Task #{args.id} updated successfully![/bold green]")
                display_task_details(task)
            else:
                console.print(f"[bold red]Failed to update task #{args.id}[/bold red]")
        
        elif args.command == "delete":
            success = task_manager.delete_task(args.id)
            if success:
                console.print(f"[bold green]Task #{args.id} deleted successfully![/bold green]")
            else:
                console.print(f"[bold red]Failed to delete task #{args.id}[/bold red]")
        
        elif args.command == "search":
            console.print(f"Searching for resources for task #{args.id}...")
            resources = task_manager.search_and_add_resources(args.id)
            if resources:
                console.print(f"[bold green]Found {len(resources)} resources![/bold green]")
                task = task_manager.get_task(args.id)
                display_task_details(task)
            else:
                console.print("[bold yellow]No resources found.[/bold yellow]")
        
        elif args.command == "insight":
            console.print(f"Generating insights for task #{args.id}...")
            insight = task_manager.generate_and_add_insight(args.id)
            if insight:
                console.print("[bold green]Insight generated successfully![/bold green]")
                task = task_manager.get_task(args.id)
                display_task_details(task)
            else:
                console.print("[bold red]Failed to generate insight.[/bold red]")
        
        elif args.command == "update-all":
            console.print("Updating all tasks...")
            updated_tasks = task_manager.update_all_tasks()
            console.print(f"[bold green]Updated {len(updated_tasks)} tasks![/bold green]")
            for task in updated_tasks:
                console.print(f"- #{task['id']} {task['title']}")
        
        elif args.command == "digest":
            console.print("Generating daily digest...")
            digest_content = task_manager.generate_daily_digest()
            
            # Display digest
            console.print("\n[bold]Daily Digest[/bold]")
            md = Markdown(digest_content)
            console.print(md)
            
            # Send email if requested
            if args.email:
                console.print("Sending digest by email...")
                success = email_service.send_daily_digest(digest_content)
                if success:
                    console.print("[bold green]Digest sent successfully![/bold green]")
                else:
                    console.print("[bold red]Failed to send digest email.[/bold red]")
        
        else:
            # Show help if no command is provided
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()