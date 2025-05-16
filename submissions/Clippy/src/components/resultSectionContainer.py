import flet as ft
from utilities.fileUtils import *


def ResultSectionContainer(section: str, paths: list[str], page: ft.Page) -> ft.Container:
    file_items = []

    for index, path in enumerate(paths):
        file_items.append(
            ft.Container(
                bgcolor="#1c2231",
                border=ft.border.all(width=1, color="#374151"),
                padding=ft.padding.all(16),
                border_radius=12,
                width=page.width,
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=(
                                ft.Icons.PLAY_CIRCLE_OUTLINE if section == "Audio" else
                                ft.Icons.IMAGE_OUTLINED if section == "Images" else
                                ft.Icons.VIDEO_LIBRARY_OUTLINED if section == "Video" else
                                ft.Icons.CODE if section == "Code" else
                                ft.Icons.TEXT_SNIPPET_OUTLINED if section == "Text Documents" else
                                ft.Icons.ARCHIVE_OUTLINED if section == "Archives" else
                                ft.Icons.SETTINGS_APPLICATIONS if section == "Config Data" else
                                ft.Icons.FONT_DOWNLOAD_OUTLINED if section == "Fonts" else
                                ft.Icons.DISC_FULL if section == "Disk Images" else
                                ft.Icons.DATASET_OUTLINED if section == "Executables" else
                                ft.Icons.HELP_OUTLINED
                            ),
                            color="#0ea5e9",
                            size=30
                        ),
                        ft.Column(
                            expand=False,
                            spacing=2,
                            controls=[
                                ft.Text(FileUtils.getFilename(path), style=ft.TextStyle(
                                    weight=ft.FontWeight.BOLD, size=14)),
                                ft.Text(path, style=ft.TextStyle(
                                    size=10, color=ft.Colors.GREY), width=500)
                            ]
                        )
                    ]
                )
            )
        )

    return ft.Container(
        padding=ft.padding.all(10),
        width=page.width,
        border=ft.border.all(width=2, color="#0ea5e933"),
        shadow=ft.BoxShadow(
            blur_radius=15,
            spread_radius=-3,
            offset=ft.Offset(0, 0),
            color="#0ea5e933"
        ),
        bgcolor="#1c2536",
        border_radius=ft.border_radius.all(12),
        content=ft.Column(
            expand=False,
            spacing=10,
            controls=[
                ft.Text(section, style=ft.TextStyle(
                    size=20, weight=ft.FontWeight.W_600, color="#0ea5e9"))
            ] + file_items
        )
    )
