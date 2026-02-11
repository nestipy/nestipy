from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable


@dataclass(frozen=True)
class CachePolicy:
    max_age: Optional[int] = None
    s_maxage: Optional[int] = None
    public: Optional[bool] = None
    private: Optional[bool] = None
    no_store: bool = False
    no_cache: bool = False
    must_revalidate: bool = False
    stale_while_revalidate: Optional[int] = None
    stale_if_error: Optional[int] = None
    vary: Optional[Iterable[str]] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None

    def build_cache_control(self) -> Optional[str]:
        directives: list[str] = []
        if self.no_store:
            directives.append("no-store")
        if self.no_cache:
            directives.append("no-cache")
        if self.public is True:
            directives.append("public")
        if self.private is True:
            directives.append("private")
        if self.must_revalidate:
            directives.append("must-revalidate")
        if self.max_age is not None:
            directives.append(f"max-age={max(0, int(self.max_age))}")
        if self.s_maxage is not None:
            directives.append(f"s-maxage={max(0, int(self.s_maxage))}")
        if self.stale_while_revalidate is not None:
            directives.append(
                f"stale-while-revalidate={max(0, int(self.stale_while_revalidate))}"
            )
        if self.stale_if_error is not None:
            directives.append(f"stale-if-error={max(0, int(self.stale_if_error))}")
        return ", ".join(directives) if directives else None

    def build_vary(self) -> Optional[str]:
        if not self.vary:
            return None
        values = [v.strip() for v in self.vary if v and str(v).strip()]
        return ", ".join(values) if values else None

