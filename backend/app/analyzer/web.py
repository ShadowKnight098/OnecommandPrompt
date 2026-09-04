"""Web, HTML/CSS, React, Vite, Vue, and Node.js project analyzer engine."""
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import json
import re
from app.models.project import (
    DependencyItem,
    EntryPointCandidate,
    WebMetadata,
)


class WebProjectAnalyzer:
    """Deep inspection engine for HTML, CSS, React, Vue, Vite, Next.js, and Node.js projects."""

    COMMON_HTML_ENTRIES = {
        "index.html": 50,
        "index.htm": 45,
        "main.html": 40,
        "app.html": 35,
        "home.html": 30,
        "default.html": 25,
    }

    COMMON_JS_ENTRIES = {
        "src/main.jsx": 50,
        "src/main.tsx": 50,
        "src/index.jsx": 48,
        "src/index.tsx": 48,
        "src/app.jsx": 45,
        "src/app.tsx": 45,
        "src/main.js": 42,
        "src/main.ts": 42,
        "src/index.js": 40,
        "src/index.ts": 40,
        "src/app.js": 38,
        "app/page.tsx": 45,
        "app/page.jsx": 45,
        "pages/index.tsx": 45,
        "pages/index.jsx": 45,
        "server.js": 35,
        "app.js": 35,
        "index.js": 30,
    }

    CDN_PATTERNS = {
        "Tailwind CSS": [r"cdn\.tailwindcss\.com", r"tailwindcss.*\.css"],
        "Bootstrap": [r"bootstrap.*\.css", r"bootstrap.*\.js", r"cdn\.jsdelivr\.net.*bootstrap"],
        "React (CDN)": [r"unpkg\.com/react", r"react(\.production|\.development)?\.js"],
        "Vue (CDN)": [r"vue(\.global)?(\.prod)?\.js", r"cdn\.jsdelivr\.net/npm/vue"],
        "Alpine.js": [r"alpine(\.min)?\.js", r"cdn\.jsdelivr\.net.*alpinejs"],
        "HTMX": [r"htmx(\.min)?\.js", r"unpkg\.com/htmx\.org"],
        "jQuery": [r"jquery(\.min)?\.js", r"code\.jquery\.com"],
        "FontAwesome": [r"font-awesome", r"fontawesome", r"cdnjs\.cloudflare\.com.*font-awesome"],
        "Google Fonts": [r"fonts\.googleapis\.com"],
        "Three.js": [r"three(\.min)?\.js", r"cdnjs\.cloudflare\.com.*three\.js"],
        "Chart.js": [r"chart(\.min)?\.js", r"cdn\.jsdelivr\.net.*chart\.js"],
        "Axios": [r"axios(\.min)?\.js", r"cdn\.jsdelivr\.net/npm/axios"],
        "Lucide Icons": [r"lucide(\.min)?\.js", r"unpkg\.com/lucide"],
    }

    @classmethod
    def scan_web_project(cls, project_root: Path) -> Dict[str, Any]:
        """
        Inspects project files to detect web technologies, package.json dependencies,
        HTML/CSS structures, framework types, dev commands, and ports.
        """
        html_files: List[Path] = []
        js_files: List[Path] = []
        css_files: List[Path] = []
        
        # Exclude common build and dependency directories
        ignored_dirs = {".git", "node_modules", "dist", "build", ".next", ".nuxt", ".output", ".venv", "__pycache__"}

        for p in project_root.rglob("*"):
            if any(part in ignored_dirs for part in p.parts):
                continue
            if p.is_file():
                suffix = p.suffix.lower()
                if suffix in [".html", ".htm"]:
                    html_files.append(p)
                elif suffix in [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"]:
                    js_files.append(p)
                elif suffix in [".css", ".scss", ".sass", ".less"]:
                    css_files.append(p)

        package_json_path = project_root / "package.json"
        has_package_json = package_json_path.exists()

        # 1. Inspect package.json if present
        pkg_info = cls._inspect_package_json(package_json_path) if has_package_json else {}

        # 2. Inspect HTML files (for static or SPA projects)
        html_meta = cls._inspect_html_files(html_files, project_root)

        # 3. Detect Package Manager
        package_manager = cls._detect_package_manager(project_root)

        # 4. Determine Project Type & Framework
        project_type, ui_framework, css_framework, dev_cmd, target_port = cls._classify_web_project(
            project_root, pkg_info, html_meta, html_files, js_files
        )

        # 5. Extract Candidate Entry Points
        candidates, primary_entry = cls._find_entry_points(
            project_root, project_type, html_files, js_files, pkg_info
        )

        # 6. Build Dependency Items
        dependencies = cls._build_dependency_items(pkg_info, html_meta)

        # 7. Construct WebMetadata
        web_metadata = WebMetadata(
            html_title=html_meta.get("title"),
            stylesheets=html_meta.get("stylesheets", []),
            scripts=html_meta.get("scripts", []),
            cdn_libraries=html_meta.get("cdn_libraries", []),
            package_manager=package_manager,
            dev_command=dev_cmd,
            build_command=pkg_info.get("scripts", {}).get("build"),
            target_port=target_port,
            node_requirement=pkg_info.get("engines", {}).get("node", ">=18.0.0"),
            ui_framework=ui_framework,
            css_framework=css_framework,
        )

        return {
            "is_web_project": bool(has_package_json or html_files),
            "project_type": project_type,
            "ui_framework": ui_framework,
            "css_framework": css_framework,
            "entry_point": primary_entry,
            "candidate_entry_points": candidates,
            "dependencies": dependencies,
            "dependency_source": "package.json" if has_package_json else ("cdn" if html_meta.get("cdn_libraries") else "html_static"),
            "web_metadata": web_metadata,
            "has_package_json": has_package_json,
            "html_count": len(html_files),
            "js_count": len(js_files),
            "css_count": len(css_files),
        }

    @classmethod
    def _inspect_package_json(cls, pkg_path: Path) -> Dict[str, Any]:
        """Reads and extracts metadata from package.json."""
        try:
            data = json.loads(pkg_path.read_text(encoding="utf-8", errors="ignore"))
            return {
                "name": data.get("name", "web-project"),
                "version": data.get("version", "1.0.0"),
                "scripts": data.get("scripts", {}),
                "dependencies": data.get("dependencies", {}),
                "devDependencies": data.get("devDependencies", {}),
                "engines": data.get("engines", {}),
            }
        except Exception:
            return {}

    @classmethod
    def _inspect_html_files(cls, html_files: List[Path], project_root: Path) -> Dict[str, Any]:
        """Scans HTML files to extract title, linked styles, scripts, and CDN libraries."""
        title: Optional[str] = None
        stylesheets: List[str] = []
        scripts: List[str] = []
        detected_cdns: List[str] = []

        # Sort to inspect index.html first
        sorted_html = sorted(
            html_files,
            key=lambda p: 0 if p.name.lower() in ["index.html", "index.htm"] else 1
        )

        for html_path in sorted_html[:5]:  # inspect top 5 HTML files
            try:
                content = html_path.read_text(encoding="utf-8", errors="ignore")
                
                # Extract <title>
                if not title:
                    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        title = title_match.group(1).strip()

                # Extract linked stylesheets <link rel="stylesheet" href="...">
                link_matches = re.findall(r"""<link[^>]+href=["']([^"']+)["'][^>]*>""", content, re.IGNORECASE)
                for link in link_matches:
                    if ".css" in link.lower() and link not in stylesheets:
                        stylesheets.append(link)

                # Extract <script src="...">
                script_matches = re.findall(r"""<script[^>]+src=["']([^"']+)["'][^>]*>""", content, re.IGNORECASE)
                for src in script_matches:
                    if src not in scripts:
                        scripts.append(src)

                # Detect CDN libraries
                for lib_name, patterns in cls.CDN_PATTERNS.items():
                    if lib_name not in detected_cdns:
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                detected_cdns.append(lib_name)
                                break

            except Exception:
                continue

        return {
            "title": title,
            "stylesheets": stylesheets[:15],
            "scripts": scripts[:15],
            "cdn_libraries": detected_cdns,
        }

    @classmethod
    def _detect_package_manager(cls, project_root: Path) -> str:
        """Determines whether to use npm, pnpm, yarn, or bun based on lockfiles."""
        if (project_root / "pnpm-lock.yaml").exists():
            return "pnpm"
        if (project_root / "yarn.lock").exists():
            return "yarn"
        if (project_root / "bun.lockb").exists() or (project_root / "bun.lock").exists():
            return "bun"
        return "npm"

    @classmethod
    def _classify_web_project(
        cls,
        project_root: Path,
        pkg_info: Dict[str, Any],
        html_meta: Dict[str, Any],
        html_files: List[Path],
        js_files: List[Path],
    ) -> Tuple[str, Optional[str], Optional[str], Optional[str], int]:
        """Classifies framework, CSS library, dev command, and port."""
        deps = {**pkg_info.get("dependencies", {}), **pkg_info.get("devDependencies", {})}
        scripts = pkg_info.get("scripts", {})

        ui_framework: Optional[str] = None
        css_framework: Optional[str] = None
        project_type: str = "static_html"
        dev_cmd: Optional[str] = None
        target_port: int = 8080

        # Check for config files
        has_vite_config = any((project_root / f"vite.config.{ext}").exists() for ext in ["js", "ts", "mjs", "cjs"])
        has_next_config = any((project_root / f"next.config.{ext}").exists() for ext in ["js", "mjs", "ts"])
        has_tailwind_config = any((project_root / f"tailwind.config.{ext}").exists() for ext in ["js", "ts", "cjs", "mjs"])

        # 1. UI Framework Detection from package.json
        if "next" in deps or has_next_config:
            project_type = "nextjs"
            ui_framework = "nextjs"
            target_port = 3000
        elif "react" in deps or "react-dom" in deps:
            project_type = "vite" if (has_vite_config or "vite" in deps) else "react"
            ui_framework = "react"
            target_port = 5173 if has_vite_config else 3000
        elif "vue" in deps or "nuxt" in deps:
            project_type = "vite" if (has_vite_config or "vite" in deps) else "vue"
            ui_framework = "vue"
            target_port = 5173 if has_vite_config else 3000
        elif "svelte" in deps or "@sveltejs/kit" in deps:
            project_type = "svelte"
            ui_framework = "svelte"
            target_port = 5173
        elif "express" in deps or "fastify" in deps or "koa" in deps:
            project_type = "nodejs"
            ui_framework = "express"
            target_port = 3000
        elif pkg_info:
            project_type = "nodejs"
            ui_framework = "nodejs"
            target_port = 3000
        elif html_files:
            project_type = "static_html"
            ui_framework = "html5"
            target_port = 8080

        # 2. CSS Framework Detection
        if "tailwindcss" in deps or has_tailwind_config or "Tailwind CSS" in html_meta.get("cdn_libraries", []):
            css_framework = "tailwind"
        elif "bootstrap" in deps or "Bootstrap" in html_meta.get("cdn_libraries", []):
            css_framework = "bootstrap"
        elif "bulma" in deps:
            css_framework = "bulma"
        elif "@mui/material" in deps or "@chakra-ui/react" in deps:
            css_framework = "component_library"
        elif html_meta.get("stylesheets"):
            css_framework = "custom_css"

        # 3. Determine Dev / Run Command
        if scripts:
            if "dev" in scripts:
                dev_cmd = "npm run dev"
            elif "start" in scripts:
                dev_cmd = "npm start"
            elif "serve" in scripts:
                dev_cmd = "npm run serve"
            elif "preview" in scripts:
                dev_cmd = "npm run preview"
        
        if not dev_cmd and project_type == "static_html":
            dev_cmd = "python -m http.server 8080"

        return project_type, ui_framework, css_framework, dev_cmd, target_port

    @classmethod
    def _find_entry_points(
        cls,
        project_root: Path,
        project_type: str,
        html_files: List[Path],
        js_files: List[Path],
        pkg_info: Dict[str, Any],
    ) -> Tuple[List[EntryPointCandidate], Optional[str]]:
        """Identifies and scores candidate entry points for web and node projects."""
        candidates: List[EntryPointCandidate] = []
        scores: Dict[str, int] = {}

        # 1. Score HTML files
        for html in html_files:
            try:
                rel = html.relative_to(project_root).as_posix()
                score = cls.COMMON_HTML_ENTRIES.get(html.name.lower(), 15)
                # Top level bonus
                if len(html.relative_to(project_root).parts) == 1:
                    score += 20
                scores[rel] = score

                content = html.read_text(encoding="utf-8", errors="ignore")
                lines = [l.strip() for l in content.splitlines() if l.strip()][:8]

                candidates.append(
                    EntryPointCandidate(
                        file_path=rel,
                        score=score,
                        has_main_block=False,
                        framework="html5",
                        preview_lines=lines,
                    )
                )
            except Exception:
                continue

        # 2. Score JS/TS/JSX files
        for js in js_files:
            try:
                rel = js.relative_to(project_root).as_posix()
                score = 0
                for pattern, pts in cls.COMMON_JS_ENTRIES.items():
                    if rel.lower() == pattern or rel.lower().endswith(pattern):
                        score = pts
                        break
                
                if score > 0:
                    content = js.read_text(encoding="utf-8", errors="ignore")
                    lines = [l.strip() for l in content.splitlines() if l.strip()][:8]
                    candidates.append(
                        EntryPointCandidate(
                            file_path=rel,
                            score=score,
                            has_main_block=False,
                            framework="react" if "jsx" in rel or "tsx" in rel else "javascript",
                            preview_lines=lines,
                        )
                    )
            except Exception:
                continue

        # Sort candidates descending by score
        candidates.sort(key=lambda c: c.score, reverse=True)
        primary_entry = candidates[0].file_path if candidates else None

        # If it's a Node/React project with an index.html or npm script, prefer index.html or package.json
        if (project_root / "index.html").exists():
            primary_entry = "index.html"

        return candidates, primary_entry

    @classmethod
    def _build_dependency_items(
        cls,
        pkg_info: Dict[str, Any],
        html_meta: Dict[str, Any],
    ) -> List[DependencyItem]:
        """Converts package.json packages and detected CDN scripts into DependencyItems."""
        items: List[DependencyItem] = []

        # From package.json dependencies
        for pkg, ver in pkg_info.get("dependencies", {}).items():
            items.append(
                DependencyItem(
                    name=pkg,
                    version_specifier=str(ver),
                    source="package.json",
                    enabled=True,
                    confidence=1.0,
                )
            )

        # From package.json devDependencies
        for pkg, ver in pkg_info.get("devDependencies", {}).items():
            items.append(
                DependencyItem(
                    name=f"{pkg} (dev)",
                    version_specifier=str(ver),
                    source="package.json",
                    enabled=True,
                    confidence=0.9,
                )
            )

        # From CDN scripts (if not using package.json)
        if not items and html_meta.get("cdn_libraries"):
            for lib in html_meta["cdn_libraries"]:
                items.append(
                    DependencyItem(
                        name=lib,
                        version_specifier="CDN",
                        source="cdn",
                        enabled=True,
                        confidence=1.0,
                    )
                )

        return items
