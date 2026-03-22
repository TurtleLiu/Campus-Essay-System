import unittest
import sys
import os
import json
import datetime
import subprocess

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def check_python_installation():
    """检查Python是否安装"""
    try:
        subprocess.run([sys.executable, "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_dependencies():
    """检查并安装项目依赖"""
    print("正在检查项目依赖...")
    
    dependencies = ['streamlit']
    
    for dep in dependencies:
        try:
            subprocess.run(
                [sys.executable, "-c", f"import {dep}; print('✅ {dep}已安装')"],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError:
            print(f"❌ 缺少依赖：{dep}")
            print(f"正在安装依赖：{dep}...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"✅ {dep}安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {dep}安装失败: {e.stderr}")
                return False
    return True


# 导入所有测试模块
from test_basic_functions import TestBasicFunctions
from test_llm_functions import TestLLMFunctions
from test_system_integration import TestSystemIntegration
from test_acceptance import TestAcceptance


class TestResultCollector(unittest.TestResult):
    """自定义测试结果收集器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    def startTest(self, test):
        self.start_time = datetime.datetime.now()
        super().startTest(test)
    
    def stopTest(self, test):
        self.end_time = datetime.datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # 记录测试结果
        test_info = {
            'test_name': test._testMethodName,
            'class_name': test.__class__.__name__,
            'status': 'passed',
            'duration': round(duration, 4),
            'message': ''
        }
        
        # 检查是否失败或出错
        for failure in self.failures:
            if failure[0] == test:
                test_info['status'] = 'failed'
                test_info['message'] = failure[1]
                break
        
        for error in self.errors:
            if error[0] == test:
                test_info['status'] = 'error'
                test_info['message'] = error[1]
                break
        
        self.test_results.append(test_info)
        super().stopTest(test)


def run_all_tests():
    """运行所有测试并收集详细结果"""
    print("开始运行 v1 版本测试套件...")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例 - 使用TestLoader替代makeSuite
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestBasicFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAcceptance))
    
    # 使用自定义结果收集器运行测试
    result_collector = TestResultCollector()
    runner = unittest.TextTestRunner(resultclass=TestResultCollector, verbosity=2)
    result = runner.run(suite)
    
    # 统计结果
    passed = len([r for r in result.test_results if r['status'] == 'passed'])
    failed = len([r for r in result.test_results if r['status'] == 'failed'])
    errors = len([r for r in result.test_results if r['status'] == 'error'])
    total = len(result.test_results)
    
    # 输出统计信息
    print("\n" + "=" * 60)
    print("📊 测试结果统计")
    print("=" * 60)
    print(f"总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {failed}")
    print(f"错误数: {errors}")
    print(f"通过率: {passed/total*100:.2f}%" if total > 0 else "通过率: 0%")
    
    # 返回测试结果数据
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'errors': errors,
        'success_rate': passed/total*100 if total > 0 else 0,
        'test_details': result.test_results,
        'timestamp': datetime.datetime.now().isoformat()
    }


def run_test_category(category):
    """按类别运行测试"""
    print(f"\n运行 {category} 测试...")
    print("=" * 60)
    
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    if category == 'unit':
        suite.addTests(loader.loadTestsFromTestCase(TestBasicFunctions))
        suite.addTests(loader.loadTestsFromTestCase(TestLLMFunctions))
    elif category == 'system':
        suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    elif category == 'acceptance':
        suite.addTests(loader.loadTestsFromTestCase(TestAcceptance))
    elif category == 'basic':
        suite.addTests(loader.loadTestsFromTestCase(TestBasicFunctions))
    elif category == 'llm':
        suite.addTests(loader.loadTestsFromTestCase(TestLLMFunctions))
    else:
        print(f"未知的测试类别: {category}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """主函数：整合批命令功能，实现跨平台一键测试"""
    print("=" * 60)
    print("妙妙作文屋 v1 版本自动测试脚本")
    print("=" * 60)
    print()
    
    # 检查Python安装
    if not check_python_installation():
        print("❌ 错误：未安装Python或Python不在系统路径中")
        input("按回车键退出...")
        sys.exit(1)
    
    print("✅ Python已安装")
    print()
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败")
        input("按回车键退出...")
        sys.exit(1)
    
    print()
    print("正在运行测试套件...")
    print("=" * 60)
    
    # 运行测试
    test_results = run_all_tests()
    
    # 更新README.md文件
    from test_report_generator import update_readme_with_results
    update_readme_with_results(test_results)
    
    # 显示结果
    print()
    if test_results['failed'] == 0 and test_results['errors'] == 0:
        print("=" * 60)
        print("🎉 测试全部通过！")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ 测试失败，请检查README.md中的失败详情")
        print("=" * 60)
    
    print()
    print("=" * 60)
    print("📊 测试结果已更新到README.md文件")
    print("=" * 60)
    
    # 等待用户输入后退出（跨平台兼容）
    input("按回车键退出...")
    sys.exit(0 if test_results['failed'] == 0 and test_results['errors'] == 0 else 1)


if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) > 1:
        category = sys.argv[1]
        success = run_test_category(category)
        sys.exit(0 if success else 1)
    else:
        main()