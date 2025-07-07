#!/usr/bin/env python3
"""
智能论文创新点生成器 - 启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'arxiv', 'requests',
        'pdfplumber', 'PyPDF2', 'openai', 'anthropic', 'loguru'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True


def check_config():
    """检查配置文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ 未找到.env配置文件")
        print("正在创建示例配置文件...")
        
        env_content = """# AI API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 其他配置
DEBUG=True
LOG_LEVEL=INFO
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ 已创建.env配置文件")
        print("⚠️  请编辑.env文件，添加你的API密钥")
        return False
    
    print("✅ 配置文件存在")
    return True


def create_directories():
    """创建必要的目录"""
    directories = [
        "data",
        "data/papers",
        "data/extracted", 
        "data/innovations",
        "data/results",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构已创建")


def start_web_interface():
    """启动Web界面"""
    print("🚀 启动Web界面...")
    
    try:
        # 检查streamlit是否可用
        subprocess.run([sys.executable, "-c", "import streamlit"], check=True)
        
        # 启动streamlit应用
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "src/ui/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ]
        
        print("🌐 Web界面将在 http://localhost:8501 启动")
        subprocess.run(cmd)
        
    except subprocess.CalledProcessError:
        print("❌ Streamlit未安装，请运行: pip install streamlit")
    except FileNotFoundError:
        print("❌ 未找到streamlit应用文件")
    except KeyboardInterrupt:
        print("\n👋 已停止Web界面")


def show_menu():
    """显示主菜单"""
    while True:
        print("\n" + "="*50)
        print("🧠 智能论文创新点生成器")
        print("="*50)
        print("1. 启动Web界面")
        print("2. 运行完整示例")
        print("3. 搜索论文")
        print("4. 解析论文")
        print("5. 提取创新点")
        print("6. 生成新想法")
        print("7. 检查环境")
        print("0. 退出")
        print("-"*50)
        
        choice = input("请选择操作 (0-7): ").strip()
        
        if choice == "0":
            print("👋 再见!")
            break
        elif choice == "1":
            start_web_interface()
        elif choice == "2":
            run_example()
        elif choice == "3":
            search_papers()
        elif choice == "4":
            parse_papers()
        elif choice == "5":
            extract_innovations()
        elif choice == "6":
            generate_ideas()
        elif choice == "7":
            check_environment()
        else:
            print("❌ 无效选择，请重试")


def run_example():
    """运行完整示例"""
    print("🔬 运行完整示例...")
    try:
        subprocess.run([sys.executable, "example.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行示例失败: {e}")
    except KeyboardInterrupt:
        print("\n⏹️  示例已停止")


def search_papers():
    """搜索论文"""
    query = input("请输入搜索查询: ").strip()
    if not query:
        print("❌ 查询不能为空")
        return
    
    max_results = input("最大结果数量 (默认20): ").strip()
    max_results = int(max_results) if max_results.isdigit() else 20
    
    download = input("是否下载论文? (y/n, 默认n): ").strip().lower() == 'y'
    
    cmd = [sys.executable, "main.py", "search", "-q", query, "-m", str(max_results)]
    if download:
        cmd.append("-d")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 搜索失败: {e}")


def parse_papers():
    """解析论文"""
    print("📖 开始解析论文...")
    try:
        subprocess.run([sys.executable, "main.py", "parse"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 解析失败: {e}")


def extract_innovations():
    """提取创新点"""
    print("💡 开始提取创新点...")
    try:
        subprocess.run([sys.executable, "main.py", "extract"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 提取失败: {e}")


def generate_ideas():
    """生成新想法"""
    topic = input("请输入研究主题: ").strip()
    if not topic:
        print("❌ 主题不能为空")
        return
    
    try:
        subprocess.run([sys.executable, "main.py", "generate", "-t", topic], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 生成失败: {e}")


def check_environment():
    """检查环境"""
    print("🔍 检查环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查依赖
    deps_ok = check_dependencies()
    
    # 检查配置
    config_ok = check_config()
    
    # 检查目录
    create_directories()
    
    if deps_ok and config_ok:
        print("✅ 环境检查通过，可以开始使用")
    else:
        print("⚠️  环境检查发现问题，请解决后重试")


def main():
    """主函数"""
    print("🧠 智能论文创新点生成器")
    print("基于ArXiv论文分析，提取创新点并生成新的研究方向")
    
    # 检查环境
    if not check_dependencies():
        return
    
    # 创建目录
    create_directories()
    
    # 显示菜单
    show_menu()


if __name__ == "__main__":
    main() 