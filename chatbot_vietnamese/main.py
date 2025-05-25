#!/usr/bin/env python3
"""
Vietnamese CubeJS Chatbot - Interactive Chat Interface with Memory
Enhanced Ollama-style conversation with memory capabilities
"""

import os
import sys
import time
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

# Add the parent directory to the path so we can import golett
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import VietnameseCubeJSChatbot


class ChatSessionManager:
    """Manages multiple chat sessions with persistence."""
    
    def __init__(self, sessions_dir: str = "chat_sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        self.current_session: Optional[InteractiveChatSession] = None
        self.chatbot: Optional[VietnameseCubeJSChatbot] = None
        
    def initialize_chatbot(self) -> bool:
        """Initialize the chatbot once for all sessions."""
        if self.chatbot is not None:
            return True
            
        try:
            print("🔄 Đang khởi tạo chatbot...")
            # Initialize with default CubeJS configuration
            self.chatbot = VietnameseCubeJSChatbot(
                cubejs_api_url="http://localhost:4000",
                cubejs_api_token=None
            )
            print("✅ Chatbot đã sẵn sàng!")
            return True
        except Exception as e:
            print(f"❌ Lỗi khởi tạo chatbot: {e}")
            print("\n🔧 Vui lòng kiểm tra:")
            print("   • CubeJS server đang chạy tại localhost:4000")
            print("   • Kết nối mạng ổn định")
            print("   • Các dependencies đã được cài đặt")
            return False
    
    def create_new_session(self, name: Optional[str] = None) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())[:8]
        if not name:
            name = f"Session_{datetime.now().strftime('%m%d_%H%M')}"
        
        self.current_session = InteractiveChatSession(session_id, name, self.chatbot)
        print(f"✨ Tạo phiên chat mới: '{name}' (ID: {session_id})")
        return session_id
    
    def list_sessions(self) -> List[Dict]:
        """List all available sessions."""
        sessions = []
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "id": session_file.stem,
                        "name": data.get("name", "Unnamed"),
                        "created": data.get("session_start", "Unknown"),
                        "messages": len(data.get("conversation", [])),
                        "last_updated": data.get("session_end", data.get("session_start", "Unknown"))
                    })
            except Exception:
                continue
        
        # Sort by last updated
        sessions.sort(key=lambda x: x["last_updated"], reverse=True)
        return sessions
    
    def load_session(self, session_id: str) -> bool:
        """Load an existing session."""
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            print(f"❌ Không tìm thấy phiên chat: {session_id}")
            return False
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.current_session = InteractiveChatSession(
                session_id, 
                data.get("name", "Loaded Session"), 
                self.chatbot
            )
            self.current_session.conversation_history = data.get("conversation", [])
            self.current_session.session_start = datetime.fromisoformat(data.get("session_start", datetime.now().isoformat()))
            
            print(f"📂 Đã tải phiên chat: '{data.get('name')}' ({len(self.current_session.conversation_history)} tin nhắn)")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi tải phiên chat: {e}")
            return False
    
    def save_current_session(self) -> bool:
        """Save the current session."""
        if not self.current_session:
            print("❌ Không có phiên chat nào để lưu.")
            return False
        
        return self.current_session.save_to_file(self.sessions_dir)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            print(f"❌ Không tìm thấy phiên chat: {session_id}")
            return False
        
        try:
            session_file.unlink()
            print(f"🗑️ Đã xóa phiên chat: {session_id}")
            return True
        except Exception as e:
            print(f"❌ Lỗi xóa phiên chat: {e}")
            return False


class InteractiveChatSession:
    """Manages an interactive chat session with conversation history."""
    
    def __init__(self, session_id: str, name: str, chatbot: VietnameseCubeJSChatbot):
        self.session_id = session_id
        self.name = name
        self.chatbot = chatbot
        self.conversation_history: List[Dict] = []
        self.session_start = datetime.now()
        
    def add_to_history(self, user_input: str, bot_response: str, processing_time: float):
        """Add interaction to conversation history."""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "bot": bot_response,
            "processing_time": processing_time
        })
    
    def show_stats(self):
        """Show session statistics."""
        duration = datetime.now() - self.session_start
        print(f"\n📊 Thống kê phiên chat '{self.name}':")
        print(f"   • ID: {self.session_id}")
        print(f"   • Thời gian: {duration.total_seconds():.1f} giây")
        print(f"   • Số câu hỏi: {len(self.conversation_history)}")
        if self.conversation_history:
            avg_time = sum(h["processing_time"] for h in self.conversation_history) / len(self.conversation_history)
            print(f"   • Thời gian xử lý trung bình: {avg_time:.2f} giây")
    
    def save_to_file(self, sessions_dir: Path) -> bool:
        """Save session to file."""
        if not self.conversation_history:
            print("📝 Không có cuộc trò chuyện nào để lưu.")
            return False
            
        session_file = sessions_dir / f"{self.session_id}.json"
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "id": self.session_id,
                    "name": self.name,
                    "session_start": self.session_start.isoformat(),
                    "session_end": datetime.now().isoformat(),
                    "conversation": self.conversation_history
                }, f, ensure_ascii=False, indent=2)
            print(f"💾 Phiên chat đã được lưu: {session_file.name}")
            return True
        except Exception as e:
            print(f"❌ Lỗi lưu file: {e}")
            return False


def print_banner():
    """Print the application banner."""
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "🇻🇳 VIETNAMESE CUBEJS CHATBOT - INTERACTIVE MODE".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("║" + "Chatbot Phân tích Dữ liệu Kinh doanh Thông minh".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")


def print_help():
    """Print help information."""
    print("\n📚 Hướng dẫn sử dụng:")
    print("┌─────────────────────────────────────────────────────────┐")
    print("│ 💬 Câu hỏi mẫu:                                         │")
    print("│   • 'Doanh số tháng này như thế nào?'                   │")
    print("│   • 'Có bao nhiêu khách hàng mới?'                      │")
    print("│   • 'Sản phẩm nào bán chạy nhất?'                       │")
    print("│   • 'Xu hướng doanh thu 6 tháng qua?'                   │")
    print("│                                                         │")
    print("│ 🔧 Lệnh điều khiển:                                     │")
    print("│   • /help, /giúp     - Hiển thị hướng dẫn này          │")
    print("│   • /stats           - Hiển thị thống kê phiên         │")
    print("│   • /save            - Lưu cuộc trò chuyện             │")
    print("│   • /clear           - Xóa màn hình                    │")
    print("│                                                         │")
    print("│ 📂 Quản lý phiên chat:                                 │")
    print("│   • /new [tên]       - Tạo phiên chat mới              │")
    print("│   • /list            - Liệt kê các phiên chat          │")
    print("│   • /load <id>       - Tải phiên chat                  │")
    print("│   • /delete <id>     - Xóa phiên chat                  │")
    print("│   • /current         - Hiển thị phiên hiện tại         │")
    print("│                                                         │")
    print("│   • /exit, /quit     - Thoát chương trình              │")
    print("└─────────────────────────────────────────────────────────┘")


def print_thinking_animation():
    """Show a thinking animation."""
    thinking_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(10):
        print(f"\r🤖 {thinking_chars[i % len(thinking_chars)]} Đang suy nghĩ...", end="", flush=True)
        time.sleep(0.1)
    print("\r" + " " * 30 + "\r", end="")  # Clear the line


def format_response(response: str) -> str:
    """Format the bot response with better styling."""
    lines = response.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():
            # Add some visual formatting
            if line.startswith('•') or line.startswith('-'):
                formatted_lines.append(f"   {line}")
            elif any(keyword in line.lower() for keyword in ['total', 'tổng', 'sum', 'count', 'số lượng']):
                formatted_lines.append(f"📊 {line}")
            elif any(keyword in line.lower() for keyword in ['insight', 'recommendation', 'khuyến nghị', 'gợi ý']):
                formatted_lines.append(f"💡 {line}")
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append("")
    
    return '\n'.join(formatted_lines)


def handle_session_commands(session_manager: ChatSessionManager, command: str, args: List[str]) -> bool:
    """Handle session management commands. Returns True if command was handled."""
    
    if command == '/new':
        name = ' '.join(args) if args else None
        session_manager.create_new_session(name)
        return True
    
    elif command == '/list':
        sessions = session_manager.list_sessions()
        if not sessions:
            print("📝 Không có phiên chat nào được lưu.")
        else:
            print("\n📂 Danh sách phiên chat:")
            print("┌─────────┬──────────────────┬─────────┬─────────────────────┐")
            print("│   ID    │       Tên        │ Tin nhắn│    Cập nhật cuối    │")
            print("├─────────┼──────────────────┼─────────┼─────────────────────┤")
            for session in sessions[:10]:  # Show max 10 sessions
                name = session["name"][:16] + "..." if len(session["name"]) > 16 else session["name"]
                last_updated = session["last_updated"][:19] if len(session["last_updated"]) > 19 else session["last_updated"]
                print(f"│ {session['id']:<7} │ {name:<16} │ {session['messages']:>7} │ {last_updated:<19} │")
            print("└─────────┴──────────────────┴─────────┴─────────────────────┘")
            
            if len(sessions) > 10:
                print(f"... và {len(sessions) - 10} phiên chat khác")
        return True
    
    elif command == '/load':
        if not args:
            print("❌ Vui lòng cung cấp ID phiên chat. Ví dụ: /load abc123")
            return True
        
        session_id = args[0]
        session_manager.load_session(session_id)
        return True
    
    elif command == '/delete':
        if not args:
            print("❌ Vui lòng cung cấp ID phiên chat. Ví dụ: /delete abc123")
            return True
        
        session_id = args[0]
        confirm = input(f"⚠️  Bạn có chắc muốn xóa phiên chat '{session_id}'? (y/n): ").lower()
        if confirm in ['y', 'yes', 'có']:
            session_manager.delete_session(session_id)
        return True
    
    elif command == '/current':
        if session_manager.current_session:
            print(f"\n📍 Phiên chat hiện tại:")
            print(f"   • ID: {session_manager.current_session.session_id}")
            print(f"   • Tên: {session_manager.current_session.name}")
            print(f"   • Tin nhắn: {len(session_manager.current_session.conversation_history)}")
            print(f"   • Bắt đầu: {session_manager.current_session.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("❌ Không có phiên chat nào đang hoạt động.")
        return True
    
    return False


def interactive_chat():
    """Main interactive chat function with session management."""
    
    print_banner()
    print("\n🚀 Khởi động chế độ chat tương tác với quản lý phiên...")
    
    # Initialize session manager
    session_manager = ChatSessionManager()
    
    if not session_manager.initialize_chatbot():
        return
    
    # Create initial session
    session_manager.create_new_session("Default Session")
    
    print("\n" + "─" * 60)
    print("💬 Bắt đầu trò chuyện! Gõ /help để xem hướng dẫn.")
    print("📂 Gõ /new để tạo phiên chat mới, /list để xem các phiên đã lưu.")
    print("─" * 60)
    
    # Main chat loop
    while True:
        try:
            # Show current session in prompt
            session_name = session_manager.current_session.name if session_manager.current_session else "No Session"
            print(f"\n┌─ {session_name} " + "─" * (56 - len(session_name)) + "┐")
            user_input = input("│ 🤔 Bạn: ").strip()
            
            # Handle empty input
            if not user_input:
                print("└" + "─" * 58 + "┘")
                continue
            
            print("└" + "─" * 58 + "┘")
            
            # Handle commands
            if user_input.startswith('/'):
                command_parts = user_input.split()
                command = command_parts[0].lower()
                args = command_parts[1:] if len(command_parts) > 1 else []
                
                # Session management commands
                if handle_session_commands(session_manager, command, args):
                    continue
                
                # Regular commands
                if command in ['/exit', '/quit', '/thoát']:
                    print("\n👋 Cảm ơn bạn đã sử dụng chatbot!")
                    if session_manager.current_session:
                        session_manager.current_session.show_stats()
                        
                        # Ask if user wants to save conversation
                        if session_manager.current_session.conversation_history:
                            save_choice = input("\n💾 Bạn có muốn lưu phiên chat hiện tại không? (y/n): ").lower()
                            if save_choice in ['y', 'yes', 'có']:
                                session_manager.save_current_session()
                    
                    print("🌟 Hẹn gặp lại!")
                    break
                
                elif command in ['/help', '/giúp']:
                    print_help()
                    continue
                
                elif command == '/stats':
                    if session_manager.current_session:
                        session_manager.current_session.show_stats()
                    else:
                        print("❌ Không có phiên chat nào đang hoạt động.")
                    continue
                
                elif command == '/save':
                    session_manager.save_current_session()
                    continue
                
                elif command == '/clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print_banner()
                    continue
                
                else:
                    print(f"❓ Lệnh không xác định: {user_input}")
                    print("💡 Gõ /help để xem danh sách lệnh.")
                    continue
            
            # Check if we have an active session
            if not session_manager.current_session:
                print("❌ Không có phiên chat nào đang hoạt động. Gõ /new để tạo phiên mới.")
                continue
            
            # Process the query
            print_thinking_animation()
            
            start_time = time.time()
            try:
                response = session_manager.current_session.chatbot.chat(user_input)
                processing_time = time.time() - start_time
                
                # Format and display response
                formatted_response = format_response(response)
                
                print("┌" + "─" * 58 + "┐")
                print("│ 🤖 Bot:")
                for line in formatted_response.split('\n'):
                    if line.strip():
                        # Word wrap for long lines
                        if len(line) > 54:
                            words = line.split()
                            current_line = "│ "
                            for word in words:
                                if len(current_line + word) > 56:
                                    print(current_line)
                                    current_line = "│ " + word + " "
                                else:
                                    current_line += word + " "
                            if current_line.strip() != "│":
                                print(current_line)
                        else:
                            print(f"│ {line}")
                    else:
                        print("│")
                
                print("│")
                print(f"│ ⏱️  Thời gian xử lý: {processing_time:.2f}s")
                print("└" + "─" * 58 + "┘")
                
                # Add to history
                session_manager.current_session.add_to_history(user_input, response, processing_time)
                
            except Exception as e:
                processing_time = time.time() - start_time
                error_msg = f"Lỗi xử lý: {e}"
                
                print("┌" + "─" * 58 + "┐")
                print("│ ❌ Lỗi:")
                print(f"│ {error_msg}")
                print("│")
                print("│ 💡 Gợi ý:")
                print("│   • Thử hỏi câu hỏi khác")
                print("│   • Kiểm tra kết nối CubeJS server")
                print("│   • Gõ /help để xem hướng dẫn")
                print("└" + "─" * 58 + "┘")
                
                # Still add to history for debugging
                session_manager.current_session.add_to_history(user_input, error_msg, processing_time)
                
        except KeyboardInterrupt:
            print("\n\n⚡ Đã nhận Ctrl+C")
            if session_manager.current_session:
                session_manager.current_session.show_stats()
            print("👋 Tạm biệt!")
            break
        except EOFError:
            print("\n\n👋 Tạm biệt!")
            break


def demo_mode():
    """Run a quick demo with sample questions."""
    
    print("🎯 Chế độ Demo - Câu hỏi mẫu")
    print("=" * 40)
    
    sample_questions = [
        "Doanh số tổng cộng là bao nhiêu?",
        "Có bao nhiêu đơn hàng?",
        "Phân tích dữ liệu bán hàng",
        "Xu hướng doanh thu như thế nào?"
    ]
    
    session_manager = ChatSessionManager()
    if not session_manager.initialize_chatbot():
        return
    
    session_manager.create_new_session("Demo Session")
    
    for i, question in enumerate(sample_questions, 1):
        print(f"\n{i}. 🤔 {question}")
        try:
            start_time = time.time()
            response = session_manager.current_session.chatbot.chat(question)
            processing_time = time.time() - start_time
            
            # Truncate long responses for demo
            display_response = response[:200] + "..." if len(response) > 200 else response
            print(f"   💬 {display_response}")
            print(f"   ⏱️  {processing_time:.2f}s")
            
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
    
    print(f"\n✅ Demo hoàn thành!")


def main():
    """Main entry point"""
    chat = VietnameseInteractiveChat()
    chat.run()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Vietnamese CubeJS Chatbot - Interactive Chat Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Start interactive chat
  python main.py --demo       # Run demo mode
  python main.py --version    # Show version
        """
    )
    parser.add_argument("--demo", action="store_true", help="Run demo mode with sample questions")
    parser.add_argument("--version", action="version", version="Vietnamese CubeJS Chatbot v1.0")
    
    args = parser.parse_args()
    
    if args.demo:
        demo_mode()
    else:
        main() 