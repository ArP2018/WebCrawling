# 爬取结果实体
# author: Yin Yalin


class Entity(object):
    url = ''
    title = ''
    short_description = ''
    publish_date = ''
    full_content = ''


class Company(object):
    url = ''
    company_name = ''
    representative = ''  # 法定代表人
    register_info = ''  # 注册信息
    status = ''
    contact_info = ''   #联系信息
    basic_info = ''  # 基本信息


if __name__ == '__main__':
    pass
