import hashlib
import datetime


def gen_md5_digest(content):
    return hashlib.md5(content.encode()).hexdigest()


def get_date(days=0):
    d = datetime.datetime.now() + datetime.timedelta(days=days)
    return d.strftime('%Y-%m-%d')

# 获取用户id
def user_id(request):
    return 2


class Pagination:
    # 输出页码
    def __init__(self, request, count, num_per_page=10, max_show=11):
        try:
            page = int(request.GET.get('page', 1))
            page = page if page > 0 else 1
        except Exception:
            page = 1
        # 记录起止
        start = (page - 1) * num_per_page
        end = start + num_per_page

        # 记录条数count
        # 总页码
        number, more = divmod(count, num_per_page)
        if more:
            number += 1
        # 页码
        half_show = max_show // 2
        if number <= max_show:
            # 页码起始
            page_start = 1
            page_end = number
        else:
            # 左侧极值
            if page - half_show < 1:
                page_start = 1
                page_end = max_show
            # 右侧极值
            elif page + half_show > number:
                page_start = number - max_show + 1
                page_end = number
            else:
                page_start = page - half_show
                page_end = page + half_show
        page_list = []
        page_list.append(
            '<li{}><a{}><span aria-hidden="true">&laquo;</span></a></li>'.format(
                ' class="disabled"' if page == 1 else '',
                '  href="?page={}" aria-label="Previous"'.format(page - 1) if page > 1 else ''))
        for i in range(page_start, page_end + 1):
            if i == page:
                page_list.append('<li class="active"><a href="?page={}">{}</a></li>'.format(i, i))
            else:
                page_list.append('<li><a href="?page={}">{}</a></li>'.format(i, i))
        page_list.append(
            '<li{}><a{}><span aria-hidden="true">&raquo;</span></a></li>'.format(
                ' class="disabled"' if page >= number else '',
                ' href="?page={}" aria-label="Next"'.format(page + 1) if page < number else ''))
        self.start = start
        self.end = end
        self.page_html = ''.join(page_list)
