"""
Moodle Client module for interacting with Moodle LMS.
Handles fetching questions, answers, and submitting grades.
"""

import re
import subprocess
from typing import Tuple, List, Dict, Optional
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests

from config import Config


class MoodleClient:
    """Client for interacting with Moodle LMS."""

    def __init__(self):
        """Initialize Moodle client with configuration."""
        self.config = Config()

    def find_requires_grade_links(self, url: str) -> List[str]:
        """
        Find all links that require grading.

        Args:
            url: Quiz report URL

        Returns:
            List of URLs for questions requiring grading
        """
        headers = self.config.get_headers()
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'reviewquestion\.php\?.*slot='))
        return [link['href'] for link in links if 'requires grading' in link.text.lower()]

    @staticmethod
    def group_links_by_slot(links: List[str]) -> Dict[str, List[str]]:
        """
        Group links by question slot number.

        Args:
            links: List of question URLs

        Returns:
            Dictionary mapping slot numbers to list of URLs
        """
        grouped_links = {}
        for link in links:
            parsed_url = urlparse(link)
            query_params = parse_qs(parsed_url.query)
            slot = query_params.get('slot', [''])[0]
            if slot not in grouped_links:
                grouped_links[slot] = []
            grouped_links[slot].append(link)
        return grouped_links

    def get_question_details(self, url: str) -> Tuple[str, str, int]:
        """
        Fetch question text, student answer, and max marks for a given question URL.

        Args:
            url: Question review URL

        Returns:
            Tuple of (question_text, student_answer, max_marks)
        """
        print(url)

        curl_command = f'''curl '{url}' \\
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \\
  -H 'accept-language: en,zh-CN;q=0.9,zh;q=0.8' \\
  -H 'cache-control: max-age=0' \\
  -b '{self.config.MOODLE_COOKIES}' \\
  -H 'user-agent: {self.config.USER_AGENT}'
'''

        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        html_content = result.stdout

        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract question text
        question_div = soup.select_one('div.qtext')
        question = question_div.get_text(strip=True) if question_div else "Question not found"

        # Extract student answer
        answer_div = soup.select_one('div.qtype_essay_response')
        answer = answer_div.get_text(strip=True) if answer_div else "Answer not found"

        # Extract max marks
        grade_div = soup.select_one('div.grade')
        grade_info = grade_div.get_text(strip=True) if grade_div else "Grade info not found"
        max_mark = grade_info.split('out of')[-1].strip() if 'out of' in grade_info else "Max mark not found"
        max_mark = int(float(max_mark)) if max_mark != "Max mark not found" else 0

        return question, answer, max_mark

    def submit_grade(self, url: str, grade: str, max_mark: int) -> bool:
        """
        Submit a grade for a question.

        Args:
            url: Question review URL
            grade: Grade to assign (as string)
            max_mark: Maximum possible marks

        Returns:
            bool: True if submission succeeded, False otherwise
        """
        # Extract attempt and slot from URL
        params = dict(param.split('=') for param in url.split('?')[1].split('&'))
        attempt = params['attempt']
        slot = params['slot']

        # Fetch the comment page to get necessary form values
        comment_url = f'{self.config.MOODLE_BASE_URL}/mod/quiz/comment.php?attempt={attempt}&slot={slot}'
        curl_comment_page = f'''curl '{comment_url}' \\
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \\
  -H 'accept-language: en,zh-CN;q=0.9,zh;q=0.8' \\
  -H 'cache-control: max-age=0' \\
  -b '{self.config.MOODLE_COOKIES}' \\
  -H 'user-agent: {self.config.USER_AGENT}'
'''

        result = subprocess.run(curl_comment_page, shell=True, capture_output=True, text=True)
        html_content = result.stdout
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract form values
        match = re.search(rf'question-(\d+)-{slot}', html_content)
        q_value = f'q{match.group(1)}' if match else ''

        sesskey_match = re.search(r'"sesskey":"([^"]+)"', html_content)
        sesskey = sesskey_match.group(1) if sesskey_match else ''

        sequencecheck_input = soup.find('input', attrs={'name': lambda x: x and 'sequencecheck' in x})
        sequencecheck_value = sequencecheck_input['value'] if sequencecheck_input else ''

        itemid_input = soup.find('input', attrs={'name': lambda x: x and 'comment:itemid' in x})
        itemid = itemid_input['value'] if itemid_input else ''

        # Prepare and execute submission
        curl_command = f'''curl '{self.config.MOODLE_BASE_URL}/mod/quiz/comment.php' \\
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \\
  -H 'accept-language: en,zh-CN;q=0.9,zh;q=0.8' \\
  -H 'cache-control: max-age=0' \\
  -H 'content-type: application/x-www-form-urlencoded' \\
  -b '{self.config.MOODLE_COOKIES}' \\
  -H 'origin: {self.config.MOODLE_BASE_URL}' \\
  -H 'referer: {comment_url}' \\
  -H 'user-agent: {self.config.USER_AGENT}' \\
  --data-raw '{q_value}%3A{slot}_%3Asequencecheck={sequencecheck_value}&{q_value}%3A{slot}_-comment=&{q_value}%3A{slot}_-comment%3Aitemid={itemid}&{q_value}%3A{slot}_-commentformat=1&{q_value}%3A{slot}_-mark={grade}&{q_value}%3A{slot}_-maxmark={max_mark}&{q_value}%3A{slot}_%3Aminfraction=0&{q_value}%3A{slot}_%3Amaxfraction=1&attempt={attempt}&slot={slot}&slots={slot}&sesskey={sesskey}&submit=Save'
'''

        print(f'Submitting grade: {grade}/{max_mark} for attempt {attempt}, slot {slot}')

        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print('Grade submission command executed successfully')
            return True
        else:
            print(f'Warning: Grade submission may have failed. Return code: {result.returncode}')
            return False
