#!/usr/bin/env python3
"""
启动Streamlit UI的脚本
"""
import subprocess
import sys
import os

def main():
    """启动Streamlit应用"""
    # 确保在正确的目录中
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 启动Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "src/ui/streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "localhost"
    ]
    
    print("🚀 启动智能论文创新点生成器...")
    print("📱 访问地址: http://localhost:8501")
    print("🛑 按 Ctrl+C 停止服务")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")

if __name__ == "__main__":
    main() 