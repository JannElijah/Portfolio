"""
Utility functions and classes for StudentOS improvements
"""
import flet as ft
import functools
import threading
import time


class UIHelpers:
    """Helper class for consistent UI improvements"""
    
    @staticmethod
    def create_scrollable_container(content, height=None, expand=True):
        """Create a standardized scrollable container"""
        return ft.Container(
            content=ft.Column([content], scroll=ft.ScrollMode.ADAPTIVE, expand=True) if expand else content,
            height=height,
            expand=expand,
        )
    
    @staticmethod
    def create_loading_indicator(text="Loading..."):
        """Create a standardized loading indicator"""
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=4),
                ft.Text(text, size=14, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            alignment=ft.alignment.center,
            height=100,
        )
    
    @staticmethod
    def show_success_snackbar(page, message):
        """Show success snackbar"""
        if page and hasattr(page, 'snack_bar'):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ {message}", color="#FFFFFF"),
                bgcolor=ft.Colors.GREEN_700,
            )
            page.snack_bar.open = True
            page.update()
    
    @staticmethod
    def show_error_snackbar(page, message):
        """Show error snackbar"""
        if page and hasattr(page, 'snack_bar'):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ {message}", color="#FFFFFF"),
                bgcolor=ft.Colors.RED_700,
                duration=5000,  # Longer for errors
            )
            page.snack_bar.open = True
            page.update()
    
    @staticmethod
    def show_warning_snackbar(page, message):
        """Show warning snackbar"""
        if page and hasattr(page, 'snack_bar'):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"⚠️ {message}", color="#FFFFFF"),
                bgcolor=ft.Colors.ORANGE_700,
            )
            page.snack_bar.open = True
            page.update()
    
    @staticmethod
    def show_info_snackbar(page, message):
        """Show info snackbar"""
        if page and hasattr(page, 'snack_bar'):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"ℹ️ {message}", color="#FFFFFF"),
                bgcolor=ft.Colors.BLUE_700,
            )
            page.snack_bar.open = True
            page.update()


class ValidationHelpers:
    """Input validation helpers"""
    
    @staticmethod
    def validate_required_field(field, field_name="Field"):
        """Validate required text field"""
        if not field.value or not field.value.strip():
            field.error_text = f"{field_name} is required"
            return False
        field.error_text = None
        return True
    
    @staticmethod
    def validate_number_field(field, field_name="Number", min_val=None, max_val=None):
        """Validate number field"""
        try:
            value = float(field.value)
            if min_val is not None and value < min_val:
                field.error_text = f"{field_name} must be at least {min_val}"
                return False, None
            if max_val is not None and value > max_val:
                field.error_text = f"{field_name} must be at most {max_val}"
                return False, None
            field.error_text = None
            return True, value
        except (ValueError, TypeError):
            field.error_text = f"Enter a valid {field_name.lower()}"
            return False, None
    
    @staticmethod
    def validate_email_field(field):
        """Validate email field"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if field.value and not re.match(email_pattern, field.value):
            field.error_text = "Enter a valid email address"
            return False
        field.error_text = None
        return True
    
    @staticmethod
    def validate_date_field(field, field_name="Date"):
        """Validate date field"""
        from datetime import datetime
        try:
            if field.value:
                datetime.strptime(field.value, "%Y-%m-%d")
            field.error_text = None
            return True
        except ValueError:
            field.error_text = f"Enter a valid {field_name.lower()} (YYYY-MM-DD)"
            return False


class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def with_error_handling(func):
        """Decorator for automatic error handling"""
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                print(f"Error in {func.__name__}: {error_msg}")  # For debugging
                
                # Show error to user if page is available
                try:
                    if hasattr(self, 'page') and self.page:
                        UIHelpers.show_error_snackbar(self.page, error_msg)
                except:
                    # Page not available yet, just print error
                    pass
                
                return None
        return wrapper
    
    @staticmethod
    def safe_operation(operation, fallback=None, error_message="Operation failed"):
        """Safely execute an operation with fallback"""
        try:
            return operation()
        except Exception as e:
            print(f"Safe operation failed: {str(e)}")
            return fallback


class AsyncUIHelpers:
    """Helpers for async operations with loading states"""
    
    @staticmethod
    def with_loading_state(loading_container, operation_func, callback_func=None):
        """Execute operation with loading state"""
        def run_operation():
            try:
                # Show loading
                loading_container.content = UIHelpers.create_loading_indicator()
                loading_container.update()
                
                # Execute operation
                result = operation_func()
                
                # Handle success
                if callback_func:
                    callback_func(result, None)
            except Exception as e:
                # Handle error
                if callback_func:
                    callback_func(None, str(e))
        
        # Run in background thread
        threading.Thread(target=run_operation, daemon=True).start()


class PerformanceHelpers:
    """Performance optimization helpers"""
    
    @staticmethod
    def debounce(wait_time):
        """Decorator to debounce function calls"""
        def decorator(func):
            timer = None
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                nonlocal timer
                if timer:
                    timer.cancel()
                timer = threading.Timer(wait_time, func, args, kwargs)
                timer.start()
            
            return wrapper
        return decorator
    
    @staticmethod
    def throttle(interval):
        """Decorator to throttle function calls"""
        def decorator(func):
            last_called = [0]
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                now = time.time()
                if now - last_called[0] >= interval:
                    last_called[0] = now
                    return func(*args, **kwargs)
            
            return wrapper
        return decorator


class ResponsiveHelpers:
    """Responsive design helpers"""
    
    @staticmethod
    def get_responsive_width(page_width, small=300, medium=600, large=900):
        """Get responsive width based on page size"""
        if page_width < 768:
            return small
        elif page_width < 1024:
            return medium
        else:
            return large
    
    @staticmethod
    def create_responsive_row(controls, spacing=20):
        """Create responsive row that wraps on small screens"""
        return ft.Row(
            controls,
            spacing=spacing,
            wrap=True,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )


class KeyboardHelpers:
    """Keyboard shortcut helpers"""
    
    @staticmethod
    def setup_form_shortcuts(page, submit_func, cancel_func=None):
        """Setup common form keyboard shortcuts"""
        def on_keyboard(e: ft.KeyboardEvent):
            if e.key == "Enter" and e.ctrl:
                submit_func()
            elif e.key == "Escape" and cancel_func:
                cancel_func()
        
        page.on_keyboard_event = on_keyboard


class DataHelpers:
    """Data handling helpers"""
    
    @staticmethod
    def safe_get_value(obj, key, default=None):
        """Safely get value from object/dict"""
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
            else:
                return getattr(obj, key, default)
        except:
            return default
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def truncate_text(text, max_length=100, suffix="..."):
        """Truncate text with ellipsis"""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix


# Quick access to common functions
show_success = UIHelpers.show_success_snackbar
show_error = UIHelpers.show_error_snackbar
show_warning = UIHelpers.show_warning_snackbar
show_info = UIHelpers.show_info_snackbar
validate_required = ValidationHelpers.validate_required_field
validate_number = ValidationHelpers.validate_number_field
with_error_handling = ErrorHandler.with_error_handling
safe_operation = ErrorHandler.safe_operation