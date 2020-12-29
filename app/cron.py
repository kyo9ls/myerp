import datetime
from app.views import create_excel


def push_email(user=1):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    select_dict = {'company__user_id': user}
    select_dict['order_date'] = today
    file_path = create_excel(select_dict, True, user)

def test():
    print(1234)