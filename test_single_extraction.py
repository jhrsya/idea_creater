#!/usr/bin/env python3
"""
测试单个论文的创新点提取
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.settings import settings
from src.extractor.innovation_extractor import InnovationExtractor
from src.utils.logger import setup_logger

def main():
    """主函数"""
    # 设置日志
    setup_logger()
    
    print("🔍 测试单个论文创新点提取...")
    print(f"API密钥配置: {'✅' if settings.DEEPSEEK_API_KEY else '❌'}")
    
    if not settings.DEEPSEEK_API_KEY:
        print("❌ 请先配置DEEPSEEK_API_KEY")
        return
    
    # 测试论文内容
    test_paper_content = """
    Title: Attention Is All You Need
    
    Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.
    
    Introduction: Recurrent neural networks, long short-term memory and gated recurrent neural networks in particular, have been firmly established as state of the art approaches in sequence modeling and transduction problems such as language modeling and machine translation. Numerous efforts have since continued to push the boundaries of recurrent language models and encoder-decoder architectures.
    
    Method: We propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output. The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder.
    
    Results: On the WMT 2014 English-to-German translation task, we achieve a new state-of-the-art BLEU score of 28.4, improving over the existing best results, including ensembles, by over 2 BLEU points. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight P100 GPUs.
    
    Conclusion: We presented the Transformer, the first sequence transduction model based entirely on attention, replacing the recurrent layers most commonly used in encoder-decoder architectures with multi-headed self-attention. The Transformer can be trained significantly more quickly than architectures based on recurrent or convolutional layers.
    """
    
    test_paper_title = "Attention Is All You Need"
    
    try:
        print(f"\n📄 测试论文: {test_paper_title}")
        print(f"📝 论文内容长度: {len(test_paper_content)} 字符")
        
        # 创建提取器
        extractor = InnovationExtractor()
        
        # 提取创新点
        print("\n🤖 开始提取创新点...")
        result = extractor.extract_innovations(test_paper_content, test_paper_title)
        
        if result:
            print("✅ 创新点提取成功！")
            print(f"📊 论文标题: {result.paper_title}")
            print(f"📝 论文总结: {result.summary}")
            print(f"💡 创新点数量: {len(result.innovations)}")
            
            for i, innovation in enumerate(result.innovations, 1):
                print(f"\n🔹 创新点 {i}:")
                print(f"   标题: {innovation.title}")
                print(f"   描述: {innovation.description[:100]}...")
                print(f"   类别: {innovation.category}")
                print(f"   新颖性: {innovation.novelty_score:.2f}")
                print(f"   置信度: {innovation.confidence:.2f}")
        else:
            print("❌ 创新点提取失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")

if __name__ == "__main__":
    main() 