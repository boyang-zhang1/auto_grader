"""
Moodle Auto Grader - Main Entry Point

A tool to automate the grading process for Moodle essay questions.
Fetches questions requiring grading, displays them to the grader,
and submits grades back to Moodle.

Author: Auto Grader Team
License: MIT
"""

from typing import List
from config import Config
from moodle_client import MoodleClient


def main():
    """Main function to run the auto grader."""

    # Validate configuration
    if not Config.validate():
        print("\nPlease configure your .env file with the required values.")
        print("See .env.example for reference.")
        return

    # Initialize Moodle client
    client = MoodleClient()
    base_url = Config.QUIZ_REPORT_URL

    print("Moodle Auto Grader")
    print("=" * 80)
    print(f"Quiz Report URL: {base_url}")
    print("=" * 80)

    # Step 1: Find all questions requiring grading
    print("\nFetching questions that require grading...")
    links = client.find_requires_grade_links(base_url)

    if not links:
        print("No questions requiring grading found.")
        return

    # Step 2: Group and sort links by slot
    grouped_links = client.group_links_by_slot(links)
    reranked_links = [
        link for slot in sorted(grouped_links.keys(), key=int)
        for link in grouped_links[slot]
    ]

    # Convert comment links to review links
    for i in range(len(reranked_links)):
        reranked_links[i] = reranked_links[i].replace('comment.php', 'reviewquestion.php')
        print(reranked_links[i])

    print(f"\nTotal submissions to grade: {len(reranked_links)}")

    # Confirm before starting
    input("\nPress Enter to start grading...")

    # Step 3: Process each submission
    previous_question = None
    for i, link in enumerate(reranked_links):
        # Fetch question details
        question, answer, max_mark = client.get_question_details(link)

        # Only display question if it's different from the previous one
        if question != previous_question:
            print(f"\n{'=' * 80}")
            print("NEW QUESTION:")
            print(f"Question: {question}")
            print(f"Max Mark: {max_mark}")
            print(f"{'=' * 80}")
            previous_question = question

        # Display student answer
        print(f"\n[{i + 1}/{len(reranked_links)}] Student Answer:")
        print(answer)
        print("-" * 80)

        # Get grade input from user
        grade = input("Enter the grade for this question: ")

        # Submit grade
        success = client.submit_grade(link, grade, max_mark)

        if success:
            print("✓ Grade submitted successfully.\n")
        else:
            print("✗ Grade submission failed. Check the error above.\n")

    print("\n" + "=" * 80)
    print("Grading session complete!")
    print(f"Total submissions graded: {len(reranked_links)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
