import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app_v2 import (
    get_client,
    rubric_for_grade,
    score_keys,
    fallback_feedback,
    build_feedback_prompt,
    call_feedback_llm,
    build_compare_prompt,
    fallback_compare,
    compare_with_sample,
    stepwise_rewrite_prompt,
    fallback_stepwise,
    stepwise_rewrite,
    generate_titles,
    generate_topic_options,
    fallback_image_prompts,
    SYSTEM_PROMPT
)


class TestLLMFunctions(unittest.TestCase):
    """测试LLM相关功能（v2版本）"""
    
    def test_get_client(self):
        """测试获取OpenAI客户端"""
        client = get_client()
        # 如果OpenAI库不可用，应该返回None
        # 这个测试主要确保函数不会抛出异常
        try:
            result = get_client()
            self.assertIsInstance(result, (type(None), object))
        except Exception:
            self.fail("get_client() raised exception unexpectedly")
    
    def test_rubric_for_grade(self):
        """测试根据年级获取评分标准"""
        # 三年级评分标准
        rubric_3 = rubric_for_grade("三年级")
        self.assertIsInstance(rubric_3, dict)
        self.assertEqual(len(rubric_3), 5)
        self.assertIn("审题与内容", rubric_3)
        
        # 六年级评分标准
        rubric_6 = rubric_for_grade("六年级")
        self.assertIsInstance(rubric_6, dict)
        self.assertEqual(len(rubric_6), 5)
        self.assertIn("审题与立意", rubric_6)
    
    def test_score_keys(self):
        """测试获取评分维度的键"""
        keys_3 = score_keys("三年级")
        self.assertIsInstance(keys_3, list)
        self.assertEqual(len(keys_3), 5)
        self.assertIn("审题与内容", keys_3)
        
        keys_6 = score_keys("六年级")
        self.assertIsInstance(keys_6, list)
        self.assertEqual(len(keys_6), 5)
        self.assertIn("审题与立意", keys_6)
    
    def test_build_feedback_prompt(self):
        """测试构建反馈提示"""
        prompt = build_feedback_prompt("三年级", "写人", "我的妈妈", "这是一篇测试作文。")
        
        # 验证提示包含所有必要信息
        self.assertIn("学生年级：三年级", prompt)
        self.assertIn("作文类型：写人", prompt)
        self.assertIn("主题：我的妈妈", prompt)
        self.assertIn("这是一篇测试作文。", prompt)
        
        # 验证包含评分维度
        self.assertIn("审题与内容", prompt)
        
        # 验证包含JSON格式要求
        self.assertIn("summary", prompt)
        self.assertIn("scores", prompt)
        self.assertIn("strengths", prompt)
        self.assertIn("improvements", prompt)
    
    def test_call_feedback_llm_fallback(self):
        """测试调用LLM反馈的回退功能"""
        feedback = call_feedback_llm("三年级", "写人", "我的妈妈", "这是一篇测试作文。")
        
        # 验证回退反馈的结构
        self.assertIn("summary", feedback)
        self.assertIn("scores", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("improvements", feedback)
        self.assertIn("teacher_feedback", feedback)
        self.assertIn("encouraging_feedback", feedback)
        self.assertIn("sentence_polish", feedback)
        self.assertIn("outline_advice", feedback)
        self.assertIn("revision_steps", feedback)
    
    def test_call_feedback_llm_short_essay(self):
        """测试短作文的反馈"""
        short_essay = "很短。"
        feedback = call_feedback_llm("三年级", "写事", "一次活动", short_essay)
        
        self.assertIn("内容还不够展开", feedback["summary"])
    
    def test_call_feedback_llm_normal_essay(self):
        """测试正常长度作文的反馈"""
        normal_essay = "这是一篇正常长度的作文。今天天气很好，我和同学们一起去公园玩。我们玩了很多游戏，非常开心。公园里的花儿开得很美，有红色的玫瑰、黄色的菊花，还有紫色的薰衣草。我们在草地上奔跑、追逐，玩得不亦乐乎。不知不觉中，太阳慢慢西沉，我们恋恋不舍地离开了公园。今天真是难忘的一天，我和朋友们度过了美好的时光。今天的天气格外晴朗，阳光洒在大地上，让人心情格外舒畅。我们在公园里看到了各种各样的花朵，它们争奇斗艳，美丽极了。"
        feedback = call_feedback_llm("三年级", "写景", "秋天的公园", normal_essay)
        
        self.assertIn("明确主题", feedback["summary"])
    
    def test_build_compare_prompt(self):
        """测试构建对比提示"""
        prompt = build_compare_prompt("三年级", "写人", "学生作文", "范文")
        
        self.assertIn("学生年级：三年级", prompt)
        self.assertIn("作文类型：写人", prompt)
        self.assertIn("学生作文：学生作文", prompt)
        self.assertIn("范文：范文", prompt)
    
    def test_fallback_compare(self):
        """测试回退对比功能"""
        result = fallback_compare("学生作文", "范文")
        
        self.assertIn("common_strengths", result)
        self.assertIn("missing_parts", result)
        self.assertIn("imitation_points", result)
        self.assertEqual(len(result["common_strengths"]), 2)
        self.assertEqual(len(result["missing_parts"]), 3)
        self.assertEqual(len(result["imitation_points"]), 3)
    
    def test_compare_with_sample(self):
        """测试与范文对比功能"""
        result = compare_with_sample("三年级", "写人", "学生作文", "范文")
        
        self.assertIn("common_strengths", result)
        self.assertIn("missing_parts", result)
        self.assertIn("imitation_points", result)
    
    def test_stepwise_rewrite_prompt(self):
        """测试构建分步改写提示"""
        feedback = {"summary": "测试反馈"}
        prompt = stepwise_rewrite_prompt("三年级", "测试作文", feedback)
        
        self.assertIn("学生年级：三年级", prompt)
        self.assertIn("作文：测试作文", prompt)
        self.assertIn("点评：", prompt)
    
    def test_fallback_stepwise(self):
        """测试回退分步改写功能"""
        result = fallback_stepwise()
        
        self.assertIn("step1_add", result)
        self.assertIn("step2_rewrite", result)
        self.assertIn("step3_opening", result)
        self.assertIn("step4_ending", result)
    
    def test_stepwise_rewrite(self):
        """测试分步改写功能"""
        feedback = {"summary": "测试反馈"}
        result = stepwise_rewrite("三年级", "测试作文", feedback)
        
        self.assertIn("step1_add", result)
        self.assertIn("step2_rewrite", result)
        self.assertIn("step3_opening", result)
        self.assertIn("step4_ending", result)
    
    def test_generate_topic_options(self):
        """测试生成主题选项"""
        topics = generate_topic_options("三年级", "写人")
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) > 0)
        
        topics_with_interest = generate_topic_options("三年级", "写人", "足球")
        self.assertIsInstance(topics_with_interest, list)
        self.assertTrue(len(topics_with_interest) > 0)
    
    def test_generate_titles(self):
        """测试生成作文题目"""
        titles = generate_titles("三年级", "写人", "妈妈")
        self.assertIsInstance(titles, list)
        self.assertTrue(len(titles) > 0)
        
        titles_no_keyword = generate_titles("三年级", "写人", "")
        self.assertIsInstance(titles_no_keyword, list)
        self.assertTrue(len(titles_no_keyword) > 0)
    
    def test_fallback_image_prompts(self):
        """测试回退图片提示功能"""
        prompts = fallback_image_prompts("三年级")
        
        self.assertIn("scene", prompts)
        self.assertIn("observe", prompts)
        self.assertIn("questions", prompts)
        self.assertIn("suggested_title", prompts)
        self.assertEqual(len(prompts["observe"]), 4)
        self.assertEqual(len(prompts["questions"]), 4)
    
    def test_system_prompt_constant(self):
        """测试系统提示常量"""
        self.assertIsInstance(SYSTEM_PROMPT, str)
        self.assertTrue(len(SYSTEM_PROMPT) > 0)
        self.assertIn("耐心、温和、擅长启发式教学", SYSTEM_PROMPT)
        self.assertIn("语言简单，鼓励性强", SYSTEM_PROMPT)


if __name__ == '__main__':
    unittest.main()