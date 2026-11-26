import flet as ft
import random
from utils import UIHelpers, ValidationHelpers, ErrorHandler, show_success, show_error, with_error_handling

class NotesView(ft.Container):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        self.current_mode = "notes"  # "notes" or "flashcards"
        self.flashcard_study_mode = False
        self.current_flashcard_index = 0
        self.flashcards_to_study = []
        self.card_flipped = False
        
        # Note form
        self.note_title = ft.TextField(label="Title", width=300)
        self.note_content = ft.TextField(label="Content", multiline=True, width=300, height=150)
        self.note_subject = ft.TextField(label="Subject (Optional)", width=300)
        self.note_tags = ft.TextField(label="Tags (comma-separated)", width=300)
        
        # Flashcard form
        self.flashcard_title = ft.TextField(label="Title", width=300)
        self.flashcard_front = ft.TextField(label="Front (Question)", multiline=True, width=300, height=80)
        self.flashcard_back = ft.TextField(label="Back (Answer)", multiline=True, width=300, height=80)
        self.flashcard_subject = ft.TextField(label="Subject (Optional)", width=300)
        self.flashcard_tags = ft.TextField(label="Tags (comma-separated)", width=300)
        
        self.content_list = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)
        self.study_area = ft.Container()
        
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI"""
        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("📚 Notes & Flashcards", size=28, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Notes",
                                    icon=ft.Icons.NOTE,
                                    on_click=lambda _: self.switch_mode_to("notes"),
                                    bgcolor=ft.Colors.PURPLE_700 if self.current_mode == "notes" else ft.Colors.GREY_700,
                                    color="#FFFFFF",
                                ),
                                ft.ElevatedButton(
                                    "Flashcards",
                                    icon=ft.Icons.STYLE,
                                    on_click=lambda _: self.switch_mode_to("flashcards"),
                                    bgcolor=ft.Colors.PURPLE_700 if self.current_mode == "flashcards" else ft.Colors.GREY_700,
                                    color="#FFFFFF",
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                
                ft.Row(
                    [
                        # Left panel - Add Note/Flashcard
                        ft.Container(
                            content=self.get_form_content(),
                            bgcolor=ft.Colors.BLUE_GREY_900,
                            padding=20,
                            border_radius=10,
                            width=380,
                        ),
                        
                        # Right panel - List/Study Area
                        ft.Container(
                            content=ft.Column(
                                [
                                    self.get_list_header(),
                                    self.study_area if self.flashcard_study_mode else self.content_list,
                                ],
                                spacing=10,
                                scroll=ft.ScrollMode.AUTO,
                            ),
                            bgcolor=ft.Colors.BLUE_GREY_900,
                            padding=20,
                            border_radius=10,
                            expand=True,
                        ),
                    ],
                    spacing=20,
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                )
            ],
            spacing=20,
            expand=True,
        )
        
        # Don't load content in constructor - will be loaded when view is displayed
        # self.load_content()
    
    def get_form_content(self):
        """Get form based on current mode"""
        if self.current_mode == "notes":
            return ft.Column(
                [
                    ft.Text("Add New Note", size=20, weight=ft.FontWeight.BOLD),
                    self.note_title,
                    self.note_content,
                    self.note_subject,
                    self.note_tags,
                    ft.ElevatedButton(
                        "Add Note",
                        icon=ft.Icons.ADD_CIRCLE,
                        on_click=self.add_note,
                        bgcolor=ft.Colors.PURPLE_700,
                        color="#FFFFFF"
                    ),
                ],
                spacing=15,
            )
        else:
            return ft.Column(
                [
                    ft.Text("Add New Flashcard", size=20, weight=ft.FontWeight.BOLD),
                    self.flashcard_title,
                    self.flashcard_front,
                    self.flashcard_back,
                    self.flashcard_subject,
                    self.flashcard_tags,
                    ft.ElevatedButton(
                        "Add Flashcard",
                        icon=ft.Icons.ADD_CIRCLE,
                        on_click=self.add_flashcard,
                        bgcolor=ft.Colors.PURPLE_700,
                        color="#FFFFFF"
                    ),
                ],
                spacing=15,
            )
    
    def get_list_header(self):
        """Get header for list/study area"""
        if self.flashcard_study_mode:
            return ft.Row(
                [
                    ft.Text("Study Mode", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        on_click=lambda _: self.exit_study_mode(),
                        tooltip="Exit study mode"
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        else:
            return ft.Row(
                [
                    ft.Text(
                        "My Notes" if self.current_mode == "notes" else "My Flashcards",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Study",
                                icon=ft.Icons.PSYCHOLOGY,
                                on_click=lambda _: self.start_study_mode(),
                                bgcolor=ft.Colors.GREEN_700,
                                color="#FFFFFF"
                            ) if self.current_mode == "flashcards" else None,
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                on_click=lambda _: self.load_content(),
                                tooltip="Refresh"
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
    
    def switch_mode_to(self, mode):
        """Switch between notes and flashcards mode"""
        self.current_mode = mode
        self.flashcard_study_mode = False
        self.build_ui()
        if self.page:
            self.update()
    
    def switch_mode(self, e):
        """Switch between notes and flashcards mode"""
        self.current_mode = "notes" if e.control.selected_index == 0 else "flashcards"
        self.flashcard_study_mode = False
        self.build_ui()
        if self.page:
            self.update()
    
    @with_error_handling
    def add_note(self, e):
        """Add new note to database"""
        if not self.note_title.value or not self.note_content.value:
            return
        
        self.db.add_note(
            title=self.note_title.value,
            content=self.note_content.value,
            subject=self.note_subject.value or None,
            tags=self.note_tags.value or None
        )
        
        # Clear form
        self.note_title.value = ""
        self.note_content.value = ""
        self.note_subject.value = ""
        self.note_tags.value = ""
        
        self.load_content()
        self.update()
    
    def add_flashcard(self, e):
        """Add new flashcard to database"""
        if not self.flashcard_title.value or not self.flashcard_front.value or not self.flashcard_back.value:
            return
        
        self.db.add_flashcard(
            title=self.flashcard_title.value,
            front=self.flashcard_front.value,
            back=self.flashcard_back.value,
            subject=self.flashcard_subject.value or None,
            tags=self.flashcard_tags.value or None
        )
        
        # Clear form
        self.flashcard_title.value = ""
        self.flashcard_front.value = ""
        self.flashcard_back.value = ""
        self.flashcard_subject.value = ""
        self.flashcard_tags.value = ""
        
        self.load_content()
        self.update()
    
    @with_error_handling
    def load_content(self):
        """Load notes or flashcards from database"""
        self.content_list.controls.clear()
        
        if self.current_mode == "notes":
            notes = self.db.get_notes(note_type="note")
            
            if not notes:
                self.content_list.controls.append(
                    ft.Text("No notes yet", italic=True, color=ft.Colors.GREY_400)
                )
            else:
                for note_id, subject, title, content, note_type, _, _, tags, created_at in notes:
                    note_card = ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                                        ft.Text(subject if subject else "", size=12, color=ft.Colors.BLUE_300),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Text(content[:200] + "..." if len(content) > 200 else content, size=14),
                                ft.Text(f"Tags: {tags}", size=12, italic=True, color=ft.Colors.GREY_400) if tags else None,
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_color=ft.Colors.RED_400,
                                            on_click=lambda _, nid=note_id: self.delete_note(nid),
                                            tooltip="Delete note"
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                )
                            ],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.PURPLE_900,
                        padding=15,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.PURPLE_400),
                    )
                    self.content_list.controls.append(note_card)
        else:
            flashcards = self.db.get_notes(note_type="flashcard")
            
            if not flashcards:
                self.content_list.controls.append(
                    ft.Text("No flashcards yet", italic=True, color=ft.Colors.GREY_400)
                )
            else:
                for note_id, subject, title, content, note_type, front, back, tags, created_at in flashcards:
                    flashcard_card = ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                                        ft.Text(subject if subject else "", size=12, color=ft.Colors.GREEN_300),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Text(f"Q: {front[:100]}...", size=13, color=ft.Colors.GREY_300),
                                ft.Text(f"A: {back[:100]}...", size=13, color=ft.Colors.GREY_400),
                                ft.Text(f"Tags: {tags}", size=12, italic=True, color=ft.Colors.GREY_400) if tags else None,
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_color=ft.Colors.RED_400,
                                            on_click=lambda _, nid=note_id: self.delete_note(nid),
                                            tooltip="Delete flashcard"
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                )
                            ],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.GREEN_900,
                        padding=15,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.GREEN_400),
                    )
                    self.content_list.controls.append(flashcard_card)
        
        if self.page:
            self.update()
    
    @with_error_handling
    def delete_note(self, note_id):
        """Delete note or flashcard"""
        self.db.delete_note(note_id)
        self.load_content()
    
    def start_study_mode(self):
        """Start flashcard study mode"""
        flashcards = self.db.get_notes(note_type="flashcard")
        
        if not flashcards:
            return
        
        self.flashcards_to_study = list(flashcards)
        random.shuffle(self.flashcards_to_study)
        self.current_flashcard_index = 0
        self.flashcard_study_mode = True
        self.card_flipped = False
        
        self.build_ui()
        self.show_current_flashcard()
        self.update()
    
    def show_current_flashcard(self):
        """Display current flashcard in study mode"""
        if self.current_flashcard_index >= len(self.flashcards_to_study):
            # Study session complete
            self.study_area.content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.CELEBRATION, size=100, color=ft.Colors.GOLD),
                        ft.Text("🎉 Study Session Complete!", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"You reviewed {len(self.flashcards_to_study)} flashcards", size=16),
                        ft.ElevatedButton(
                            "Study Again",
                            on_click=lambda _: self.start_study_mode(),
                            bgcolor=ft.Colors.GREEN_700,
                            color="#FFFFFF"
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                alignment=ft.alignment.Alignment(0, 0),
                expand=True,
            )
            self.update()
            return
        
        note_id, subject, title, content, note_type, front, back, tags, created_at = self.flashcards_to_study[self.current_flashcard_index]
        
        # Display front or back based on flipped state
        display_text = front if not self.card_flipped else back
        display_label = "Question:" if not self.card_flipped else "Answer:"
        
        self.study_area.content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(f"Card {self.current_flashcard_index + 1} of {len(self.flashcards_to_study)}", size=16, color=ft.Colors.GREY_400),
                    ft.Text(title, size=22, weight=ft.FontWeight.BOLD),
                    ft.Text(subject if subject else "", size=14, color=ft.Colors.BLUE_300),
                    ft.Divider(),
                    ft.Text(display_label, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                    ft.Container(
                        content=ft.Text(display_text, size=18, text_align=ft.TextAlign.CENTER),
                        padding=30,
                        bgcolor=ft.Colors.BLUE_GREY_800,
                        border_radius=15,
                        alignment=ft.alignment.Alignment(0, 0),
                        height=200,
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Flip Card" if not self.card_flipped else "Next Card",
                                icon=ft.Icons.FLIP if not self.card_flipped else ft.Icons.ARROW_FORWARD,
                                on_click=lambda _: self.flip_or_next_card(),
                                bgcolor=ft.Colors.BLUE_700,
                                color="#FFFFFF"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            expand=True,
        )
        self.update()
    
    def flip_or_next_card(self):
        """Flip current card or move to next"""
        if not self.card_flipped:
            self.card_flipped = True
            self.show_current_flashcard()
        else:
            self.current_flashcard_index += 1
            self.card_flipped = False
            self.show_current_flashcard()
    
    def exit_study_mode(self):
        """Exit study mode"""
        self.flashcard_study_mode = False
        self.build_ui()
        self.update()
