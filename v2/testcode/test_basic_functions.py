import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app_v2 import (
    count_chinese_chars,
    paragraph_count,
    sentence_count,
    has_beginning_middle_end,
    structure_level,
    expression_level,
    GRADE_OPTIONS,
    GENRE_OPTIONS,
    DEFAULT_TOPICS,
    GRADE_RUBRICS,
    GRADE_WORDS,
    TEMPLATES
)


class TestBasicFunctions(unittest.TestCase):
    """测试基础功能函数"""
    
    def test_count_chinese_chars(self):
        """测试中文字符计数功能"""
        self.assertEqual(count_chinese_chars(""), 0)
        self.assertEqual(count_chinese_chars("你好"), 2)
        self.assertEqual(count_chinese_chars("Hello 世界"), 2)
        self.assertEqual(count_chinese_chars("今天天气真好！"), 6)
        self.assertEqual(count_chinese_chars("123中文abc"), 2)
    
    def test_count_chinese_chars_with_special_chars(self):
        """测试包含特殊字符的中文字符计数"""
        text = "这是一篇作文！包含标点符号，数字123，字母abc。"
        self.assertEqual(count_chinese_chars(text), 16)
    
    def test_count_chinese_chars_edge_cases(self):
        """测试中文字符计数的边界情况"""
        # 全角字符测试
        self.assertEqual(count_chinese_chars("ａｂｃ１２３"), 0)
        # 中文标点测试
        self.assertEqual(count_chinese_chars("，。！？：；""''"), 0)
        # 混合文本测试
        self.assertEqual(count_chinese_chars("Hello 世界123你好abc"), 4)
    
    def test_paragraph_count(self):
        """测试段落计数功能"""
        self.assertEqual(paragraph_count(""), 1)
        self.assertEqual(paragraph_count("这是一段文字。"), 1)
        self.assertEqual(paragraph_count("第一段\n第二段"), 2)
        self.assertEqual(paragraph_count("第一段\n\n第二段"), 2)
        self.assertEqual(paragraph_count("第一段\n\n\n第二段\n第三段"), 3)
    
    def test_sentence_count(self):
        """测试句子计数功能"""
        self.assertEqual(sentence_count(""), 1)
        self.assertEqual(sentence_count("这是一个句子。"), 1)
        self.assertEqual(sentence_count("这是第一个句子。这是第二个句子！"), 2)
        self.assertEqual(sentence_count("Hello. World!"), 2)
        self.assertEqual(sentence_count("这是句子？是的！"), 2)
    
    def test_has_beginning_middle_end(self):
        """测试文章结构完整性检查"""
        # 段落数足够
        self.assertTrue(has_beginning_middle_end("第一段\n第二段\n第三段"))
        # 句子数足够
        self.assertTrue(has_beginning_middle_end("第一句。第二句。第三句。第四句。第五句。"))
        # 段落数不足但句子数足够
        self.assertTrue(has_beginning_middle_end("第一句。第二句。第三句。第四句。第五句。第六句。"))
        # 都不足
        self.assertFalse(has_beginning_middle_end("第一句。第二句。"))
    
    def test_structure_level(self):
        """测试结构水平评估"""
        # 较完整（3个段落，每个段落至少2个句子）
        self.assertEqual(structure_level("第一段第一句。第一段第二句。\n第二段第一句。第二段第二句。\n第三段第一句。第三段第二句。"), "较完整")
        # 基本完整（4个句子）
        self.assertEqual(structure_level("第一段。第二段。第三段。第四句。"), "基本完整")
        # 待加强（只有2个句子）
        self.assertEqual(structure_level("第一句。第二句。"), "待加强")
    
    def test_expression_level(self):
        """测试表达水平评估"""
        # 较丰富
        self.assertEqual(expression_level("好像他在笑，心里很高兴，于是就跑过去。"), "较丰富")
        # 一般
        self.assertEqual(expression_level("他笑了，心里很高兴。"), "一般")
        # 待丰富
        self.assertEqual(expression_level("他很高兴。"), "待丰富")
    
    def test_constants_validation(self):
        """测试常量定义的有效性"""
        self.assertIsInstance(GRADE_OPTIONS, list)
        self.assertIsInstance(GENRE_OPTIONS, list)
        self.assertIsInstance(DEFAULT_TOPICS, list)
        self.assertIsInstance(GRADE_RUBRICS, dict)
        self.assertIsInstance(GRADE_WORDS, dict)
        self.assertIsInstance(TEMPLATES, dict)
        
        self.assertTrue(len(GRADE_OPTIONS) > 0)
        self.assertTrue(len(GENRE_OPTIONS) > 0)
        self.assertTrue(len(DEFAULT_TOPICS) > 0)
        self.assertTrue(len(GRADE_RUBRICS) > 0)
        self.assertTrue(len(GRADE_WORDS) > 0)
        self.assertTrue(len(TEMPLATES) > 0)
    
    def test_constants_content_validation(self):
        """测试常量内容的有效性"""
        # 验证年级选项包含预期值
        self.assertIn("三年级", GRADE_OPTIONS)
        self.assertIn("六年级", GRADE_OPTIONS)
        
        # 验证作文类型选项包含预期值
        self.assertIn("写人", GENRE_OPTIONS)
        self.assertIn("写事", GENRE_OPTIONS)
        self.assertIn("看图作文", GENRE_OPTIONS)
        
        # 验证年级评分标准
        self.assertIn("三年级", GRADE_RUBRICS)
        self.assertIn("六年级", GRADE_RUBRICS)
        self.assertEqual(len(GRADE_RUBRICS["三年级"]), 5)
        self.assertEqual(len(GRADE_RUBRICS["六年级"]), 5)
        
        # 验证年级字数要求
        for grade in GRADE_OPTIONS:
            self.assertIn(grade, GRADE_WORDS)
            self.assertIsInstance(GRADE_WORDS[grade], tuple)
            self.assertEqual(len(GRADE_WORDS[grade]), 2)
        
        # 验证模板库
        for genre in ["写人", "写事", "写景", "想象作文", "读后感", "日记", "看图作文"]:
            self.assertIn(genre, TEMPLATES)
            self.assertIn("框架", TEMPLATES[genre])
            self.assertIn("句式", TEMPLATES[genre])


if __name__ == '__main__':
    unittest.main()