import sys
import logging

# Auto-detect and apply Pi optimizations if running on Raspberry Pi
try:
    from .config_pi import is_raspberry_pi, check_pi_temperature
    if is_raspberry_pi():
        print("🍓 Raspberry Pi detected - optimizations applied")
        # Temperature check on startup
        check_pi_temperature()
except ImportError:
    pass  # Pi config not available

def main():
    """Main entry point for Evil Assistant"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🔥 Starting Evil Assistant")
    
    try:
        from .assistant_clean import run_clean_assistant
        import asyncio
        asyncio.run(run_clean_assistant())
    except ImportError as e:
        logger.error(f"Assistant components not available: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🔥 Evil Assistant shutting down...")

if __name__ == "__main__":
    main()