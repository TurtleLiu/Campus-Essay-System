import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app import (
    count_chinese_chars,
    fallback_feedback,
    build_user_prompt,
    call_llm,
    make_revision_prompt,
    revise_guidance,
    RUBRIC
)


class TestSystemIntegration(unittest.TestCase):
    """系统测试 - 测试模块间交互"""
    
    def test_full_essay_review_flow(self):
        """测试完整的作文点评流程"""
        # 测试数据
        grade = "四年级"
        genre = "记叙文"
        theme = "难忘的一天"
        goal_words = 300
        essay = "今天我和爸爸妈妈一起去公园玩。公园里的花儿开得很美，我们还看到了小松鼠。我们玩得很开心，这真是难忘的一天。"
        
        # 步骤1: 构建用户提示
        prompt = build_user_prompt(grade, genre, theme, goal_words, essay)
        
        # 验证提示包含所有必要信息
        self.assertIn(f"学生年级：{grade}", prompt)
        self.assertIn(f"作文类型：{genre}", prompt)
        self.assertIn(f"主题：{theme}", prompt)
        self.assertIn(f"目标字数：{goal_words}", prompt)
        self.assertIn(essay, prompt)
        
        # 步骤2: 调用LLM获取反馈（回退模式）
        feedback = call_llm(grade, genre, theme, goal_words, essay)
        
        # 验证反馈结构完整性
        self.assertIn("summary", feedback)
        self.assertIn("scores", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("improvements", feedback)
        
        # 步骤3: 生成修改提示
        revision_prompt = make_revision_prompt(essay, feedback)
        
        # 验证修改提示包含必要信息
        self.assertIn(essay, revision_prompt)
        self.assertIn("引导式修改建议", revision_prompt)
        
        # 步骤4: 生成修改指导
        guidance = revise_guidance(essay, feedback)
        
        # 验证修改指导包含三个部分
        self.assertIn("可以先补充", guidance)
        self.assertIn("可以改写", guidance)
        self.assertIn("参考开头", guidance)
    
    def test_character_count_and_feedback_integration(self):
        """测试字符计数与反馈生成的集成"""
        essay = "这是一篇测试作文。今天天气很好，阳光明媚，我和朋友们一起去郊外游玩。我们在草地上野餐，玩游戏，度过了愉快的一天。"
        
        # 计算中文字符数
        char_count = count_chinese_chars(essay)
        
        # 根据字符数判断是否为短作文
        is_short = char_count < 120
        
        # 获取反馈
        feedback = fallback_feedback(essay)
        
        # 验证反馈与作文长度的关系
        if is_short:
            self.assertIn("篇幅偏短", feedback["summary"])
            self.assertEqual(feedback["scores"]["细节描写"], 5)
        else:
            self.assertIn("完整主题", feedback["summary"])
            self.assertEqual(feedback["scores"]["细节描写"], 6)
    
    def test_rubric_consistency_across_modules(self):
        """测试评分维度在各模块间的一致性"""
        # 测试数据
        grade = "五年级"
        genre = "写人"
        theme = "我的好朋友"
        goal_words = 400
        essay = "我的好朋友小明是一个很有趣的人。他总是乐于助人，学习也很努力。我们经常一起学习和玩耍。"
        
        # 构建提示
        prompt = build_user_prompt(grade, genre, theme, goal_words, essay)
        
        # 验证提示中包含所有评分维度
        for rubric_key in RUBRIC.keys():
            self.assertIn(rubric_key, prompt)
        
        # 获取反馈
        feedback = call_llm(grade, genre, theme, goal_words, essay)
        
        # 验证反馈中的评分维度与RUBRIC一致
        scores = feedback.get("scores", {})
        for rubric_key in RUBRIC.keys():
            self.assertIn(rubric_key, scores)
            # 验证分数范围
            self.assertTrue(0 <= scores[rubric_key] <= 10)
    
    def test_error_handling_in_integration(self):
        """测试集成过程中的错误处理"""
        # 测试空作文的处理
        feedback = call_llm("三年级", "记叙文", "测试主题", 300, "")
        
        # 验证即使输入为空，系统也能正常返回反馈
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
        
        # 测试生成修改指导时的空反馈处理
        empty_feedback = {"strengths": [], "improvements": []}
        guidance = revise_guidance("测试作文", empty_feedback)
        
        # 验证回退机制正常工作
        self.assertIn("可以先补充", guidance)
    
    def test_full_workflow_with_short_essay(self):
        """测试完整工作流程（短作文场景）"""
        # 短作文测试数据
        short_essay = "很短。"
        grade = "三年级"
        genre = "记叙文"
        theme = "难忘的一天"
        goal_words = 300
        
        # 完整流程测试
        feedback = call_llm(grade, genre, theme, goal_words, short_essay)
        
        # 验证短作文的反馈特征
        self.assertIn("篇幅偏短", feedback["summary"])
        self.assertEqual(feedback["scores"]["细节描写"], 5)
        
        # 生成修改指导
        guidance = revise_guidance(short_essay, feedback)
        
        # 验证修改指导包含适合短作文的建议
        self.assertIn("可以先补充", guidance)
    
    def test_full_workflow_with_normal_essay(self):
        """测试完整工作流程（正常长度作文场景）"""
        # 正常长度作文测试数据
        normal_essay = "今天是周末，我和家人一起去公园游玩。公园里人很多，有小朋友在玩耍，有老人在散步。我们在湖边喂了鸭子，还拍了很多照片。中午我们在公园里野餐，吃了美味的食物。下午我们去了游乐场，玩了过山车和旋转木马。晚上回家的时候，大家都觉得很累但很开心。这真是难忘的一天。"
        grade = "四年级"
        genre = "记叙文"
        theme = "难忘的一天"
        goal_words = 400
        
        # 完整流程测试
        feedback = call_llm(grade, genre, theme, goal_words, normal_essay)
        
        # 验证正常作文的反馈特征
        self.assertIn("完整主题", feedback["summary"])
        self.assertEqual(feedback["scores"]["细节描写"], 6)
        
        # 生成修改指导
        guidance = revise_guidance(normal_essay, feedback)
        
        # 验证修改指导包含适合正常作文的建议
        self.assertIn("可以改写", guidance)
        self.assertIn("参考开头", guidance)


if __name__ == '__main__':
    unittest.main()