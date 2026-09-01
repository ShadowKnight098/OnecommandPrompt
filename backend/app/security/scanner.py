"""Scans extracted project files for security risks, secrets, and suspicious malware patterns."""
import ast
from pathlib import Path
from typing import List, Tuple
import re
from app.models.project import SecurityWarning
from app.security.limits import SecurityLimits


class MalwareASTVisitor(ast.NodeVisitor):
    """Inspects Python Abstract Syntax Trees for potentially dangerous or malicious operations."""

    def __init__(self, rel_path: str):
        self.rel_path = rel_path
        self.findings: List[Tuple[str, str]] = []  # (severity, message)

    def visit_Call(self, node: ast.Call):
        func_name = ""
        module_name = ""

        # Extract function call name
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id

        full_call = f"{module_name}.{func_name}" if module_name else func_name

        # 1. Obfuscated / dynamic execution
        if func_name in {"exec", "eval"}:
            # Check if executing decoded/decompressed data
            is_obfuscated = False
            for arg in node.args:
                if isinstance(arg, ast.Call):
                    inner_name = ""
                    if isinstance(arg.func, ast.Name):
                        inner_name = arg.func.id
                    elif isinstance(arg.func, ast.Attribute):
                        inner_name = arg.func.attr
                    if inner_name in {"b64decode", "b85decode", "b32decode", "decompress", "decode"}:
                        is_obfuscated = True
                        break

            if is_obfuscated:
                self.findings.append((
                    "critical",
                    f"Obfuscated dynamic payload execution ({func_name} + decode) detected in '{self.rel_path}' at line {node.lineno}."
                ))
            else:
                self.findings.append((
                    "warning",
                    f"Dynamic code evaluation '{func_name}()' detected in '{self.rel_path}' at line {node.lineno}."
                ))

        # 2. Arbitrary shell / system command execution
        if full_call in {"os.system", "os.popen", "os.popen2", "os.popen3", "os.popen4"}:
            self.findings.append((
                "warning",
                f"Direct system shell execution '{full_call}()' detected in '{self.rel_path}' at line {node.lineno}."
            ))

        if module_name == "subprocess" or func_name in {"Popen", "run", "call", "check_output", "check_call"}:
            # Check if shell=True is passed
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.findings.append((
                        "warning",
                        f"Subprocess invoked with shell=True in '{self.rel_path}' at line {node.lineno}."
                    ))

        # 3. Network sockets / Reverse shell patterns
        if full_call in {"socket.connect", "socket.connect_ex"}:
            self.findings.append((
                "warning",
                f"Outbound raw socket connection '{full_call}()' detected in '{self.rel_path}' at line {node.lineno}."
            ))

        if full_call in {"pty.spawn", "posix_spawn"}:
            self.findings.append((
                "critical",
                f"Terminal PTY spawn '{full_call}()' (potential reverse shell) detected in '{self.rel_path}' at line {node.lineno}."
            ))

        # 4. Untrusted deserialization
        if full_call in {"pickle.loads", "pickle.load", "_pickle.loads", "_pickle.load"}:
            self.findings.append((
                "warning",
                f"Untrusted object deserialization '{full_call}()' detected in '{self.rel_path}' at line {node.lineno}."
            ))

        self.generic_visit(node)


class ProjectScanner:
    """Inspects project files for security considerations without executing untrusted code."""

    SENSITIVE_FILENAMES = {
        ".env",
        ".env.local",
        ".env.production",
        "id_rsa",
        "id_ed25519",
        "id_dsa",
        ".npmrc",
        ".pypirc",
        "credentials.json",
        "service_account.json",
        "auth.json",
    }

    SECRET_PATTERNS = [
        (re.compile(r"""(?i)(?:api_key|apikey|secret_key|app_secret|auth_token)\s*=\s*['"][a-zA-Z0-9_\-]{16,}['"]"""), "Hardcoded API Key / Secret detected in code"),
        (re.compile(r"""(?i)-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"""), "Private Key content detected in project"),
        (re.compile(r"""(?i)ghp_[a-zA-Z0-9]{36}"""), "GitHub Personal Access Token detected"),
        (re.compile(r"""(?i)sk_live_[a-zA-Z0-9]{24}"""), "Stripe Live Secret Key detected"),
        (re.compile(r"""(?i)AKIA[0-9A-Z]{16}"""), "AWS Access Key ID detected"),
    ]

    SUSPICIOUS_SHELL_STRINGS = [
        (re.compile(r"""/bin/(?:sh|bash)\s+-i"""), "critical", "Interactive reverse shell signature detected"),
        (re.compile(r"""rm\s+-rf\s+[/~]"""), "critical", "Destructive recursive filesystem deletion command detected"),
        (re.compile(r"""(?:curl|wget)\s+https?://[^\s]+\s*\|\s*(?:ba)?sh"""), "critical", "Piped remote script download and execution detected"),
    ]

    @classmethod
    def scan_project(cls, project_root: Path) -> List[SecurityWarning]:
        warnings: List[SecurityWarning] = []

        for path in project_root.rglob("*"):
            if not path.is_file():
                continue

            # Check if inside ignored directories
            if any(part in SecurityLimits.IGNORED_DIRS for part in path.parts):
                continue

            rel_path = path.relative_to(project_root).as_posix()

            # 1. Check for sensitive files (.env, keys)
            if path.name.lower() in cls.SENSITIVE_FILENAMES:
                warnings.append(
                    SecurityWarning(
                        severity="warning",
                        message=f"Sensitive configuration or credentials file detected: '{rel_path}'. Ensure secrets are not published.",
                        file_path=rel_path,
                    )
                )

            # 2. Check for binary / executable extensions
            if path.suffix.lower() in SecurityLimits.FORBIDDEN_EXTENSIONS:
                warnings.append(
                    SecurityWarning(
                        severity="warning",
                        message=f"Executable or binary file detected: '{rel_path}'.",
                        file_path=rel_path,
                    )
                )

            # 3. Check text / code files (< 1MB)
            if path.suffix.lower() in {".py", ".json", ".yaml", ".yml", ".toml", ".txt", ".env"} and path.stat().st_size < 1_000_000:
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")

                    # A. Secret Patterns
                    for pattern, msg in cls.SECRET_PATTERNS:
                        if pattern.search(content):
                            warnings.append(
                                SecurityWarning(
                                    severity="warning",
                                    message=f"{msg} in '{rel_path}'.",
                                    file_path=rel_path,
                                )
                            )
                            break

                    # B. Suspicious Shell Signatures
                    for pattern, sev, msg in cls.SUSPICIOUS_SHELL_STRINGS:
                        if pattern.search(content):
                            warnings.append(
                                SecurityWarning(
                                    severity=sev,
                                    message=f"{msg} in '{rel_path}'.",
                                    file_path=rel_path,
                                )
                            )
                            break

                    # C. Static AST Python Code Inspection
                    if path.suffix.lower() == ".py":
                        try:
                            tree = ast.parse(content, filename=rel_path)
                            visitor = MalwareASTVisitor(rel_path)
                            visitor.visit(tree)
                            for sev, msg in visitor.findings:
                                warnings.append(
                                    SecurityWarning(
                                        severity=sev,
                                        message=msg,
                                        file_path=rel_path,
                                    )
                                )
                        except Exception:
                            # AST parsing failure handled gracefully
                            pass

                except Exception:
                    pass

        return warnings

