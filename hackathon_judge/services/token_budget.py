import tiktoken

TRUNCATION_MARKER = "\n[... truncated ...]\n"

_encoder = None


def _get_encoder():
    global _encoder
    if _encoder is None:
        _encoder = tiktoken.get_encoding("cl100k_base")
    return _encoder


def count_tokens(text: str) -> int:
    if not text:
        return 0
    return len(_get_encoder().encode(text))


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    if not text:
        return text
    tokens = _get_encoder().encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated_tokens = tokens[:max_tokens]
    return _get_encoder().decode(truncated_tokens) + TRUNCATION_MARKER


class TokenBudget:
    def __init__(self, total_budget: int = 30000):
        self.total_budget = total_budget
        self.readme_budget = min(5000, total_budget // 4)
        self.tree_budget = min(2000, total_budget // 10)
        self.config_budget = min(3000, total_budget // 8)

    def allocate(
        self,
        readme: str | None,
        file_tree: str | None,
        config_files: dict[str, str] | None,
        source_files: dict[str, str] | None,
    ) -> dict:
        used = 0

        readme_out = truncate_to_tokens(readme or "", self.readme_budget)
        used += count_tokens(readme_out)

        tree_out = truncate_to_tokens(file_tree or "", self.tree_budget)
        used += count_tokens(tree_out)

        config_out = {}
        if config_files:
            for path, content in config_files.items():
                remaining = self.config_budget - sum(count_tokens(v) for v in config_out.values())
                if remaining <= 0:
                    break
                config_out[path] = truncate_to_tokens(content, remaining)
        used += sum(count_tokens(v) for v in config_out.values())

        source_out = {}
        remaining_budget = self.total_budget - used
        if source_files and remaining_budget > 0:
            for path, content in source_files.items():
                if remaining_budget <= 0:
                    break
                t = truncate_to_tokens(content, remaining_budget)
                tok = count_tokens(t)
                source_out[path] = t
                remaining_budget -= tok

        total_tokens = used + sum(count_tokens(v) for v in source_out.values())

        return {
            "readme": readme_out,
            "file_tree": tree_out,
            "config_files": config_out,
            "source_files": source_out,
            "total_tokens": total_tokens,
        }
