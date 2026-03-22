import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app import (
    count_chinese_chars,
    call_llm,
    revise_guidance,
    GRADE_OPTIONS,
    GENRE_OPTIONS,
    THEME_OPTIONS,
    RUBRIC
)


class TestAcceptance(unittest.TestCase):
    """验收测试 - 验证完整业务流程"""
    
    def test_user_story_grade_3_narrative_essay(self):
        """用户故事测试：三年级学生写记叙文"""
        # 用户故事：三年级学生写一篇题为"难忘的一天"的记叙文
        grade = "三年级"
        genre = "记叙文"
        theme = "难忘的一天"
        goal_words = 300
        
        # 学生输入的作文
        essay = "今天是我的生日，爸爸妈妈给我买了一个大蛋糕。我邀请了很多好朋友来参加我的生日派对。我们一起唱生日歌，吃蛋糕，玩游戏。我收到了很多礼物，非常开心。这真是难忘的一天。"
        
        # 验证输入验证
        self.assertTrue(len(essay) > 0)
        char_count = count_chinese_chars(essay)
        self.assertTrue(char_count > 0)
        
        # 获取反馈
        feedback = call_llm(grade, genre, theme, goal_words, essay)
        
        # 验收标准1：反馈结构完整
        required_fields = ["summary", "scores", "strengths", "improvements", "sentence_polish", "outline_advice", "encouragement"]
        for field in required_fields:
            self.assertIn(field, feedback, f"反馈缺少必要字段: {field}")
        
        # 验收标准2：评分维度完整
        for rubric_key in RUBRIC.keys():
            self.assertIn(rubric_key, feedback["scores"], f"评分缺少维度: {rubric_key}")
        
        # 验收标准3：反馈内容符合三年级水平
        self.assertIsInstance(feedback["summary"], str)
        self.assertTrue(len(feedback["summary"]) > 0)
        
        # 验收标准4：修改指导功能正常
        guidance = revise_guidance(essay, feedback)
        self.assertIsInstance(guidance, str)
        self.assertTrue(len(guidance) > 0)
    
    def test_user_story_grade_5_descriptive_essay(self):
        """用户故事测试：五年级学生写写景作文"""
        # 用户故事：五年级学生写一篇题为"秋天来了"的写景作文
        grade = "五年级"
        genre = "写景"
        theme = "秋天来了"
        goal_words = 400
        
        # 学生输入的作文
        essay = "秋天来了，天气变得凉爽起来。树上的叶子变黄了，一片片飘落下来，像一只只黄色的蝴蝶。果园里的果子成熟了，红彤彤的苹果，黄澄澄的梨子，看起来非常诱人。秋天是一个丰收的季节，也是一个美丽的季节。"
        
        # 获取反馈
        feedback = call_llm(grade, genre, theme, goal_words, essay)
        
        # 验收标准：反馈内容适合五年级学生
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
        
        # 验证评分在合理范围内
        scores = feedback.get("scores", {})
        for score in scores.values():
            self.assertTrue(0 <= score <= 10, f"分数 {score} 超出合理范围")
        
        # 验证修改指导生成
        guidance = revise_guidance(essay, feedback)
        self.assertIn("可以先补充", guidance)
    
    def test_user_story_short_essay_handling(self):
        """用户故事测试：短作文处理"""
        # 用户故事：学生提交了一篇很短的作文
        grade = "四年级"
        genre = "记叙文"
        theme = "我的周末"
        goal_words = 300
        
        # 很短的作文
        short_essay = "我的周末很开心。"
        
        # 获取反馈
        feedback = call_llm(grade, genre, theme, goal_words, short_essay)
        
        # 验收标准：系统能正确处理短作文
        self.assertIn("篇幅偏短", feedback["summary"])
        self.assertEqual(feedback["scores"]["细节描写"], 5)
        
        # 验证修改指导给出适合短作文的建议
        guidance = revise_guidance(short_essay, feedback)
        self.assertIn("可以先补充", guidance)
    
    def test_user_story_empty_input_handling(self):
        """用户故事测试：空输入处理"""
        # 用户故事：学生提交了空作文
        grade = "三年级"
        genre = "记叙文"
        theme = "难忘的一天"
        goal_words = 300
        
        # 空作文
        empty_essay = ""
        
        # 获取反馈（应该使用回退机制）
        feedback = call_llm(grade, genre, theme, goal_words, empty_essay)
        
        # 验收标准：系统不会崩溃，能返回合理的反馈
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
        
        # 验证修改指导功能
        guidance = revise_guidance(empty_essay, feedback)
        self.assertIsInstance(guidance, str)
    
    def test_user_story_complex_essay_with_dialogue(self):
        """用户故事测试：包含对话的复杂作文"""
        # 用户故事：学生写了一篇包含对话的作文
        grade = "六年级"
        genre = "记叙文"
        theme = "一次有趣的活动"
        goal_words = 500
        
        # 包含对话的作文
        essay = """今天我们班组织了一次有趣的活动。老师说："同学们，今天我们要去科技馆参观。"大家听了都很高兴。
        
到了科技馆，我们看到了很多有趣的科学展品。小明问："这个机器人是怎么工作的？"老师回答："它是通过程序控制的。"
        
最有趣的是那个会跳舞的机器人，它随着音乐跳来跳去，逗得大家哈哈大笑。
        
这次活动让我学到了很多科学知识，真是一次难忘的经历。"""
        
        # 获取反馈
        feedback = call_llm(grade, genre, theme, goal_words, essay)
        
        # 验收标准：系统能正确处理包含对话的作文
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
        
        # 验证修改指导
        guidance = revise_guidance(essay, feedback)
        self.assertIsInstance(guidance, str)
        self.assertTrue(len(guidance) > 0)
    
    def test_acceptance_criteria_output_format(self):
        """验收标准：输出格式验证"""
        grade = "四年级"
        genre = "写人"
        theme = "我的好朋友"
        goal_words = 350
        essay = "我的好朋友叫小红。她有一双大大的眼睛，长长的头发。她学习很好，也很乐于助人。我们经常一起上学，一起做作业。我很喜欢和她做朋友。"
        
        feedback = call_llm(grade, genre, theme, goal_words, essay)
        
        # 验收标准1：反馈是字典格式
        self.assertIsInstance(feedback, dict)
        
        # 验收标准2：scores是字典
        self.assertIsInstance(feedback.get("scores", {}), dict)
        
        # 验收标准3：strengths和improvements是列表
        self.assertIsInstance(feedback.get("strengths", []), list)
        self.assertIsInstance(feedback.get("improvements", []), list)
        
        # 验收标准4：sentence_polish是列表
        self.assertIsInstance(feedback.get("sentence_polish", []), list)
        
        # 验收标准5：outline_advice是列表
        self.assertIsInstance(feedback.get("outline_advice", []), list)
        
        # 验收标准6：encouragement是字符串
        self.assertIsInstance(feedback.get("encouragement", ""), str)
    
    def test_acceptance_criteria_content_quality(self):
        """验收标准：内容质量验证"""
        grade = "五年级"
        genre = "想象作文"
        theme = "假如我会飞"
        goal_words = 400
        essay = "假如我会飞，我要飞到天空中，和小鸟一起玩耍。我要飞到高高的山顶，看看美丽的风景。我要飞到大海边，看看蓝色的大海。假如我会飞，那该多好啊！"
        
        feedback = call_llm(grade, genre, theme, goal_words, essay)
        
        # 验收标准1：优点至少有3条
        strengths = feedback.get("strengths", [])
        self.assertTrue(len(strengths) >= 3, f"优点数量不足，只有 {len(strengths)} 条")
        
        # 验收标准2：改进建议至少有3条
        improvements = feedback.get("improvements", [])
        self.assertTrue(len(improvements) >= 3, f"改进建议数量不足，只有 {len(improvements)} 条")
        
        # 验收标准3：句子优化至少有2条
        sentence_polish = feedback.get("sentence_polish", [])
        self.assertTrue(len(sentence_polish) >= 2, f"句子优化数量不足，只有 {len(sentence_polish)} 条")
        
        # 验收标准4：补写提纲建议至少有3条
        outline_advice = feedback.get("outline_advice", [])
        self.assertTrue(len(outline_advice) >= 3, f"补写提纲建议数量不足，只有 {len(outline_advice)} 条")


if __name__ == '__main__':
    unittest.main()