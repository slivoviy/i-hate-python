import pytest
from unittest.mock import mock_open, patch
import json
from service import get_news, get_news_by_keyword, __format_datetime

# Тестовые данные
test_data = [
    {"message": "Первое важное сообщение", "date": "2023-04-01T12:00:00+03:00"},
    {"message": "Второе важное сообщение", "date": "2023-04-02T12:00:00+03:00"},
    {"message": "Сообщение с ключевым словом test", "date": "2023-04-03T18:30:00+03:00"}
]

# Тест для функции get_news
def test_get_news():
    with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
        result = get_news(2)
        assert len(result) == 2
        assert "Первое важное сообщение" in result[0]
        assert "Второе важное сообщение" in result[1]

# Тест для функции get_news_by_keyword
def test_get_news_by_keyword():
    with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
        result = get_news_by_keyword("ключевым словом")
        assert len(result) == 1
        assert "Сообщение с ключевым словом test" in result[0]

# Тест для внутренней функции __format_datetime
def test__format_datetime():
    datetime_str = "2023-04-01T12:00:00+03:00"
    formatted_datetime = __format_datetime(datetime_str)
    assert formatted_datetime == "01 апреля в 12:00 МСК"

# Тест на неправильный формат даты
def test__format_datetime_invalid_date():
    with pytest.raises(ValueError): # ожидаемое исключение, если формат даты неправильный
        __format_datetime("2023-04-01 12:00:00")
