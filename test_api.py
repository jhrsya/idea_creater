 #!/usr/bin/env python3
"""
测试API调用
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.settings import settings
from src.utils.ai_client import call_ai
from loguru import logger

def test_api_connection():
    """测试API连接"""
    print("🔍 测试API连接...")
    # print(f"API密钥: {settings.DEEPSEEK_API_KEY[:10]}...")
    print(f"模型: {settings.DEEPSEEK_MODEL}")
    print(f"基础URL: https://api.deepseek.com/v1")
    
    try:
        # 简单的测试提示
        test_prompt = "请简单介绍一下机器学习，用一句话回答即可。"
        
        print("\n📤 发送测试请求...")
        response = call_ai(test_prompt)
        
        if response:
            print("✅ API调用成功！")
            print(f"📝 响应内容: {response}")
            return True
        else:
            print("❌ API调用失败：返回空响应")
            return False
            
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        return False

def test_innovation_extraction():
    """测试创新点提取"""
    print("\n🧪 测试创新点提取...")
    
    # 模拟论文内容
    test_paper = """
    Title: A Novel Approach to Machine Learning Optimization
    
    Abstract: This paper presents a new optimization algorithm that combines gradient descent with evolutionary strategies to achieve faster convergence in neural network training.
    
    Introduction: Traditional optimization methods often struggle with local minima...
    
    Method: We propose a hybrid approach that uses genetic algorithms to escape local minima while maintaining the efficiency of gradient-based methods...
    
    Results: Our method achieves 30% faster convergence compared to Adam optimizer on benchmark datasets...
    
    Conclusion: The proposed method shows significant improvements in both speed and accuracy...
    """
    
    try:
        from src.extractor.innovation_extractor import InnovationExtractor
        
        extractor = InnovationExtractor()
        result = extractor.extract_innovations(test_paper, "A Novel Approach to Machine Learning Optimization")
        
        if result:
            print("✅ 创新点提取成功！")
            print(f"📊 提取到 {len(result.innovations)} 个创新点")
            for i, innovation in enumerate(result.innovations, 1):
                print(f"  {i}. {innovation.title}")
            return True
        else:
            print("❌ 创新点提取失败")
            return False
            
    except Exception as e:
        print(f"❌ 创新点提取失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        return False

def main():
    """主函数"""
    print("🚀 开始API测试...")
    
    # 测试基本API连接
    api_ok = test_api_connection()
    
    if api_ok:
        # 测试创新点提取
        extraction_ok = test_innovation_extraction()
        
        if extraction_ok:
            print("\n🎉 所有测试通过！")
        else:
            print("\n⚠️ 创新点提取测试失败")
    else:
        print("\n❌ API连接测试失败，请检查配置")

if __name__ == "__main__":
    main()