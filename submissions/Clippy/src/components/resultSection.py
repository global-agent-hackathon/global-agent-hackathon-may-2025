import flet as ft
from components.resultSectionContainer import *


def resultSection(grouped_path: dict, page: ft.Page) -> ft.Column:
    if not dict:
        return ft.Container()
    contents = []
    for group, paths in grouped_path.items():
        contents.append(ResultSectionContainer(group, paths, page))
    return ft.Column(
        expand=False,
        scroll=ft.ScrollMode.ALWAYS,
        controls=contents,
    )
