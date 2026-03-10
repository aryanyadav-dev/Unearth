#!/usr/bin/env python3
"""
Unearth Forensic Recovery Tool - Main Launcher
Interactive launcher that lets users choose between CLI and GUI.

Usage:
    python run.py           # Interactive mode (asks for preference)
    python run.py --cli     # Launch CLI directly
    python run.py --gui     # Launch GUI directly
"""

import sys
import os
import argparse
from pathlib import Path
import subprocess

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def print_banner():
    """Print Unearth banner"""
    banner = """
 ╔════════════════════════════════════════════════════════════════╗
 ║                                                                ║
 ║  ██    ██ ███    ██ ███████  █████  ██████╗ ████████╗ ██   ██  ║
 ║  ██    ██ ████   ██ ██      ██   ██ ██   ██ ╚══██╔══╝ ██   ██  ║
 ║  ██    ██ ██ ██  ██ █████   ███████ ██████╔╝   ██║    ███████  ║
 ║  ██    ██ ██  ██ ██ ██      ██   ██ ██   ██    ██║    ██   ██  ║
 ║   ██████  ██   ████ ███████ ██   ██ ██   ██    ██║    ██   ██  ║
 ║                                                                ║
 ║               Forensic Data Recovery & Analysis Tool           ║
 ║                           Version 1.0.0                        ║
 ║                                                                ║
 ╚════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def is_root():
    """Check if the current process is running as root"""
    return os.geteuid() == 0


def relaunch_with_sudo():
    """Relaunch the script with sudo, preserving display and dbus environment"""
    print("\n🔒 Elevating privileges for full disk access...\n")

    env_vars = {
        "DISPLAY": os.getenv("DISPLAY", ""),
        "XAUTHORITY": os.getenv("XAUTHORITY", ""),
        "DBUS_SESSION_BUS_ADDRESS": os.getenv("DBUS_SESSION_BUS_ADDRESS", ""),
    }

    command = [
        "sudo",
        "-E",
        "env",
        f"DISPLAY={env_vars['DISPLAY']}",
        f"XAUTHORITY={env_vars['XAUTHORITY']}",
        f"DBUS_SESSION_BUS_ADDRESS={env_vars['DBUS_SESSION_BUS_ADDRESS']}",
        sys.executable,
        *sys.argv,
    ]

    try:
        subprocess.run(command)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Failed to relaunch with sudo: {e}")
        sys.exit(1)


def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []

    try:
        import click
        import rich
    except ImportError as e:
        missing.append(f"CLI: {str(e).split()[-1]}")

    try:
        import PyQt6
        import qtawesome
    except ImportError as e:
        missing.append(f"GUI: {str(e).split()[-1]}")

    return missing


def launch_cli():
    """Launch CLI interface"""
    try:
        from ui.cli import main as cli_main
        print("\n🖥️  Launching CLI Interface...\n")
        cli_main()
    except ImportError as e:
        print(f"❌ Error: Failed to launch CLI ({e})")
        print("💡 Install CLI dependencies: pip install click rich")
        sys.exit(1)


def launch_gui():
    """Launch GUI interface"""
    try:
        from ui.gui import main as gui_main
        print("\n🖼️  Launching GUI Interface...\n")
        gui_main()
    except ImportError as e:
        print(f"❌ Error: Failed to launch GUI ({e})")
        print("💡 Install GUI dependencies: pip install PyQt6 qtawesome")
        sys.exit(1)
    except Exception as e:
        print(f"❌ GUI Runtime Error: {e}")
        sys.exit(1)


def interactive_mode():
    """Interactive mode - ask user preference"""
    print_banner()

    # Check dependencies
    missing = check_dependencies()
    if missing:
        print("⚠️  Missing dependencies:")
        for dep in missing:
            print(f"   • {dep}")
        print("\n💡 Install all dependencies with:")
        print("   pip install -r requirements.txt\n")

    print("📋 Choose Interface Mode:\n")
    print("   [1] 🖼️  GUI - Graphical User Interface (Recommended)")
    print("   [2] 🖥️  CLI - Command-Line Interface")
    print("   [3] ❌ Exit\n")

    while True:
        choice = input("Enter your choice (1-3): ").strip()
        if choice == '1':
            launch_gui()
            break
        elif choice == '2':
            launch_cli()
            break
        elif choice == '3':
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")


def main():
    """Main launcher entry point"""
    parser = argparse.ArgumentParser(
        description="Unearth Forensic Recovery Tool",
        epilog="For detailed help, run: Unearth --help (CLI) or use GUI help menu"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--cli", action="store_true", help="Launch CLI interface directly")
    group.add_argument("--gui", action="store_true", help="Launch GUI interface directly")

    args = parser.parse_args()

    # Check for root permissions FIRST, before showing any menu
    if not is_root():
        print_banner()
        print("⚠️  Unearth requires root privileges for disk access.\n")
        relaunch_with_sudo()
    
    # Now we are running as root - proceed with normal flow
    if args.cli:
        launch_cli()
    elif args.gui:
        launch_gui()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
