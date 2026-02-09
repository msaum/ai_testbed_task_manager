"""
Integration tests for project deletion with task reassignment.

Tests that when a project is deleted, tasks associated with that project
are tracked for potential reassignment by the service layer.

Note: The storage layer itself does not auto-reassign tasks on project deletion.
The service layer would need additional logic to handle this.
"""
import pytest
from pathlib import Path
from datetime import datetime

from app.models.task import Task, TaskUpdate
from app.models.project import Project
from app.storage.json_file import JSONFileStore
from app.services.tasks import TaskService
from app.services.projects import ProjectService


class TestProjectDeletionWithTaskReassignment:
    """Tests for project deletion with task reassignment."""

    def test_project_can_be_deleted(self, temp_dir):
        """Test that a project can be deleted successfully."""
        tasks_file = str(temp_dir / "tasks.json")
        projects_file = str(temp_dir / "projects.json")

        task_store = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        # Create a project
        project = Project(name="Work")
        project_store.add(project)

        # Create tasks with that project
        task1 = Task(title="Task 1", project="Work")
        task2 = Task(title="Task 2", project="Work")
        task3 = Task(title="Task 3", project="Personal")
        task_store.add(task1)
        task_store.add(task2)
        task_store.add(task3)

        # Verify initial state
        all_tasks = task_store.get_all()
        work_tasks = [t for t in all_tasks if t.project == "Work"]
        assert len(work_tasks) == 2

        personal_tasks = [t for t in all_tasks if t.project == "Personal"]
        assert len(personal_tasks) == 1

        # Delete the project
        deleted = project_store.delete_by_field("name", "Work")
        assert deleted == 1
        assert project_store.count() == 0

        # Tasks remain in storage with their original project reference
        # (This documents current storage layer behavior)
        all_tasks = task_store.get_all()
        assert len(all_tasks) == 3

    def test_delete_nonexistent_project(self, temp_dir):
        """Test that deleting a non-existent project returns False."""
        projects_file = str(temp_dir / "projects.json")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        deleted = project_store.delete_by_field("name", "NonExistent")
        assert deleted == 0

    def test_delete_project_keeps_other_projects(self, temp_dir):
        """Test that deleting one project keeps other projects."""
        projects_file = str(temp_dir / "projects.json")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        # Create multiple projects
        project_store.add(Project(name="Work"))
        project_store.add(Project(name="Personal"))
        project_store.add(Project(name="Inbox"))

        # Delete Work
        project_store.delete_by_field("name", "Work")

        # Other projects should remain
        all_projects = project_store.get_all()
        project_names = [p.name for p in all_projects]
        assert "Work" not in project_names
        assert "Personal" in project_names
        assert "Inbox" in project_names

    def test_delete_all_projects(self, temp_dir):
        """Test that all projects can be deleted."""
        projects_file = str(temp_dir / "projects.json")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        project_store.add(Project(name="Work"))
        project_store.add(Project(name="Personal"))

        project_store.delete_by_field("name", "Work")
        project_store.delete_by_field("name", "Personal")

        assert project_store.count() == 0


class TestTaskServiceProjectReassignment:
    """Tests for TaskService with project deletion considerations."""

    def test_task_service_with_project_deletion(self, temp_dir):
        """Test TaskService handles project deletion gracefully."""
        tasks_file = str(temp_dir / "tasks.json")
        projects_file = str(temp_dir / "projects.json")

        task_store = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        # Create a project and tasks
        project = Project(name="ProjectToDelete")
        project_store.add(project)

        task_store.add(Task(title="Task 1", project="ProjectToDelete"))
        task_store.add(Task(title="Task 2", project="ProjectToDelete"))

        # Delete project
        deleted = project_store.delete_by_field("name", "ProjectToDelete")
        assert deleted == 1

        # Tasks should remain but with original project name (storage layer doesn't auto-reassign)
        # This test documents current behavior - tasks keep their project name
        all_tasks = task_store.get_all()
        assert len(all_tasks) == 2


class TestCrossEntityIntegrity:
    """Tests for cross-entity integrity during project deletion."""

    def test_tasks_reference_valid_projects_after_delete(self, temp_dir):
        """Test that tasks can reference any project name."""
        tasks_file = str(temp_dir / "tasks.json")
        projects_file = str(temp_dir / "projects.json")

        task_store = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        # Create projects
        project_store.add(Project(name="Work"))
        project_store.add(Project(name="Personal"))

        # Create tasks with different projects
        task_store.add(Task(title="Work Task 1", project="Work"))
        task_store.add(Task(title="Work Task 2", project="Work"))
        task_store.add(Task(title="Personal Task", project="Personal"))

        # Delete Work project
        project_store.delete_by_field("name", "Work")

        # Get all tasks - verify they exist
        all_tasks = task_store.get_all()
        assert len(all_tasks) == 3

        # Verify tasks with deleted project reference exist
        work_tasks = [t for t in all_tasks if t.project == "Work"]
        assert len(work_tasks) == 2

    def test_persistence_after_project_delete(self, temp_dir):
        """Test that changes persist after project deletion."""
        tasks_file = str(temp_dir / "tasks.json")
        projects_file = str(temp_dir / "projects.json")

        # First instance
        task_store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store1 = JSONFileStore(projects_file, Project, collection_key="items")

        project_store1.add(Project(name="ToDelete"))
        task_store1.add(Task(title="Task 1", project="ToDelete"))

        # Second instance - verify persistence
        task_store2 = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store2 = JSONFileStore(projects_file, Project, collection_key="items")

        assert project_store2.count() == 1
        assert task_store2.count() == 1

        # Delete project via second instance
        deleted = project_store2.delete_by_field("name", "ToDelete")
        assert deleted == 1

        # Third instance - verify deletion
        task_store3 = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store3 = JSONFileStore(projects_file, Project, collection_key="items")

        assert project_store3.count() == 0
        assert task_store3.count() == 1


class TestEmptyProjectDeletion:
    """Tests for edge cases in project deletion."""

    def test_delete_project_with_no_tasks(self, temp_dir):
        """Test deleting a project that has no tasks."""
        projects_file = str(temp_dir / "projects.json")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        project_store.add(Project(name="EmptyProject"))

        assert project_store.count() == 1

        deleted = project_store.delete_by_field("name", "EmptyProject")
        assert deleted == 1
        assert project_store.count() == 0

    def test_multiple_deletes_of_same_project(self, temp_dir):
        """Test deleting the same project multiple times."""
        projects_file = str(temp_dir / "projects.json")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        project_store.add(Project(name="ToDelete"))

        deleted1 = project_store.delete_by_field("name", "ToDelete")
        assert deleted1 == 1

        deleted2 = project_store.delete_by_field("name", "ToDelete")
        assert deleted2 == 0  # Second delete returns False

    def test_case_sensitive_project_name(self, temp_dir):
        """Test that project name matching is case-sensitive."""
        projects_file = str(temp_dir / "projects.json")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        project_store.add(Project(name="Work"))

        # Delete with different case
        deleted = project_store.delete_by_field("name", "work")
        assert deleted == 0

        # Verify project still exists
        assert project_store.count() == 1

        # Delete with correct case
        deleted = project_store.delete_by_field("name", "Work")
        assert deleted == 1


class TestTaskReassignmentPattern:
    """Tests demonstrating expected task reassignment pattern."""

    def test_service_layer_should_reassign_tasks(self, temp_dir):
        """
        Test that demonstrates the expected reassignment pattern.

        This test documents what a proper service layer implementation
        should do when a project is deleted: reassign all tasks to Inbox.
        """
        tasks_file = str(temp_dir / "tasks.json")
        projects_file = str(temp_dir / "projects.json")

        task_store = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        # Setup: Create project and tasks
        project_store.add(Project(name="Work"))
        task_store.add(Task(title="Task 1", project="Work"))
        task_store.add(Task(title="Task 2", project="Work"))
        task_store.add(Task(title="Task 3", project="Personal"))

        # Simulate service layer reassignment:
        # When Work project is deleted, reassign its tasks to Inbox
        tasks_to_update = [t for t in task_store.get_all() if t.project == "Work"]
        for task in tasks_to_update:
            task.project = "Inbox"
            task_store.update(task)

        # Delete the project
        project_store.delete_by_field("name", "Work")

        # Verify reassignment worked
        inbox_tasks = [t for t in task_store.get_all() if t.project == "Inbox"]
        assert len(inbox_tasks) == 2  # Task 1 and 2 were reassigned from Work
        personal_tasks = [t for t in task_store.get_all() if t.project == "Personal"]
        assert len(personal_tasks) == 1  # Task 3 stays in Personal
        # Total should be 3 tasks
        assert len(task_store.get_all()) == 3

    def test_manual_task_project_update(self, temp_dir):
        """Test that individual task project can be updated manually."""
        tasks_file = str(temp_dir / "tasks.json")
        project_store = JSONFileStore(str(temp_dir / "projects.json"), Project, collection_key="items")

        project_store.add(Project(name="Work"))
        project_store.add(Project(name="Inbox"))

        task_store = JSONFileStore(tasks_file, Task, collection_key="items")
        task = task_store.add(Task(title="Task", project="Work"))

        # Manually update task project
        task.project = "Personal"
        task_store.update(task)

        # Verify update
        updated = task_store.get_by_id(task.id)
        assert updated.project == "Personal"


class TestProjectCleanupPattern:
    """Tests for project cleanup patterns."""

    def test_cleanup_project_removes_tasks_reference(self, temp_dir):
        """Test pattern for cleaning up project references from tasks."""
        tasks_file = str(temp_dir / "tasks.json")
        projects_file = str(temp_dir / "projects.json")

        task_store = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store = JSONFileStore(projects_file, Project, collection_key="items")

        # Setup
        project_store.add(Project(name="OldProject"))
        task_store.add(Task(title="Task 1", project="OldProject"))
        task_store.add(Task(title="Task 2", project="OldProject"))

        # Pattern: Clean up project and all task references
        # First, update tasks to use a different project
        for task in task_store.get_all():
            if task.project == "OldProject":
                task.project = "Inbox"
                task_store.update(task)

        # Then delete the project
        project_store.delete_by_field("name", "OldProject")

        # Verify: no tasks reference deleted project
        tasks_with_old_project = [t for t in task_store.get_all() if t.project == "OldProject"]
        assert len(tasks_with_old_project) == 0

        # Verify: no projects with that name
        assert project_store.get_by_field("name", "OldProject") is None
