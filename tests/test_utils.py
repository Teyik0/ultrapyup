from pathlib import Path

from ultrapyup.utils import console, file_exist, log


class TestFileExist:
    """Tests for file_exist function."""

    def test_file_exists(self, temp_dir: Path):
        """Test when file exists."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        assert file_exist(test_file) is True

    def test_file_does_not_exist(self, temp_dir: Path):
        """Test when file doesn't exist."""
        test_file = temp_dir / "nonexistent.txt"

        assert file_exist(test_file) is False

    def test_directory_exists(self, temp_dir: Path):
        """Test when checking a directory."""
        test_dir = temp_dir / "testdir"
        test_dir.mkdir()

        assert file_exist(test_dir) is True

    def test_symlink_exists(self, temp_dir: Path):
        """Test when checking a symlink."""
        test_file = temp_dir / "original.txt"
        test_file.write_text("content")

        symlink = temp_dir / "link_to_original.txt"
        symlink.symlink_to(test_file)

        assert file_exist(symlink) is True

    def test_broken_symlink(self, temp_dir: Path):
        """Test when checking a broken symlink."""
        symlink = temp_dir / "broken_link.txt"
        non_existent = temp_dir / "does_not_exist.txt"
        symlink.symlink_to(non_existent)

        assert file_exist(symlink) is False

    def test_with_string_path(self, temp_dir: Path):
        """Test file_exist with string path instead of Path object."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        assert file_exist(str(test_file)) is True
        assert file_exist(str(temp_dir / "nonexistent.txt")) is False

    def test_with_nested_path(self, temp_dir: Path):
        """Test file_exist with nested directory structure."""
        nested_dir = temp_dir / "a" / "b" / "c"
        nested_dir.mkdir(parents=True)

        nested_file = nested_dir / "deep.txt"
        nested_file.write_text("deep content")

        assert file_exist(nested_file) is True
        assert file_exist(nested_dir) is True
        assert file_exist(temp_dir / "a" / "b") is True


class TestLog:
    """Tests for log utility functions."""

    def test_log_title(self, capsys):
        """Test log.title output."""
        log.title("Test Title")

        captured = capsys.readouterr()
        assert "Test Title" in captured.out
        # Title should be in cyan (though we can't test color directly in text)
        assert captured.out.strip() != ""

    def test_log_info(self, capsys):
        """Test log.info output."""
        log.info("Test information message")

        captured = capsys.readouterr()
        assert "Test information message" in captured.out

    def test_log_multiple_messages(self, capsys):
        """Test multiple log messages."""
        log.title("Starting Process")
        log.info("Step 1 completed")
        log.info("Step 2 completed")
        log.title("Process Complete")

        captured = capsys.readouterr()
        assert "Starting Process" in captured.out
        assert "Step 1 completed" in captured.out
        assert "Step 2 completed" in captured.out
        assert "Process Complete" in captured.out

    def test_log_with_special_characters(self, capsys):
        """Test log with special characters."""
        log.info("Special chars: @#$%^&*()")
        log.title("Unicode: 🎉 ✨ 🚀")

        captured = capsys.readouterr()
        assert "@#$%^&*()" in captured.out
        assert "🎉" in captured.out
        assert "✨" in captured.out
        assert "🚀" in captured.out

    def test_log_empty_string(self, capsys):
        """Test logging empty strings."""
        log.info("")
        log.title("")

        captured = capsys.readouterr()
        # Should still output something (likely just newlines)
        assert captured.out != ""

    def test_log_multiline_message(self, capsys):
        """Test logging multiline messages."""
        multiline = "Line 1\nLine 2\nLine 3"
        log.info(multiline)

        captured = capsys.readouterr()
        assert "Line 1" in captured.out
        assert "Line 2" in captured.out
        assert "Line 3" in captured.out


class TestConsole:
    """Tests for console utility functions."""

    def test_console_print(self, capsys):
        """Test console.print functionality."""
        console.print("Test message")

        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_console_print_with_style(self, capsys):
        """Test console.print with styling."""
        console.print("[bold]Bold text[/bold]")
        console.print("[red]Red text[/red]")
        console.print("[green]✓[/green] Success")

        captured = capsys.readouterr()
        assert "Bold text" in captured.out
        assert "Red text" in captured.out
        assert "✓" in captured.out
        assert "Success" in captured.out

    def test_console_print_table_like_output(self, capsys):
        """Test console.print with table-like formatted output."""
        console.print("Package    Version")
        console.print("--------   -------")
        console.print("ultrapyup    0.1.0")
        console.print("ruff       0.1.0")

        captured = capsys.readouterr()
        assert "Package" in captured.out
        assert "Version" in captured.out
        assert "ultrapyup" in captured.out
        assert "0.1.0" in captured.out
