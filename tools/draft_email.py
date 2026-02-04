"""Email generation tool."""

from typing import Optional, Dict, Any

from anthropic import Anthropic

from config.settings import settings


class EmailDraftTool:
    """Tool for generating professional email drafts using Claude."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the email draft tool.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.llm_model
        self.client = Anthropic(api_key=self.api_key)

    def draft_research_inquiry(
        self,
        faculty_name: str,
        faculty_research_interests: str,
        student_name: str,
        student_background: str,
        student_interests: str,
        tone: str = "professional",
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a draft email for a student to reach out to a faculty member.

        Args:
            faculty_name: Name of the faculty member
            faculty_research_interests: Faculty's research interests
            student_name: Name of the student
            student_background: Brief background about the student
            student_interests: Student's research interests
            tone: Tone of the email (professional, casual, formal)
            additional_context: Any additional context to include

        Returns:
            Dictionary with subject line and email body
        """
        prompt = f"""You are helping a student draft a professional research inquiry email to a professor.

Faculty Information:
- Name: {faculty_name}
- Research Interests: {faculty_research_interests}

Student Information:
- Name: {student_name}
- Background: {student_background}
- Research Interests: {student_interests}

Email Tone: {tone}

{f"Additional Context: {additional_context}" if additional_context else ""}

Please draft a professional email with:
1. An appropriate subject line
2. A concise, well-structured email body (200-300 words)

The email should:
- Express genuine interest in the professor's research
- Highlight relevant connections between the student's interests and the professor's work
- Be respectful of the professor's time
- Include a clear ask (e.g., meeting to discuss research opportunities)
- Be personalized and not generic

Format your response as:
Subject: [subject line]

[email body]"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = message.content[0].text

            # Split into subject and body
            lines = response_text.strip().split('\n', 1)
            subject = ""
            body = response_text

            if lines[0].startswith("Subject:"):
                subject = lines[0].replace("Subject:", "").strip()
                body = lines[1].strip() if len(lines) > 1 else ""

            return {
                'success': True,
                'subject': subject,
                'body': body,
                'full_text': response_text
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'subject': None,
                'body': None
            }

    def draft_followup_email(
        self,
        faculty_name: str,
        student_name: str,
        original_context: str,
        reason_for_followup: str
    ) -> Dict[str, Any]:
        """
        Generate a follow-up email draft.

        Args:
            faculty_name: Name of the faculty member
            student_name: Name of the student
            original_context: Context from the original email
            reason_for_followup: Reason for following up

        Returns:
            Dictionary with subject line and email body
        """
        prompt = f"""Draft a brief, polite follow-up email for a student.

Faculty Name: {faculty_name}
Student Name: {student_name}
Original Context: {original_context}
Reason for Follow-up: {reason_for_followup}

The email should be short (100-150 words), polite, and respect the professor's time.

Format your response as:
Subject: [subject line]

[email body]"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Parse response
            lines = response_text.strip().split('\n', 1)
            subject = ""
            body = response_text

            if lines[0].startswith("Subject:"):
                subject = lines[0].replace("Subject:", "").strip()
                body = lines[1].strip() if len(lines) > 1 else ""

            return {
                'success': True,
                'subject': subject,
                'body': body,
                'full_text': response_text
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'subject': None,
                'body': None
            }


def draft_research_inquiry_email(
    faculty_name: str,
    faculty_research_interests: str,
    student_name: str,
    student_background: str,
    student_interests: str,
    tone: str = "professional"
) -> Dict[str, Any]:
    """
    Convenience function to draft a research inquiry email.

    Args:
        faculty_name: Name of the faculty member
        faculty_research_interests: Faculty's research interests
        student_name: Name of the student
        student_background: Brief background about the student
        student_interests: Student's research interests
        tone: Tone of the email (professional, casual, formal)

    Returns:
        Dictionary with subject line and email body
    """
    tool = EmailDraftTool()
    return tool.draft_research_inquiry(
        faculty_name,
        faculty_research_interests,
        student_name,
        student_background,
        student_interests,
        tone
    )