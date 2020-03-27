import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_PATH, 'annual_report.db')
PDF_PATH = os.path.join(BASE_PATH, 'pdf')

WEB_MAPPING = {
    '上交所': 'sse',
    '深交所': 'szse'
}
