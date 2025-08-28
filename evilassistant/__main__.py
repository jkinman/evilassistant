import sys
import asyncio
import logging

def main():
    """Main entry point with fallback support"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Check for mode
    if "--vad" in sys.argv:
        if "--clean" in sys.argv:
            logger.info("🔥 Starting Clean Refactored Evil Assistant")
            try:
                from .assistant_clean import run_clean_assistant
                run_clean_assistant()
            except ImportError as e:
                logger.error(f"Clean assistant components not available: {e}")
                sys.exit(1)
            except KeyboardInterrupt:
                print("Stopped")
        else:
            logger.info("🔥 Starting VAD-powered Evil Assistant with speech-based chunking")
            try:
                from .assistant_vad import run_vad_assistant
                run_vad_assistant()
            except ImportError as e:
                logger.error(f"VAD components not available: {e}")
                logger.info("Install webrtcvad: pip install webrtcvad")
                sys.exit(1)
            except KeyboardInterrupt:
                print("Stopped")
    else:
        logger.info("🔥 Starting Evil Assistant (default: clean version)")
        try:
            from .assistant_clean import run_clean_assistant
            run_clean_assistant()
        except KeyboardInterrupt:
            print("Stopped")

if __name__ == "__main__":
    main()
