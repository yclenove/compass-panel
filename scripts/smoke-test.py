#!/usr/bin/env python3
"""
mdserver-web 冒烟测试
用于验证部署后的基本功能
"""

import requests
import sys


class SmokeTest:
    def __init__(self, base_url='http://localhost:7200'):
        self.base_url = base_url
        self.session = requests.Session()
        self.passed = 0
        self.failed = 0

    def log(self, message, level='INFO'):
        print(f'[{level}] {message}')

    def test_pass(self, test_name):
        self.passed += 1
        self.log(f'PASS: {test_name}')

    def test_fail(self, test_name, reason=''):
        self.failed += 1
        self.log(f'FAIL: {test_name}: {reason}')

    def test_home_page(self):
        """测试首页访问"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code in [200, 302]:
                self.test_pass('首页访问')
            else:
                self.test_fail('首页访问', f'状态码: {response.status_code}')
        except Exception as e:
            self.test_fail('首页访问', str(e))

    def test_login_page(self):
        """测试登录页面"""
        try:
            response = self.session.get(f'{self.base_url}/login', timeout=10)
            if response.status_code in [200, 302]:
                self.test_pass('登录页面')
            else:
                self.test_fail('登录页面', f'状态码: {response.status_code}')
        except Exception as e:
            self.test_fail('登录页面', str(e))

    def test_check_login_api(self):
        """测试登录状态检查 API"""
        try:
            response = self.session.get(f'{self.base_url}/check_login', timeout=10)
            data = response.json()
            if 'status' in data:
                self.test_pass('登录状态检查 API')
            else:
                self.test_fail('登录状态检查 API', '返回数据格式异常')
        except Exception as e:
            self.test_fail('登录状态检查 API', str(e))

    def run_all_tests(self):
        """运行所有测试"""
        self.log('开始冒烟测试...')
        self.log('=' * 40)

        self.test_home_page()
        self.test_login_page()
        self.test_check_login_api()

        self.log('=' * 40)
        self.log(f'测试完成: {self.passed} 通过, {self.failed} 失败')

        return self.failed == 0


if __name__ == '__main__':
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:7200'
    tester = SmokeTest(base_url)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
