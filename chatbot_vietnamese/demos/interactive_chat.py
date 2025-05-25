#!/usr/bin/env python3
"""
Interactive Vietnamese Farm Chatbot
Chế độ chat tương tác cho Chatbot Nông nghiệp Việt Nam
"""

import os
import sys
import signal
from typing import Optional
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from chatbot_vietnamese.farm_chatbot import FarmVietnameseChatbot
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class InteractiveVietnameseChatbot:
    """Interactive Vietnamese Farm Chatbot Interface"""
    
    def __init__(self):
        self.chatbot: Optional[FarmVietnameseChatbot] = None
        self.session_id: Optional[str] = None
        self.running = True
        
        # Setup signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Đang thoát chương trình...")
        self.running = False
        if self.chatbot:
            self.chatbot.end_session()
        sys.exit(0)
    
    def _print_banner(self):
        """Print welcome banner"""
        print("=" * 80)
        print("🌱 CHATBOT NÔNG NGHIỆP THÔNG MINH - CHẾ ĐỘ TƯƠNG TÁC 🌱")
        print("=" * 80)
        print("🚀 Chào mừng bạn đến với hệ thống phân tích dữ liệu nông nghiệp!")
        print("💬 Hãy đặt câu hỏi bằng tiếng Việt về kinh doanh nông nghiệp")
        print("📊 Tôi có thể phân tích dữ liệu từ CubeJS và đưa ra khuyến nghị")
        print("=" * 80)
        print("⌨️  Gõ 'help' để xem hướng dẫn")
        print("⌨️  Gõ 'status' để kiểm tra trạng thái hệ thống")
        print("⌨️  Gõ 'history' để xem lịch sử chat")
        print("⌨️  Gõ 'exit' hoặc Ctrl+C để thoát")
        print("=" * 80)
    
    def _get_config_from_env(self) -> dict:
        """Get configuration from environment variables"""
        config = {
            "postgres_connection": os.getenv(
                "POSTGRES_CONNECTION", 
                "postgresql://postgres:password@localhost:5432/golett"
            ),
            "cubejs_api_url": os.getenv(
                "CUBEJS_API_URL", 
                "http://localhost:4000/cubejs-api/v1"
            ),
            "cubejs_api_token": os.getenv("CUBEJS_API_TOKEN"),
            "cubejs_schemas_path": os.getenv(
                "CUBEJS_SCHEMAS_PATH", 
                "cubejs/model/cubes"
            ),
            "qdrant_url": os.getenv("QDRANT_URL", "http://localhost:6333"),
            "knowledge_file_path": os.getenv(
                "KNOWLEDGE_FILE_PATH", 
                "farm_data/farm_business_domain_knowledge_vietnamese.md"
            ),
            "llm_model": os.getenv("LLM_MODEL", "gpt-4o"),
            "user_id": os.getenv("USER_ID", "interactive_user")
        }
        return config
    
    def _initialize_chatbot(self) -> bool:
        """Initialize the chatbot with configuration"""
        try:
            print("🔄 Đang khởi tạo hệ thống...")
            
            config = self._get_config_from_env()
            
            # Check required environment variables
            if not config["cubejs_api_token"]:
                print("⚠️  Cảnh báo: CUBEJS_API_TOKEN chưa được thiết lập")
                print("   Một số tính năng CubeJS có thể không hoạt động")
            
            # Initialize chatbot
            self.chatbot = FarmVietnameseChatbot(
                postgres_connection=config["postgres_connection"],
                cubejs_api_url=config["cubejs_api_url"],
                cubejs_api_token=config["cubejs_api_token"],
                cubejs_schemas_path=config["cubejs_schemas_path"],
                qdrant_url=config["qdrant_url"],
                knowledge_file_path=config["knowledge_file_path"],
                llm_model=config["llm_model"],
                user_id=config["user_id"]
            )
            
            # Start session
            self.session_id = self.chatbot.start_session({
                "mode": "interactive",
                "interface": "terminal"
            })
            
            print(f"✅ Hệ thống đã sẵn sàng! (Session: {self.session_id[:8]}...)")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khởi tạo hệ thống: {e}")
            print("💡 Hãy kiểm tra:")
            print("   - PostgreSQL đang chạy")
            print("   - Qdrant đang chạy") 
            print("   - CubeJS API đang chạy")
            print("   - Biến môi trường đã được thiết lập")
            return False
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands, return True if handled"""
        command = user_input.lower().strip()
        
        if command in ['exit', 'quit', 'thoát']:
            print("👋 Cảm ơn bạn đã sử dụng chatbot! Tạm biệt!")
            self.running = False
            return True
        
        elif command == 'help':
            print(self.chatbot.get_help_message())
            return True
        
        elif command == 'status':
            status = self.chatbot.get_system_status()
            print("\n📊 TRẠNG THÁI HỆ THỐNG:")
            print("-" * 40)
            for component, status_text in status.items():
                print(f"  {component}: {status_text}")
            print("-" * 40)
            return True
        
        elif command == 'history':
            history = self.chatbot.get_session_history(limit=10)
            print(f"\n📜 LỊCH SỬ CHAT (10 tin nhắn gần nhất):")
            print("-" * 50)
            if history:
                for i, msg in enumerate(history[-10:], 1):
                    role = msg.get("data", {}).get("role", "unknown")
                    content = msg.get("data", {}).get("content", "")
                    timestamp = msg.get("metadata", {}).get("timestamp", "")
                    
                    # Truncate long messages
                    if len(content) > 100:
                        content = content[:97] + "..."
                    
                    print(f"  {i}. [{role}] {content}")
                    if timestamp:
                        print(f"      ⏰ {timestamp}")
            else:
                print("  Chưa có lịch sử chat")
            print("-" * 50)
            return True
        
        elif command == 'clear':
            os.system('clear' if os.name == 'posix' else 'cls')
            self._print_banner()
            return True
        
        elif command == 'metrics':
            metrics = self.chatbot.get_available_metrics()
            print("\n📈 CÁC CHỈ SỐ CÓ SẴN:")
            print("-" * 40)
            for category, metric_list in metrics.items():
                print(f"  📊 {category}:")
                for metric in metric_list:
                    print(f"    • {metric}")
            print("-" * 40)
            return True
        
        elif command == 'collections':
            collections = self.chatbot.get_knowledge_collections()
            print("\n📚 BỘ SƯU TẬP TRI THỨC:")
            print("-" * 40)
            for name, info in collections.items():
                print(f"  📖 {name}: {info}")
            print("-" * 40)
            return True
        
        return False
    
    def _format_response(self, response: str) -> str:
        """Format the chatbot response for better display"""
        # Add some visual formatting
        formatted = f"🤖 **Chuyên gia nông nghiệp:**\n{response}"
        return formatted
    
    def run(self):
        """Run the interactive chat interface"""
        self._print_banner()
        
        # Initialize chatbot
        if not self._initialize_chatbot():
            return
        
        print("\n💬 Bắt đầu cuộc trò chuyện! Hãy đặt câu hỏi...")
        print("=" * 80)
        
        # Main chat loop
        while self.running:
            try:
                # Get user input
                user_input = input("\n👤 Bạn: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if self._handle_special_commands(user_input):
                    continue
                
                # Process with chatbot
                print("🔄 Đang xử lý...")
                response = self.chatbot.chat(user_input)
                
                # Display response
                print("\n" + "=" * 80)
                print(self._format_response(response))
                print("=" * 80)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Đang thoát...")
                break
            except EOFError:
                print("\n\n👋 Tạm biệt!")
                break
            except Exception as e:
                print(f"\n❌ Lỗi: {e}")
                print("💡 Hãy thử lại hoặc gõ 'help' để xem hướng dẫn")
        
        # Cleanup
        if self.chatbot:
            print("\n🔄 Đang lưu phiên chat...")
            self.chatbot.end_session()
            print("✅ Đã lưu thành công!")

def main():
    """Main function"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Yêu cầu Python 3.8 trở lên")
            sys.exit(1)
        
        # Check OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Thiếu OPENAI_API_KEY trong biến môi trường")
            print("💡 Hãy thiết lập: export OPENAI_API_KEY='your-api-key'")
            sys.exit(1)
        
        # Run interactive chat
        chat_interface = InteractiveVietnameseChatbot()
        chat_interface.run()
        
    except Exception as e:
        print(f"❌ Lỗi khởi động: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 