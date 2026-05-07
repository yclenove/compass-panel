# coding:utf-8
"""分页模块测试"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))


class TestPage:
    """分页类测试"""

    def test_make_link_href(self):
        """测试生成 href 链接"""
        from utils.page import Page
        p = Page()
        p._Page__RTURN_JS = ""
        p._Page__URI = "?"
        p._Page__ARGS_TPL = ""

        link = p._make_link("Pnum", 3, "3")
        assert "Pnum" in link
        assert "href" in link
        assert "p=3" in link

    def test_make_link_js(self):
        """测试生成 JS 回调链接"""
        from utils.page import Page
        p = Page()
        p._Page__RTURN_JS = "goPage"
        p._Page__URI = "?"
        p._Page__ARGS_TPL = ""

        link = p._make_link("Pnum", 3, "3")
        assert "Pnum" in link
        assert "onclick" in link
        assert "goPage" in link

    def test_get_cpage_with_value(self):
        """测试获取当前页 - 有值"""
        from utils.page import Page
        p = Page()
        assert p._Page__GetCpage(5) == 5

    def test_get_cpage_without_value(self):
        """测试获取当前页 - 无值"""
        from utils.page import Page
        p = Page()
        assert p._Page__GetCpage(0) == 1
        assert p._Page__GetCpage(None) == 1

    def test_start_row(self):
        """测试起始行计算"""
        from utils.page import Page
        p = Page()
        p._Page__C_PAGE = 3
        p.ROW = 10
        assert p._Page__StartRow() == 21

    def test_end_row(self):
        """测试结束行计算"""
        from utils.page import Page
        p = Page()
        p._Page__C_PAGE = 2
        p.ROW = 10
        p._Page__COUNT_ROW = 50
        assert p._Page__EndRow() == 20

    def test_end_row_less_than_row(self):
        """测试结束行 - 总数小于每页行数"""
        from utils.page import Page
        p = Page()
        p._Page__C_PAGE = 1
        p.ROW = 10
        p._Page__COUNT_ROW = 5
        assert p._Page__EndRow() == 5

    def test_get_count_page(self):
        """测试总页数计算"""
        from utils.page import Page
        p = Page()
        p._Page__COUNT_ROW = 25
        p.ROW = 10
        assert p._Page__GetCountPage() == 3

    def test_set_uri(self):
        """测试 URI 构造"""
        from utils.page import Page
        p = Page()
        uri = p._Page__SetUri({"p": "1", "type": "all"})
        assert "p=" not in uri
        assert "type=all" in uri

    def test_get_page_href_mode(self):
        """测试完整分页 - href 模式"""
        from utils.page import Page
        p = Page()
        page_info = {
            "return_js": "",
            "count": 100,
            "row": 10,
            "p": 3,
            "uri": {"type": "all"},
        }
        result = p.GetPage(page_info)
        assert "<div>" in result
        assert "Pnum" in result
        assert "Pcurrent" in result

    def test_get_page_js_mode(self):
        """测试完整分页 - JS 回调模式"""
        from utils.page import Page
        p = Page()
        page_info = {
            "return_js": "goPage",
            "count": 100,
            "row": 10,
            "p": 3,
            "uri": {"type": "all"},
        }
        result = p.GetPage(page_info)
        assert "goPage" in result
        assert "onclick" in result

    def test_get_page_first_page(self):
        """测试第一页分页"""
        from utils.page import Page
        p = Page()
        page_info = {
            "return_js": "",
            "count": 100,
            "row": 10,
            "p": 1,
            "uri": {},
        }
        result = p.GetPage(page_info)
        # 第一页不应该有"上一页"和"首页"
        assert "Ppren" not in result
        assert "Pstart" not in result

    def test_get_page_last_page(self):
        """测试最后一页分页"""
        from utils.page import Page
        p = Page()
        page_info = {
            "return_js": "",
            "count": 100,
            "row": 10,
            "p": 10,
            "uri": {},
        }
        result = p.GetPage(page_info)
        # 最后一页不应该有"下一页"和"尾页"
        assert "Pnext" not in result
        assert "Pend" not in result

    def test_get_page_custom_limit(self):
        """测试自定义分页组件"""
        from utils.page import Page
        p = Page()
        page_info = {
            "return_js": "",
            "count": 100,
            "row": 10,
            "p": 5,
            "uri": {},
        }
        result = p.GetPage(page_info, limit="3,6,8")
        assert "Pnum" in result
        assert "Pnumber" in result
        assert "Pcount" in result

    def test_get_page_num_with_args_tpl(self):
        """测试带参数模板的页码"""
        from utils.page import Page
        p = Page()
        p._Page__ARGS_TPL = "&type=all"
        assert p.getPageNum(3) == "3&type=all"
