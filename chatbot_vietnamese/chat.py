#!/usr/bin/env python3
"""
Vietnamese CubeJS Chatbot - Quick Launcher

A simple launcher script similar to Ollama's interface.
Usage: python chat.py
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import interactive_chat, demo_mode, print_banner


def main():
    """Quick launcher for the chatbot."""
    
    # Check for simple command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--demo', '-d', 'demo']:
            demo_mode()
            return
        elif arg in ['--help', '-h', 'help']:
            print_banner()
            print("\n🚀 Vietnamese CubeJS Chatbot - Quick Launcher")
            print("\nUsage:")
            print("  python chat.py           # Start interactive chat")
            print("  python chat.py demo      # Run demo mode")
            print("  python chat.py help      # Show this help")
            print("\nCommands in chat:")
            print("  /help     - Show help")
            print("  /stats    - Show session stats")
            print("  /save     - Save conversation")
            print("  /clear    - Clear screen")
            print("  /exit     - Exit chat")
            return
        elif arg in ['--version', '-v', 'version']:
            print("Vietnamese CubeJS Chatbot v1.0")
            return
    
    # Default: start interactive chat
    interactive_chat()


if __name__ == "__main__":
    main() 