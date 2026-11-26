import flet as ft
import fitz  # PyMuPDF
import time
import threading
import os

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LibraryView(ft.Container):
    """AI PDF Reader - Upload and summarize PDFs"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        self.current_pdf_text = ""
        
        # File picker
        self.file_picker = ft.FilePicker()
        
        # UI Components
        self.pdf_text_display = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        )
        
        self.summarize_btn = ft.ElevatedButton(
            "Summarize with AI",
            icon=ft.Icons.AUTO_AWESOME,
            on_click=self.summarize_text,
            disabled=True,
            bgcolor=ft.Colors.PURPLE_700,
            color="#FFFFFF",
        )
        
        self.summary_display = ft.Container(
            content=ft.Text(
                "Summary will appear here...",
                size=14,
                color=ft.Colors.GREY_500,
                italic=True,
            ),
            padding=20,
            bgcolor=ft.Colors.GREY_900,
            border_radius=10,
            visible=False,
        )
        
        self.loading_indicator = ft.ProgressRing(visible=False)
        
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI"""
        self.content = ft.Column([
            # Hidden file picker
            self.file_picker,
            
            # Header
            ft.Row([
                ft.Text("Library - AI PDF Reader", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Upload PDF",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=self.pick_pdf_file,
                    bgcolor=ft.Colors.BLUE_700,
                    color="#FFFFFF",
                ),
            ]),
            ft.Divider(),
            
            # PDF Content Card
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PICTURE_AS_PDF, color=ft.Colors.RED_400, size=32),
                            ft.Text("PDF Content", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            self.loading_indicator,
                        ]),
                        ft.Divider(),
                        ft.Container(
                            content=self.pdf_text_display,
                            expand=True,
                        ),
                    ]),
                    padding=20,
                ),
                elevation=3,
            ),
            
            # Action buttons
            ft.Row([
                self.summarize_btn,
            ], spacing=10),
            
            # Summary display
            self.summary_display,
        ], spacing=15, expand=True)
    
    def pick_pdf_file(self, e):
        """Open file picker to select PDF"""
        self.file_picker.pick_files(
            allowed_extensions=["pdf"],
            dialog_title="Select a PDF file",
            on_result=self.on_file_picked
        )
    
    def on_file_picked(self, e):
        """Handle file selection"""
        if e.files:
            file_path = e.files[0].path
            self.extract_pdf_text(file_path)
    
    def extract_pdf_text(self, file_path):
        """Extract text from PDF using PyMuPDF"""
        try:
            self.pdf_text_display.controls.clear()
            self.current_pdf_text = ""
            
            # Show loading
            self.pdf_text_display.controls.append(
                ft.Row([
                    ft.ProgressRing(width=30, height=30),
                    ft.Text("Extracting text from PDF...", size=14),
                ], spacing=10)
            )
            self.update()
            
            # Open PDF
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Extract text from all pages
            full_text = []
            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text()
                full_text.append(text)
            
            doc.close()
            
            self.current_pdf_text = "\n\n".join(full_text)
            
            # Display extracted text
            self.pdf_text_display.controls.clear()
            
            # Show page count
            self.pdf_text_display.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.BLUE_400),
                        ft.Text(
                            f"Extracted from {total_pages} page(s)",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ], spacing=10),
                    padding=10,
                    bgcolor=ft.Colors.BLUE_900,
                    border_radius=8,
                )
            )
            
            # Show text content
            if self.current_pdf_text.strip():
                self.pdf_text_display.controls.append(
                    ft.Container(
                        content=ft.SelectionArea(
                            content=ft.Text(
                                self.current_pdf_text[:5000] + ("..." if len(self.current_pdf_text) > 5000 else ""),
                                size=13,
                                selectable=True,
                            ),
                        ),
                        padding=15,
                        bgcolor=ft.Colors.GREY_900,
                        border_radius=8,
                    )
                )
                self.summarize_btn.disabled = False
            else:
                self.pdf_text_display.controls.append(
                    ft.Text(
                        "No text found in PDF",
                        size=14,
                        color=ft.Colors.ORANGE_400,
                    )
                )
            
            self.update()
            self.show_snackbar(f"Successfully extracted text from {total_pages} pages!", success=True)
            
        except Exception as e:
            self.pdf_text_display.controls.clear()
            self.pdf_text_display.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400, size=48),
                        ft.Text(
                            f"Error reading PDF: {str(e)}",
                            size=14,
                            color=ft.Colors.RED_400,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                )
            )
            self.update()
            self.show_snackbar(f"Error: {str(e)}", error=True)
    
    def summarize_text(self, e):
        """Summarize the PDF text with AI"""
        if not self.current_pdf_text:
            return
        
        # Run in background thread
        if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
            thread = threading.Thread(target=self._real_ai_summary, daemon=True)
        else:
            thread = threading.Thread(target=self._mock_ai_summary, daemon=True)
        thread.start()
    
    def _real_ai_summary(self):
        """Real AI summary using Gemini API"""
        try:
            # Show loading
            self.summarize_btn.disabled = True
            self.loading_indicator.visible = True
            self.summary_display.visible = True
            self.summary_display.content = ft.Row([
                ft.ProgressRing(width=20, height=20),
                ft.Text("Gemini AI is analyzing the document...", size=14),
            ], spacing=10)
            self.update()
            
            # Configure Gemini
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-pro')
            
            # Prepare prompt
            prompt = f"""Please analyze this document and provide:
1. A concise summary (2-3 paragraphs)
2. Key points and main themes
3. Important takeaways or conclusions

Document text:
{self.current_pdf_text[:15000]}  # Limit to avoid token limits
"""
            
            # Generate summary
            response = model.generate_content(prompt)
            summary_text = response.text
            
            # Display summary
            word_count = len(self.current_pdf_text.split())
            char_count = len(self.current_pdf_text)
            
            formatted_summary = f"""📄 **Document Analysis Complete**

📊 **Statistics:**
- Total Words: {word_count:,}
- Total Characters: {char_count:,}
- Estimated Reading Time: {word_count // 200} minutes

---

🤖 **Gemini AI Summary:**

{summary_text}

---

💡 **Powered by Google Gemini**
"""
            
            self.summary_display.content = ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.PURPLE_400, size=24),
                    ft.Text("AI Summary", size=18, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Divider(),
                ft.Markdown(
                    formatted_summary,
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                ),
            ], spacing=10)
            
            self.loading_indicator.visible = False
            self.summarize_btn.disabled = False
            self.update()
            
            self.show_snackbar("AI Summary generated!", success=True)
            
        except Exception as e:
            # Fallback to mock if API fails
            self.show_snackbar(f"Gemini API error, using mock: {str(e)}", error=True)
            self._mock_ai_summary()
    
    def _mock_ai_summary(self):
        """Mock AI summary - replace with real Gemini API later"""
        try:
            # Show loading
            self.summarize_btn.disabled = True
            self.loading_indicator.visible = True
            self.summary_display.visible = True
            self.summary_display.content = ft.Row([
                ft.ProgressRing(width=20, height=20),
                ft.Text("AI is analyzing the document...", size=14),
            ], spacing=10)
            self.update()
            
            # Simulate AI processing
            time.sleep(3)
            
            # Generate mock summary
            word_count = len(self.current_pdf_text.split())
            char_count = len(self.current_pdf_text)
            
            mock_summary = f"""📄 **Document Analysis Complete**

📊 **Statistics:**
- Total Words: {word_count:,}
- Total Characters: {char_count:,}
- Estimated Reading Time: {word_count // 200} minutes

🤖 **AI Summary (Mock):**
This document contains {word_count} words across multiple sections. The content appears to be structured with various topics and themes. 

Key points identified:
• The document contains substantial textual content
• Multiple paragraphs and sections are present
• Content structure suggests academic or professional material

*Note: This is a mock summary. Connect to Gemini API for real AI-powered summarization.*

💡 **Next Steps:**
- Review the full text above for detailed information
- Use the summary to quickly understand the document's scope
- Export or save important sections for later reference
"""
            
            # Display summary
            self.summary_display.content = ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.PURPLE_400, size=24),
                    ft.Text("AI Summary", size=18, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Divider(),
                ft.Markdown(
                    mock_summary,
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                ),
            ], spacing=10)
            
            self.loading_indicator.visible = False
            self.summarize_btn.disabled = False
            self.update()
            
            self.show_snackbar("AI Summary generated!", success=True)
            
        except Exception as e:
            self.loading_indicator.visible = False
            self.summarize_btn.disabled = False
            self.summary_display.content = ft.Text(
                f"Error generating summary: {str(e)}",
                color=ft.Colors.RED_400,
            )
            self.update()
    
    def show_snackbar(self, message, success=False, error=False):
        """Show a snackbar notification"""
        if self.page:
            bgcolor = ft.Colors.GREEN_700 if success else (ft.Colors.RED_700 if error else ft.Colors.BLUE_700)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message, color="#FFFFFF"),
                bgcolor=bgcolor,
            )
            self.page.snack_bar.open = True
            self.page.update()
