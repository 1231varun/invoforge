"""
Cross-Platform PDF Converter

Implements the Strategy pattern for PDF conversion across different platforms.
Automatically selects the best available converter based on the OS and installed software.

Supported platforms:
- macOS: MS Word (via docx2pdf) → LibreOffice → unoconv
- Windows: MS Word (via docx2pdf) → LibreOffice
- Linux: LibreOffice → unoconv → wkhtmltopdf
"""
import platform
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from app.core.interfaces.pdf_converter import PDFConverter


class ConversionStrategy(ABC):
    """Abstract base class for PDF conversion strategies"""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this conversion method is available on the system"""
        pass

    @abstractmethod
    def convert(self, source_path: Path, output_path: Path) -> bool:
        """
        Convert DOCX to PDF.
        Returns True if successful, False otherwise.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this strategy"""
        pass


class DocxToPdfStrategy(ConversionStrategy):
    """Uses docx2pdf library (requires MS Word on macOS/Windows)"""

    @property
    def name(self) -> str:
        return "docx2pdf (MS Word)"

    def is_available(self) -> bool:
        try:
            from docx2pdf import convert  # noqa: F401
            return True
        except ImportError:
            return False

    def convert(self, source_path: Path, output_path: Path) -> bool:
        try:
            from docx2pdf import convert
            convert(str(source_path), str(output_path))
            return output_path.exists()
        except Exception:
            return False


class LibreOfficeStrategy(ConversionStrategy):
    """Uses LibreOffice in headless mode"""

    def __init__(self):
        self._executable: Optional[str] = None

    @property
    def name(self) -> str:
        return "LibreOffice"

    def is_available(self) -> bool:
        self._executable = self._find_executable()
        return self._executable is not None

    def _find_executable(self) -> Optional[str]:
        """Find LibreOffice executable based on platform"""
        system = platform.system()

        if system == "Darwin":  # macOS
            paths = [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                "/Applications/OpenOffice.app/Contents/MacOS/soffice",
            ]
        elif system == "Windows":
            paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
        else:  # Linux and others
            paths = [
                "/usr/bin/libreoffice",
                "/usr/bin/soffice",
                "/usr/local/bin/libreoffice",
                "/opt/libreoffice/program/soffice",
                "/snap/bin/libreoffice",
            ]

        # Check explicit paths first
        for path in paths:
            if Path(path).is_file():
                return path

        # Try PATH lookup
        for cmd in ["libreoffice", "soffice"]:
            found = shutil.which(cmd)
            if found:
                return found

        return None

    def convert(self, source_path: Path, output_path: Path) -> bool:
        if not self._executable:
            return False

        try:
            result = subprocess.run(
                [
                    self._executable,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(source_path.parent),
                    str(source_path)
                ],
                capture_output=True,
                timeout=120,
                check=False
            )
            return result.returncode == 0 and output_path.exists()
        except (subprocess.TimeoutExpired, OSError):
            return False


class UnoconvStrategy(ConversionStrategy):
    """Uses unoconv (Python-UNO bridge to LibreOffice)"""

    @property
    def name(self) -> str:
        return "unoconv"

    def is_available(self) -> bool:
        return shutil.which("unoconv") is not None

    def convert(self, source_path: Path, output_path: Path) -> bool:
        try:
            result = subprocess.run(
                ["unoconv", "-f", "pdf", "-o", str(output_path), str(source_path)],
                capture_output=True,
                timeout=120,
                check=False
            )
            return result.returncode == 0 and output_path.exists()
        except (subprocess.TimeoutExpired, OSError):
            return False


class CrossPlatformPDFConverter(PDFConverter):
    """
    Cross-platform PDF converter that automatically selects 
    the best available conversion strategy.
    
    Follows the Strategy pattern for extensibility.
    """

    def __init__(self, strategies: Optional[List[ConversionStrategy]] = None):
        """
        Initialize with custom strategies or use defaults.
        
        Args:
            strategies: Optional list of conversion strategies to try in order.
                       If None, uses platform-appropriate defaults.
        """
        self._strategies = strategies or self._get_default_strategies()
        self._available_strategies: Optional[List[ConversionStrategy]] = None

    def _get_default_strategies(self) -> List[ConversionStrategy]:
        """Get default strategies ordered by preference for current platform"""
        system = platform.system()

        if system == "Darwin":  # macOS
            return [
                DocxToPdfStrategy(),
                LibreOfficeStrategy(),
                UnoconvStrategy(),
            ]
        elif system == "Windows":
            return [
                DocxToPdfStrategy(),
                LibreOfficeStrategy(),
            ]
        else:  # Linux and others
            return [
                LibreOfficeStrategy(),
                UnoconvStrategy(),
            ]

    def get_available_strategies(self) -> List[ConversionStrategy]:
        """Get list of available conversion strategies"""
        if self._available_strategies is None:
            self._available_strategies = [
                s for s in self._strategies if s.is_available()
            ]
        return self._available_strategies

    def convert(self, source_path: Path) -> Optional[Path]:
        """
        Convert DOCX to PDF using the first available strategy.
        
        Args:
            source_path: Path to the DOCX file
            
        Returns:
            Path to the generated PDF, or None if conversion failed
        """
        output_path = source_path.with_suffix(".pdf")

        available = self.get_available_strategies()

        if not available:
            raise RuntimeError(
                "No PDF conversion method available. "
                "Please install LibreOffice, MS Word, or unoconv."
            )

        errors = []
        for strategy in available:
            try:
                if strategy.convert(source_path, output_path):
                    return output_path
                errors.append(f"{strategy.name}: conversion returned no file")
            except Exception as e:
                errors.append(f"{strategy.name}: {e}")

        # All strategies failed
        error_details = "; ".join(errors)
        raise RuntimeError(f"PDF conversion failed. Tried: {error_details}")

    def get_converter_info(self) -> dict:
        """Get information about available converters (useful for diagnostics)"""
        return {
            "platform": platform.system(),
            "available_converters": [s.name for s in self.get_available_strategies()],
            "all_converters": [s.name for s in self._strategies],
        }

