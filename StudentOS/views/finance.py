import flet as ft
from utils import UIHelpers, ValidationHelpers, ErrorHandler, show_success, show_error, with_error_handling


class ExpenseTracker(ft.Container):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.expand = True
        self.padding = 20
        self.budget_limit = 500.0  # Default budget
        
        # Form fields
        self.item_field = ft.TextField(
            label="Item Name",
            hint_text="e.g., Lunch at cafeteria",
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
            autofocus=True,
        )
        self.amount_field = ft.TextField(
            label="Amount (₱)",
            hint_text="0.00",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_700,
        )
        self.category_field = ft.Dropdown(
            label="Category",
            options=[],  # Will be loaded from database
            value=None,
            border_color=ft.Colors.BLUE_400,
        )
        
        # Load categories from database
        self.load_categories()
        
        # UI components
        self.spending_text = ft.Text(
            "₱0.00 / ₱500.00",
            size=24,
            weight=ft.FontWeight.BOLD,
        )
        self.progress_bar = ft.ProgressBar(
            value=0,
            color=ft.Colors.GREEN_700,
            bgcolor=ft.Colors.GREY_900,
            height=10,
        )
        self.budget_status = ft.Text(
            "Under budget",
            size=14,
            color=ft.Colors.GREEN_400,
        )
        
        # Expense list
        self.expense_list = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        # Add expense dialog
        self.add_dialog = ft.AlertDialog(
            title=ft.Text("Add New Expense", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                self.item_field,
                self.amount_field,
                self.category_field,
            ], tight=True, width=400, spacing=15),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.ElevatedButton(
                    "Add Expense",
                    icon=ft.Icons.ADD,
                    on_click=self.save_expense,
                    bgcolor=ft.Colors.BLUE_700,
                    color="#FFFFFF",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.build_ui()
    
    def build_ui(self):
        """Build the main UI"""
        # Budget card
        budget_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=ft.Colors.BLUE_400, size=32),
                        ft.Column([
                            ft.Text("Daily Budget Tracker", size=16, color=ft.Colors.GREY_400),
                            self.spending_text,
                        ], spacing=2),
                    ], spacing=15),
                    ft.Container(height=10),
                    self.progress_bar,
                    ft.Container(height=5),
                    self.budget_status,
                ]),
                padding=20,
            ),
            elevation=3,
        )
        
        # Expenses list card
        expenses_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Recent Expenses", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.expense_list,
                ]),
                padding=20,
            ),
            elevation=3,
        )
        
        # Load initial data
        self.refresh_data(update_ui=False)
        
        self.content = ft.Column([
                # Header
                ft.Row([
                    ft.Text("Finance", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Add Expense",
                        icon=ft.Icons.ADD,
                        on_click=self.open_dialog,
                        bgcolor=ft.Colors.BLUE_700,
                        color="#FFFFFF",
                    ),
                ]),
                ft.Divider(),
                
                budget_card,
                ft.Container(height=10),
                ft.Container(content=expenses_card, expand=True),
            ], spacing=15, expand=True)

    @with_error_handling
    def refresh_data(self, update_ui=True):
        """Refresh budget and expenses data"""
        # Get totals
        daily_total = self.db.get_daily_spending()
        expenses = self.db.get_expenses()
        
        # Update budget display
        self.spending_text.value = f"₱{daily_total:.2f} / ₱{self.budget_limit:.2f}"
        
        # Update progress bar
        progress = min(daily_total / self.budget_limit, 1.0)
        self.progress_bar.value = progress
        
        # Update status and colors
        if daily_total > self.budget_limit:
            self.progress_bar.color = ft.Colors.RED_700
            self.spending_text.color = ft.Colors.RED_400
            over_amount = daily_total - self.budget_limit
            self.budget_status.value = f"Over budget by ₱{over_amount:.2f}"
            self.budget_status.color = ft.Colors.RED_400
        elif daily_total > self.budget_limit * 0.8:
            self.progress_bar.color = ft.Colors.ORANGE_700
            self.spending_text.color = ft.Colors.ORANGE_400
            remaining = self.budget_limit - daily_total
            self.budget_status.value = f"Almost at limit. ₱{remaining:.2f} remaining"
            self.budget_status.color = ft.Colors.ORANGE_400
        else:
            self.progress_bar.color = ft.Colors.GREEN_700
            self.spending_text.color = "#FFFFFF"
            remaining = self.budget_limit - daily_total
            self.budget_status.value = f"Under budget. ₱{remaining:.2f} remaining"
            self.budget_status.color = ft.Colors.GREEN_400
        
        # Update expense list
        self.expense_list.controls.clear()
        
        if not expenses:
            self.expense_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG_OUTLINED,
                            size=80,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Text(
                            "No expenses yet",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_500,
                        ),
                        ft.Text(
                            "Click 'Add Expense' to track your spending!",
                            size=14,
                            color=ft.Colors.GREY_500,
                            italic=True,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.Alignment(0,0),
                    padding=40,
                )
            )
        else:
            for expense in expenses:
                item, amount, category, date = expense
                self.expense_list.controls.append(
                    self.create_expense_card(item, amount, category, date)
                )
        
        if update_ui:
            self.update()

    def create_expense_card(self, item, amount, category, date):
        """Create a card for displaying an expense"""
        # Category icons and colors
        category_config = {
            "Food": (ft.Icons.RESTAURANT, ft.Colors.ORANGE_700),
            "Transport": (ft.Icons.DIRECTIONS_BUS, ft.Colors.BLUE_700),
            "School": (ft.Icons.SCHOOL, ft.Colors.PURPLE_700),
            "Entertainment": (ft.Icons.MOVIE, ft.Colors.PINK_700),
            "Other": (ft.Icons.MORE_HORIZ, ft.Colors.GREY_700),
        }
        icon, color = category_config.get(category, (ft.Icons.SHOPPING_BAG, ft.Colors.GREY_700))
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, color="#FFFFFF", size=24),
                        bgcolor=color,
                        padding=10,
                        border_radius=8,
                    ),
                    ft.Column([
                        ft.Text(
                            item,
                            size=15,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"{category} • {date}",
                            size=12,
                            color=ft.Colors.GREY_400,
                        ),
                    ], spacing=2, expand=True),
                    ft.Text(
                        f"₱{amount:.2f}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.RED_400,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=15,
                bgcolor=ft.Colors.GREY_900,
                border_radius=10,
            ),
            elevation=1,
        )

    def open_dialog(self, e):
        """Open the add expense dialog"""
        self.item_field.value = ""
        self.amount_field.value = ""
        self.category_field.value = "Food"
        self.item_field.error_text = None
        self.amount_field.error_text = None
        self.page.dialog = self.add_dialog
        self.add_dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """Close the add expense dialog"""
        self.add_dialog.open = False
        self.page.update()

    @with_error_handling
    def save_expense(self, e):
        """Save a new expense to the database"""
        # Validation
        if not self.item_field.value or not self.item_field.value.strip():
            self.item_field.error_text = "Item name is required"
            self.page.update()
            self.show_snackbar("Please enter an item name", error=True)
            return
        
        try:
            amount = float(self.amount_field.value)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            self.amount_field.error_text = "Enter a valid amount"
            self.page.update()
            self.show_snackbar("Please enter a valid amount", error=True)
            return
        
        item = self.item_field.value.strip()
        category = self.category_field.value
        
        # Add to database
        self.db.add_expense(item, amount, category)
        
        # Refresh and close
        self.refresh_data()
        self.close_dialog(None)
        self.show_snackbar(f"Expense '₱{amount:.2f}' added successfully!", success=True)

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
    
    def load_categories(self):
        """Load expense categories from database"""
        try:
            # Get expense categories from database
            category_names = self.db.get_category_names("expense")
            
            # Create dropdown options
            self.category_field.options = [
                ft.dropdown.Option(name) for name in category_names
            ]
            
            # Set default value if categories exist
            if category_names:
                self.category_field.value = category_names[0]
            
        except:
            # Fallback to default categories if database fails
            self.category_field.options = [
                ft.dropdown.Option("Food"),
                ft.dropdown.Option("Transportation"),
                ft.dropdown.Option("Books"),
                ft.dropdown.Option("Entertainment"),
            ]
            self.category_field.value = "Food"






