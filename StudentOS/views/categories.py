"""Custom Categories Management View for StudentOS"""
import flet as ft

class CategoriesView(ft.Column):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.spacing = 20
        
        # Form fields
        self.category_name = ft.TextField(
            label="Category Name",
            width=300,
        )
        
        self.category_type = ft.Dropdown(
            label="Category Type",
            width=300,
            options=[
                ft.dropdown.Option("expense", "Expense"),
                ft.dropdown.Option("event", "Event"),
            ],
            value="expense"
        )
        
        self.category_color = ft.Dropdown(
            label="Color",
            width=300,
            options=[
                ft.dropdown.Option("#F44336", "🔴 Red"),
                ft.dropdown.Option("#E91E63", "🌸 Pink"),
                ft.dropdown.Option("#9C27B0", "🟣 Purple"),
                ft.dropdown.Option("#673AB7", "🟪 Deep Purple"),
                ft.dropdown.Option("#3F51B5", "🔵 Indigo"),
                ft.dropdown.Option("#2196F3", "🔷 Blue"),
                ft.dropdown.Option("#03A9F4", "🔵 Light Blue"),
                ft.dropdown.Option("#00BCD4", "🩵 Cyan"),
                ft.dropdown.Option("#009688", "🟢 Teal"),
                ft.dropdown.Option("#4CAF50", "🟢 Green"),
                ft.dropdown.Option("#8BC34A", "🍃 Light Green"),
                ft.dropdown.Option("#CDDC39", "🟡 Lime"),
                ft.dropdown.Option("#FFEB3B", "🟨 Yellow"),
                ft.dropdown.Option("#FFC107", "🟠 Amber"),
                ft.dropdown.Option("#FF9800", "🟠 Orange"),
                ft.dropdown.Option("#FF5722", "🔴 Deep Orange"),
                ft.dropdown.Option("#795548", "🟤 Brown"),
                ft.dropdown.Option("#9E9E9E", "⚪ Grey"),
                ft.dropdown.Option("#607D8B", "⚫ Blue Grey"),
            ],
            value="#607D8B"
        )
        
        # Categories lists
        self.expense_categories_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        self.event_categories_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        # Tab containers that will be shown/hidden
        self.expense_tab_container = ft.Container(
            content=self.expense_categories_list,
            height=400,
            padding=10,
            data="expense_tab"
        )
        self.event_tab_container = ft.Container(
            content=self.event_categories_list,
            height=400,
            padding=10,
            data="event_tab",
            visible=False
        )
        
        self.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("🏷️ Custom Categories", size=24, weight=ft.FontWeight.BOLD),
                    
                    ft.Row([
                        # Left panel - Add Category
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Add New Category", size=18, weight=ft.FontWeight.BOLD),
                                self.category_name,
                                self.category_type,
                                self.category_color,
                                ft.ElevatedButton(
                                    "Add Category",
                                    icon=ft.Icons.ADD_CIRCLE,
                                    on_click=self.add_category,
                                    bgcolor=ft.Colors.BLUE_700,
                                    color="#FFFFFF",
                                ),
                            ], spacing=15),
                            bgcolor=ft.Colors.BLUE_GREY_900,
                            padding=20,
                            border_radius=10,
                            width=350,
                        ),
                        
                        # Right panel - Categories Lists
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Manage Categories", size=18, weight=ft.FontWeight.BOLD),
                                
                                ft.TabBar(
                                    tabs=[
                                        ft.Tab(label="💰 Expense Categories"),
                                        ft.Tab(label="📅 Event Categories"),
                                    ],
                                    on_click=self.on_tab_change,
                                ),
                                
                                # Tab content containers
                                self.expense_tab_container,
                                self.event_tab_container,
                            ], spacing=15),
                            expand=True,
                            bgcolor=ft.Colors.BLUE_GREY_900,
                            padding=20,
                            border_radius=10,
                        ),
                    ], spacing=20, expand=True),
                ]),
                padding=20,
            )
        ]
    
    def on_tab_change(self, e):
        """Handle tab click to show/hide appropriate containers"""
        # For TabBar, we can check the index or use the control to determine which tab
        # Let's use a simple toggle approach
        if self.expense_tab_container.visible:
            # Currently showing expense, switch to event
            self.expense_tab_container.visible = False
            self.event_tab_container.visible = True
        else:
            # Currently showing event, switch to expense
            self.expense_tab_container.visible = True
            self.event_tab_container.visible = False
            
        self.expense_tab_container.update()
        self.event_tab_container.update()
    
    def add_category(self, e):
        """Add a new custom category"""
        name = self.category_name.value.strip()
        category_type = self.category_type.value
        color = self.category_color.value
        
        if not name:
            self.show_message("Please enter a category name", ft.Colors.RED_700)
            return
        
        # Check if category already exists
        existing_categories = self.db.get_category_names(category_type)
        if name in existing_categories:
            self.show_message(f"Category '{name}' already exists", ft.Colors.ORANGE_700)
            return
        
        try:
            category_id = self.db.add_custom_category(name, category_type, color)
            self.show_message(f"✅ Category '{name}' added successfully", ft.Colors.GREEN_700)
            
            # Clear form
            self.category_name.value = ""
            self.category_name.update()
            
            # Refresh categories list
            self.load_categories()
            
        except Exception as ex:
            self.show_message(f"Failed to add category: {str(ex)}", ft.Colors.RED_700)
    
    def load_categories(self):
        """Load and display categories"""
        # Clear lists
        self.expense_categories_list.controls.clear()
        self.event_categories_list.controls.clear()
        
        # Load expense categories
        expense_categories = self.db.get_categories("expense")
        if not expense_categories:
            self.expense_categories_list.controls.append(
                ft.Text("No expense categories yet", italic=True, color=ft.Colors.GREY_400)
            )
        else:
            for category_id, name, category_type, color, is_default in expense_categories:
                category_card = self.create_category_card(category_id, name, color, bool(is_default))
                self.expense_categories_list.controls.append(category_card)
        
        # Load event categories
        event_categories = self.db.get_categories("event")
        if not event_categories:
            self.event_categories_list.controls.append(
                ft.Text("No event categories yet", italic=True, color=ft.Colors.GREY_400)
            )
        else:
            for category_id, name, category_type, color, is_default in event_categories:
                category_card = self.create_category_card(category_id, name, color, bool(is_default))
                self.event_categories_list.controls.append(category_card)
        
        if hasattr(self, 'page') and self.page:
            self.update()
    
    def create_category_card(self, category_id: int, name: str, color: str, is_default: bool):
        """Create a category card"""
        return ft.Container(
            content=ft.Row([
                # Color indicator
                ft.Container(
                    width=12,
                    height=12,
                    bgcolor=color,
                    border_radius=6,
                ),
                
                # Category name
                ft.Text(name, size=16, weight=ft.FontWeight.BOLD, expand=True),
                
                # Default indicator
                ft.Container(
                    content=ft.Text("Default", size=10, color="#FFFFFF"),
                    bgcolor=ft.Colors.GREY_600,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    border_radius=10,
                    visible=is_default,
                ),
                
                # Edit button (only for custom categories)
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color=ft.Colors.BLUE_400,
                    tooltip="Edit category",
                    on_click=lambda _, cid=category_id, cname=name, ccol=color: self.edit_category(cid, cname, ccol),
                    disabled=is_default,
                ),
                
                # Delete button (only for custom categories)
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Delete category",
                    on_click=lambda _, cid=category_id, cname=name: self.delete_category(cid, cname),
                    disabled=is_default,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=ft.Colors.BLUE_GREY_800,
            padding=12,
            border_radius=8,
            border=ft.border.all(1, color),
        )
    
    def edit_category(self, category_id: int, current_name: str, current_color: str):
        """Edit a custom category"""
        def save_changes(name, color):
            try:
                self.db.update_custom_category(category_id, name, color)
                self.show_message(f"✅ Category '{name}' updated", ft.Colors.GREEN_700)
                self.load_categories()
            except Exception as ex:
                self.show_message(f"Failed to update category: {str(ex)}", ft.Colors.RED_700)
        
        # Create edit dialog
        name_field = ft.TextField(value=current_name, label="Category Name", width=300)
        color_dropdown = ft.Dropdown(
            label="Color",
            width=300,
            value=current_color,
            options=self.category_color.options
        )
        
        def on_save(e):
            if name_field.value.strip():
                save_changes(name_field.value.strip(), color_dropdown.value)
                dialog.open = False
                if hasattr(self, 'page') and self.page:
                    self.page.update()
        
        def on_cancel(e):
            dialog.open = False
            if hasattr(self, 'page') and self.page:
                self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Edit Category"),
            content=ft.Column([name_field, color_dropdown], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=on_cancel),
                ft.ElevatedButton("Save", on_click=on_save, bgcolor=ft.Colors.BLUE_700),
            ],
        )
        
        if hasattr(self, 'page') and self.page:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
    
    def delete_category(self, category_id: int, name: str):
        """Delete a custom category"""
        def confirm_delete(e):
            try:
                self.db.delete_custom_category(category_id)
                self.show_message(f"🗑️ Category '{name}' deleted", ft.Colors.ORANGE_700)
                self.load_categories()
            except Exception as ex:
                self.show_message(f"Failed to delete category: {str(ex)}", ft.Colors.RED_700)
            
            dialog.open = False
            if hasattr(self, 'page') and self.page:
                self.page.update()
        
        def cancel_delete(e):
            dialog.open = False
            if hasattr(self, 'page') and self.page:
                self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Delete Category"),
            content=ft.Text(f"Are you sure you want to delete the category '{name}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton("Delete", on_click=confirm_delete, bgcolor=ft.Colors.RED_700),
            ],
        )
        
        if hasattr(self, 'page') and self.page:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
    
    def show_message(self, message: str, color):
        """Show a snack bar message"""
        if hasattr(self, 'page') and self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message, color="#FFFFFF"),
                bgcolor=color,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def did_mount(self):
        """Called when the control is added to the page"""
        self.load_categories()