# handlers/pdf_handler.py

from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def register():
    try:
        from WrapCapPDF.pdf_extractor import CapPDFHandler
        logger.info("✅ WrapCapPDF loaded successfully.")
    except ImportError as e:
        logger.warning(f"❌ WrapCapPDF not found: {e}")
        return {}
    except Exception as e:
        logger.warning(f"❌ Failed to load CapPDFHandler: {e}")
        return {}

    def handler(path: Path) -> str:
        logger.info(f"📄 Using CapPDFHandler on: {path}")
        cap = CapPDFHandler(str(path))
        return cap.extract_text_content() or f"[No text extracted from {path.name}]"

    return {".pdf": handler}
