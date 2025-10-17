"""
Configuration module for Moodle Auto Grader.
Loads environment variables from .env file.
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Configuration class for Moodle Auto Grader."""

    # Moodle URLs
    MOODLE_BASE_URL: str = os.getenv('MOODLE_BASE_URL', 'https://moodle.lsu.edu')
    QUIZ_REPORT_URL: str = os.getenv('QUIZ_REPORT_URL', '')

    # Authentication
    MOODLE_COOKIES: str = os.getenv('MOODLE_COOKIES', '')

    # User Agent
    USER_AGENT: str = os.getenv(
        'USER_AGENT',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    )

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not cls.QUIZ_REPORT_URL:
            print("Error: QUIZ_REPORT_URL is not set in .env file")
            return False

        if not cls.MOODLE_COOKIES:
            print("Error: MOODLE_COOKIES is not set in .env file")
            return False

        return True

    @classmethod
    def get_headers(cls) -> dict:
        """
        Get HTTP headers for requests.

        Returns:
            dict: HTTP headers including cookies and user agent
        """
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                     'image/avif,image/webp,image/apng,*/*;q=0.8,'
                     'application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
            'cache-control': 'max-age=0',
            'cookie': cls.MOODLE_COOKIES,
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", '
                        '"Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': cls.USER_AGENT
        }
