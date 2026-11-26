"""Shared Flet reminder management dialog for Calendar events and Assignments."""

from datetime import datetime, timedelta
import flet as ft


def open_reminders_dialog(page, db, entity_type: str, entity_id: int, entity_title: str, on_change=None):
    """Open an interactive dialog to view, add, and delete scheduled reminders."""
    default_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    time_field = ft.TextField(
        label="Reminder Time (YYYY-MM-DD HH:MM)",
        value=default_time,
        width=320,
    )
    reminders_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=180)

    def refresh_list():
        reminders_column.controls.clear()
        items = db.get_reminders(entity_type, entity_id)
        if not items:
            reminders_column.controls.append(
                ft.Text("No reminders set yet.", italic=True, color=ft.Colors.GREY_400)
            )
        else:
            for rem_id, rem_time, is_sent in items:
                status_text = "Sent" if is_sent else "Scheduled"
                status_color = ft.Colors.GREY_500 if is_sent else ft.Colors.INDIGO_300
                reminders_column.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=16, color=status_color),
                                        ft.Text(rem_time, size=13, weight=ft.FontWeight.W_500),
                                        ft.Text(f"({status_text})", size=11, color=status_color),
                                    ],
                                    spacing=6,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_400,
                                    icon_size=18,
                                    tooltip="Remove reminder",
                                    on_click=lambda _, rid=rem_id: handle_delete(rid),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=ft.Colors.BLUE_GREY_900,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        border_radius=6,
                    )
                )

    def handle_add(_):
        raw = (time_field.value or "").strip()
        try:
            datetime.strptime(raw, "%Y-%m-%d %H:%M")
        except ValueError:
            if page and hasattr(page, "snack_bar"):
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Use format YYYY-MM-DD HH:MM", color="#FFFFFF"),
                    bgcolor=ft.Colors.RED_700,
                )
                page.snack_bar.open = True
                page.update()
            return

        db.add_reminder(entity_type, entity_id, raw)
        refresh_list()
        if on_change:
            on_change()
        if page:
            page.update()

    def handle_delete(rem_id: int):
        db.delete_reminder(rem_id)
        refresh_list()
        if on_change:
            on_change()
        if page:
            page.update()

    def close_dialog(_):
        dialog.open = False
        if page:
            page.update()

    refresh_list()
    dialog = ft.AlertDialog(
        title=ft.Text(f"Reminders: {entity_title}", weight=ft.FontWeight.BOLD, size=17),
        content=ft.Container(
            width=360,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            time_field,
                            ft.IconButton(
                                icon=ft.Icons.ADD_ALARM,
                                icon_color=ft.Colors.INDIGO_300,
                                tooltip="Add reminder",
                                on_click=handle_add,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    reminders_column,
                ],
                tight=True,
                spacing=10,
            ),
        ),
        actions=[ft.TextButton("Close", on_click=close_dialog)],
    )

    if page:
        page.dialog = dialog
        dialog.open = True
        page.update()
