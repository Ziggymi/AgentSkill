#!/usr/bin/env python3
"""Print the fixed repository policy without accessing credentials or network."""

import json


def main() -> None:
    print(
        json.dumps(
            {
                "repository": "https://github.com/Ziggymi/AgentSkill.git",
                "branch": "main",
                "readme_language": "zh-CN",
                "force_push": False,
                "exact_path_staging": True,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
