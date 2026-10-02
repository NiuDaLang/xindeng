from django.test import SimpleTestCase
from creators.utils import clean_blog_body

class CleanBlogBodyTests(SimpleTestCase):
    def test_strips_script_and_javascript_href(self):
        html = '<p class="text-center text-red-500">Hi <script>alert(1)</script><a href="javascript:evil()">x</a></p>'
        out = clean_blog_body(html)
        self.assertNotIn('<script>', out)
        self.assertNotIn('javascript:', out)
        self.assertNotIn('text-red-500', out)
        self.assertIn('text-center', out)

    def test_preserves_external_link_with_rel(self):
        html = '<p>see <a href="https://example.com" target="_blank">here</a></p>'
        out = clean_blog_body(html)
        self.assertIn('href="https://example.com"', out)
        self.assertIn('rel="noopener noreferrer"', out)

    def test_removes_dead_anchor_keeps_text(self):
        html = '<p>click <a>me</a></p>'
        out = clean_blog_body(html)
        self.assertNotIn('<a', out)
        self.assertIn('click me', out)

    def test_no_anchor_still_returns_content(self):
        # Guards against the dedent bug we just fixed
        out = clean_blog_body('<p>just text</p>')
        self.assertIsNotNone(out)
        self.assertIn('just text', out)