# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 分页库操作
# ---------------------------------------------------------------------------------


import math


class Page:
    # --------------------------
    # 分页类 - JS回调版
    # --------------------------
    __PREV = "上一页"
    __NEXT = "下一页"
    __START = "首页"
    __END = "尾页"
    __COUNT_START = "共"
    __COUNT_END = "条数据"
    __FO = "从"
    __LINE = "条"
    __LIST_NUM = 4
    SHIFT = None  # 偏移量
    ROW = None  # 每页行数
    __C_PAGE = None  # 当前页
    __COUNT_PAGE = None  # 总页数
    __COUNT_ROW = None  # 总行数
    __URI = None  # URI
    __RTURN_JS = False  # 是否返回JS回调
    __START_NUM = None  # 起始行
    __END_NUM = None  # 结束行
    __ARGS_TPL = ""

    def __init__(self):
        pass

    def getPageNum(self, num):
        return str(num) + self.__ARGS_TPL

    def _make_link(self, css_class, page_num, label):
        """生成分页链接（href 或 onclick 模式）"""
        if self.__RTURN_JS == "":
            return (
                f"<a class='{css_class}' href='"
                + self.__URI + "p=" + str(page_num)
                + "'>" + str(label) + "</a>"
            )
        return (
            f"<a class='{css_class}' onclick='"
            + self.__RTURN_JS + "(" + self.getPageNum(page_num)
            + ")'>" + str(label) + "</a>"
        )

    def GetPage(self, pageInfo, limit="1,2,3,4,5,6,7,8"):
        # 取分页信息
        self.__RTURN_JS = pageInfo["return_js"]
        self.__COUNT_ROW = pageInfo["count"]

        if "args_tpl" in pageInfo:
            self.__ARGS_TPL = pageInfo["args_tpl"]

        self.ROW = pageInfo["row"]
        self.__C_PAGE = self.__GetCpage(pageInfo["p"])
        self.__START_NUM = self.__StartRow()
        self.__END_NUM = self.__EndRow()
        self.__COUNT_PAGE = self.__GetCountPage()
        self.__URI = self.__SetUri(pageInfo["uri"])
        self.SHIFT = self.__START_NUM - 1

        keys = limit.split(",")
        pages = {
            "1": self.__GetStart(),
            "2": self.__GetPrev(),
            "3": self.__GetPages(),
            "4": self.__GetNext(),
            "5": self.__GetEnd(),
            "6": (
                "<span class='Pnumber'>"
                + str(self.__C_PAGE) + "/" + str(self.__COUNT_PAGE)
                + "</span>"
            ),
            "7": (
                "<span class='Pline'>"
                + str(self.__FO) + str(self.__START_NUM)
                + "-" + str(self.__END_NUM) + str(self.__LINE)
                + "</span>"
            ),
            "8": (
                "<span class='Pcount'>"
                + str(self.__COUNT_START) + str(self.__COUNT_ROW)
                + str(self.__COUNT_END) + "</span>"
            ),
        }

        return "<div>" + "".join(pages[v] for v in keys) + "</div>"

    def __GetEnd(self):
        if self.__C_PAGE >= self.__COUNT_PAGE:
            return ""
        return self._make_link("Pend", self.__COUNT_PAGE, self.__END)

    def __GetNext(self):
        if self.__C_PAGE >= self.__COUNT_PAGE:
            return ""
        return self._make_link("Pnext", self.__C_PAGE + 1, self.__NEXT)

    def __GetPages(self):
        pages = ""
        # 当前页之前
        if (self.__COUNT_PAGE - self.__C_PAGE) < self.__LIST_NUM:
            num = self.__LIST_NUM + (
                self.__LIST_NUM - (self.__COUNT_PAGE - self.__C_PAGE)
            )
        else:
            num = self.__LIST_NUM
        for i in range(num):
            page = self.__C_PAGE - (num - i)
            if page > 0:
                pages += self._make_link("Pnum", page, page)

        # 当前页
        if self.__C_PAGE > 0:
            pages += "<span class='Pcurrent'>" + str(self.__C_PAGE) + "</span>"

        # 当前页之后
        if self.__C_PAGE <= self.__LIST_NUM:
            num = self.__LIST_NUM + (self.__LIST_NUM - self.__C_PAGE) + 1
        else:
            num = self.__LIST_NUM
        for i in range(1, num):
            page = self.__C_PAGE + i
            if page > self.__COUNT_PAGE:
                break
            pages += self._make_link("Pnum", page, page)

        return pages

    def __GetPrev(self):
        if self.__C_PAGE == 1:
            return ""
        return self._make_link("Ppren", self.__C_PAGE - 1, self.__PREV)

    def __GetStart(self):
        if self.__C_PAGE == 1:
            return ""
        return self._make_link("Pstart", 1, self.__START)

    def __GetCpage(self, p):
        return p if p else 1

    def __StartRow(self):
        return (self.__C_PAGE - 1) * self.ROW + 1

    def __EndRow(self):
        if self.ROW > self.__COUNT_ROW:
            return self.__COUNT_ROW
        return self.__C_PAGE * self.ROW

    def __GetCountPage(self):
        return int(math.ceil(self.__COUNT_ROW / float(self.ROW)))

    def __SetUri(self, sinput):
        uri = "?"
        for key in sinput:
            if key == "p":
                continue
            uri += key + "=" + sinput[key] + "&"
        return str(uri)
