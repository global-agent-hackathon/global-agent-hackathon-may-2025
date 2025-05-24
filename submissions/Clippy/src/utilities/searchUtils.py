import platform
import subprocess
import sys


class SearchUtils:
    @staticmethod
    def search_files(query: str) -> list[str]:
        system = platform.system()

        if system == "Darwin":
            res = SearchUtils.macos_search_files(query)
            return res
        return []

    @staticmethod
    def macos_search_files(query: str):
        try:
            result = subprocess.run(
                [
                    "mdfind",
                    f'(kMDItemDisplayName == "*{query}*"cd) || (kMDItemPath == "*{query}*"cd)'
                ],
                capture_output=True,
                text=True
            )

            all_results = result.stdout.strip().splitlines()

            # Filter out paths that contain "/Library/"
            filtered_results = [
                path for path in all_results
                if "/Library/" not in path and not path.startswith("/Library/")
            ]

            if len(filtered_results) > 100:
                return filtered_results[:100]

            return filtered_results

        except Exception as e:
            return []
