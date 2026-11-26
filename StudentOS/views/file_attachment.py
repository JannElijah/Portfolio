"""File Attachment Widget for StudentOS"""
import flet as ft
import os
from datetime import datetime

class FileAttachmentWidget(ft.Column):
    def __init__(self, db, entity_type: str, entity_id: int = None, on_file_change=None):
        super().__init__()
        self.db = db
        self.entity_type = entity_type  # 'assignment', 'project', 'note'
        self.entity_id = entity_id
        self.on_file_change = on_file_change
        
        # Create uploads directory if it doesn't exist
        self.uploads_dir = os.path.join(os.getcwd(), "uploads", entity_type + "s")
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        self.spacing = 10
        self.attached_files = []
        
        # File picker
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self.on_file_selected
        
        # Add file button
        self.add_file_button = ft.ElevatedButton(
            "📎 Attach File",
            icon=ft.Icons.ATTACH_FILE,
            on_click=self.open_file_picker,
            bgcolor=ft.Colors.BLUE_700,
            color="#FFFFFF",
            disabled=self.entity_id is None
        )
        
        # Files list
        self.files_list = ft.Column(spacing=8)
        
        self.controls = [
            ft.Row([
                ft.Text("📎 File Attachments", size=16, weight=ft.FontWeight.BOLD),
                self.add_file_button,
            ]),
            self.files_list,
            self.file_picker,
        ]
        
        if self.entity_id:
            self.load_attachments()
    
    def set_entity_id(self, entity_id: int):
        """Set the entity ID and enable file operations"""
        self.entity_id = entity_id
        self.add_file_button.disabled = False
        self.load_attachments()
        self.update()
    
    def open_file_picker(self, e):
        """Open file picker dialog"""
        if not self.entity_id:
            return
        
        self.file_picker.pick_files(
            dialog_title="Select files to attach",
            allow_multiple=True,
            allowed_extensions=["pdf", "docx", "txt", "png", "jpg", "jpeg", "zip", "xlsx", "pptx"]
        )
    
    def on_file_selected(self, e):
        """Handle selected files"""
        if not e.files or not self.entity_id:
            return
        
        for file in e.files:
            try:
                # Copy file to uploads directory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = f"{timestamp}_{file.name.replace(' ', '_')}"
                dest_path = os.path.join(self.uploads_dir, safe_name)
                
                # Copy file
                import shutil
                shutil.copy2(file.path, dest_path)
                
                # Add to database
                self.db.add_file_attachment(self.entity_type, self.entity_id, safe_name)
                
                # Add to UI
                self.add_file_card(safe_name, file.name)
                
                if self.on_file_change:
                    self.on_file_change()
                    
            except Exception as ex:
                # Show error
                if hasattr(self.page, 'snack_bar'):
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Failed to attach {file.name}: {str(ex)}", color="#FFFFFF"),
                        bgcolor=ft.Colors.RED_700,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
        
        self.update()
    
    def load_attachments(self):
        """Load existing file attachments"""
        if not self.entity_id:
            return
        
        self.files_list.controls.clear()
        self.attached_files = self.db.get_file_attachments(self.entity_type, self.entity_id)
        
        if not self.attached_files:
            self.files_list.controls.append(
                ft.Text("No files attached", italic=True, color=ft.Colors.GREY_400, size=14)
            )
        else:
            for file_name in self.attached_files:
                # Extract original name (remove timestamp prefix)
                original_name = "_".join(file_name.split("_")[2:]) if "_" in file_name else file_name
                self.add_file_card(file_name, original_name)
    
    def add_file_card(self, stored_name: str, display_name: str):
        """Add a file card to the UI"""
        file_path = os.path.join(self.uploads_dir, stored_name)
        file_exists = os.path.exists(file_path)
        
        # File extension icon
        ext = display_name.split('.')[-1].lower() if '.' in display_name else 'file'
        icon_map = {
            'pdf': ft.Icons.PICTURE_AS_PDF,
            'docx': ft.Icons.DESCRIPTION,
            'doc': ft.Icons.DESCRIPTION,
            'txt': ft.Icons.TEXT_SNIPPET,
            'png': ft.Icons.IMAGE,
            'jpg': ft.Icons.IMAGE,
            'jpeg': ft.Icons.IMAGE,
            'zip': ft.Icons.ARCHIVE,
            'xlsx': ft.Icons.TABLE_CHART,
            'xls': ft.Icons.TABLE_CHART,
            'pptx': ft.Icons.SLIDESHOW,
            'ppt': ft.Icons.SLIDESHOW,
        }
        icon = icon_map.get(ext, ft.Icons.ATTACH_FILE)
        
        # File size
        try:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            size_text = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{os.path.getsize(file_path) / 1024:.1f} KB"
        except:
            size_text = "N/A"
        
        file_card = ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=ft.Colors.BLUE_400, size=20),
                ft.Column([
                    ft.Text(display_name, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{ext.upper()} • {size_text}", size=12, color=ft.Colors.GREY_400),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=ft.Icons.OPEN_IN_NEW,
                    icon_color=ft.Colors.GREEN_400,
                    tooltip="Open file",
                    on_click=lambda _, fn=stored_name: self.open_file(fn),
                    disabled=not file_exists
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Remove attachment",
                    on_click=lambda _, fn=stored_name: self.remove_file(fn)
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=ft.Colors.BLUE_GREY_800 if file_exists else ft.Colors.GREY_800,
            padding=10,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.BLUE_400 if file_exists else ft.Colors.GREY_600),
        )
        
        self.files_list.controls.append(file_card)
    
    def open_file(self, file_name: str):
        """Open file with system default application"""
        file_path = os.path.join(self.uploads_dir, file_name)
        
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
                
        except Exception as ex:
            if hasattr(self.page, 'snack_bar'):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to open file: {str(ex)}", color="#FFFFFF"),
                    bgcolor=ft.Colors.RED_700,
                )
                self.page.snack_bar.open = True
                self.page.update()
    
    def remove_file(self, file_name: str):
        """Remove file attachment"""
        if not self.entity_id:
            return
        
        # Remove from database
        self.db.remove_file_attachment(self.entity_type, self.entity_id, file_name)
        
        # Delete physical file
        file_path = os.path.join(self.uploads_dir, file_name)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass  # File might be in use or already deleted
        
        # Refresh UI
        self.load_attachments()
        self.update()
        
        if self.on_file_change:
            self.on_file_change()
        
        if hasattr(self.page, 'snack_bar'):
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("🗑️ File attachment removed", color="#FFFFFF"),
                bgcolor=ft.Colors.ORANGE_700,
            )
            self.page.snack_bar.open = True
            self.page.update()