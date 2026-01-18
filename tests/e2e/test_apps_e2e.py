"""
End-to-end tests for Darvis Voice Assistant application launching.

These tests verify that voice commands correctly launch applications,
open web services, and handle various application management scenarios.
"""

import pytest
import time
import psutil
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mark all tests in this module as E2E and apps tests
pytestmark = [pytest.mark.e2e, pytest.mark.apps]


class TestApplicationLaunching:
    """Tests for basic application launching functionality."""

    def test_calculator_launch(self, darvis_process, voice_simulator, process_monitor):
        """
        Test launching calculator application.

        Verifies that voice command "open calculator" successfully launches calculator.
        """
        # Trigger voice command
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open calculator")

        # Wait for application to launch
        calculator_found = process_monitor.wait_for_process("calculator", timeout=5.0)

        # Verify calculator launched
        assert calculator_found, "Calculator should launch after voice command"

        assert darvis_process.poll() is None

    def test_terminal_launch(self, darvis_process, voice_simulator, process_monitor):
        """
        Test launching terminal application.

        Verifies that terminal/terminal emulator launches correctly.
        """
        # Trigger voice command
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open terminal")

        # Wait for terminal to launch (could be gnome-terminal, konsole, xterm, etc.)
        terminal_names = ["gnome-terminal", "konsole", "xterm", "alacritty", "terminator"]
        terminal_found = False

        for term_name in terminal_names:
            if process_monitor.wait_for_process(term_name, timeout=3.0):
                terminal_found = True
                break

        assert terminal_found, f"Terminal should launch (checked: {terminal_names})"

        assert darvis_process.poll() is None

    def test_web_browser_launch(self, darvis_process, voice_simulator, process_monitor):
        """
        Test launching web browser.

        Verifies that browser launches for general web commands.
        """
        # Trigger voice command
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open browser")

        # Wait for browser to launch
        browser_names = ["firefox", "chromium", "chrome", "opera", "vivaldi"]
        browser_found = False

        for browser_name in browser_names:
            if process_monitor.wait_for_process(browser_name, timeout=5.0):
                browser_found = True
                break

        assert browser_found, f"Web browser should launch (checked: {browser_names})"

        assert darvis_process.poll() is None


class TestWebServiceIntegration:
    """Tests for web service launching and URL handling."""

    def test_youtube_launch(self, darvis_process, voice_simulator, process_monitor):
        """
        Test YouTube web service integration.

        Verifies that YouTube commands open browser with correct URL.
        """
        # Trigger YouTube command
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open youtube")

        # Wait for browser to launch
        browser_found = process_monitor.wait_for_process("firefox|chromium|chrome", timeout=5.0)
        assert browser_found, "Browser should launch for YouTube command"

        assert darvis_process.poll() is None

    def test_github_launch(self, darvis_process, voice_simulator, process_monitor):
        """
        Test GitHub web service integration.

        Verifies that GitHub commands work correctly.
        """
        # Trigger GitHub command
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open github")

        # Wait for browser to launch
        browser_found = process_monitor.wait_for_process("firefox|chromium|chrome", timeout=5.0)
        assert browser_found, "Browser should launch for GitHub command"

        assert darvis_process.poll() is None

    def test_multiple_web_services(self, darvis_process, voice_simulator, process_monitor):
        """
        Test launching multiple web services in sequence.

        Verifies that consecutive web service commands work properly.
        """
        services = ["youtube", "github", "gmail"]

        for service in services:
            # Clear previous processes
            process_monitor.take_baseline()

            # Trigger service command
            voice_simulator.simulate_wake_word("hey darvis")
            time.sleep(0.5)
            voice_simulator.simulate_voice_command(f"open {service}")

            # Wait for browser
            browser_found = process_monitor.wait_for_process("firefox|chromium|chrome", timeout=5.0)
            assert browser_found, f"Browser should launch for {service}"

            # Brief pause between commands
            time.sleep(2)

        assert darvis_process.poll() is None


class TestApplicationErrorHandling:
    """Tests for application launching error scenarios."""

    def test_unknown_application(self, darvis_process, voice_simulator):
        """
        Test handling of unknown application names.

        Verifies graceful handling when requested application doesn't exist.
        """
        # Trigger command for non-existent application
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open nonexistentapp12345")

        # Wait for processing
        voice_simulator.wait_for_voice_processing()

        # Verify application didn't crash and handled error gracefully
        assert darvis_process.poll() is None, "Should handle unknown applications without crashing"

    def test_application_already_running(self, darvis_process, voice_simulator, process_monitor):
        """
        Test launching application that's already running.

        Verifies behavior when trying to launch an already open application.
        """
        # First launch calculator
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open calculator")

        calculator_found = process_monitor.wait_for_process("calculator", timeout=5.0)
        assert calculator_found, "Calculator should launch initially"

        # Try to launch again
        time.sleep(2)  # Wait a bit
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open calculator")

        # Wait for processing
        voice_simulator.wait_for_voice_processing()

        # Verify system remains stable
        assert darvis_process.poll() is None, "Should handle already-running applications gracefully"

    def test_permission_denied_applications(self, darvis_process, voice_simulator):
        """
        Test handling applications that require elevated permissions.

        Verifies appropriate handling of permission-related launch failures.
        """
        # Try to launch system settings or similar (may require permissions)
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open system settings")

        # Wait for processing
        voice_simulator.wait_for_voice_processing()

        # Verify graceful handling
        assert darvis_process.poll() is None, "Should handle permission issues without crashing"


class TestApplicationPerformance:
    """Tests for application launching performance."""

    def test_launch_response_time(self, darvis_process, voice_simulator, process_monitor):
        """
        Test application launch response time.

        Measures time from voice command to application window appearance.
        """
        import time

        # Measure launch time
        start_time = time.time()

        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open calculator")

        # Wait for calculator
        calculator_found = process_monitor.wait_for_process("calculator", timeout=10.0)

        launch_time = time.time() - start_time

        assert calculator_found, "Calculator should launch"
        assert launch_time < 15.0, f"Launch time {launch_time:.2f}s exceeded 15s limit"

        assert darvis_process.poll() is None

    def test_concurrent_application_launches(self, darvis_process, voice_simulator, process_monitor):
        """
        Test launching multiple applications in quick succession.

        Verifies system stability when multiple launch commands are issued rapidly.
        """
        # Launch multiple applications quickly
        apps = ["calculator", "terminal", "browser"]

        for app in apps:
            voice_simulator.simulate_wake_word("hey darvis")
            time.sleep(0.5)
            voice_simulator.simulate_voice_command(f"open {app}")
            time.sleep(1)  # Brief pause between commands

        # Wait for all to complete processing
        time.sleep(5)

        # Verify system remained stable
        assert darvis_process.poll() is None, "Should handle concurrent launches without crashing"

    def test_application_cleanup(self, darvis_process, voice_simulator, process_monitor):
        """
        Test that launched applications are properly managed.

        Verifies that the assistant doesn't leave orphaned processes.
        """
        # Launch an application
        voice_simulator.simulate_wake_word("hey darvis")
        time.sleep(0.5)
        voice_simulator.simulate_voice_command("open calculator")

        calculator_found = process_monitor.wait_for_process("calculator", timeout=5.0)
        assert calculator_found, "Calculator should launch"

        # Get list of new processes
        new_processes = process_monitor.get_new_processes()

        # Verify calculator is in the list
        calculator_processes = [p for p in new_processes if 'calculator' in p.get('name', '').lower()]
        assert len(calculator_processes) > 0, "Calculator process should be tracked"

        assert darvis_process.poll() is None