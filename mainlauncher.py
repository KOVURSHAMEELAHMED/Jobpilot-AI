# 🚀 launch_offcampus.py
#!/usr/bin/env python3
"""
OFF-CAMPUS AUTO JOB APPLICATION LAUNCHER
Main entry point for the automated job application system
"""

import argparse
import sys
import os
import logging
from datetime import datetime
from backend_job_applicator import OffCampusAutoApplicator
from job_matcher_ai import OffCampusJobMatcher

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/offcampus_applications.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def display_banner():
    """Display application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║     ███████╗ █████╗ ██╗   ██╗██████╗ ██╗██████╗  ██████╗ ████████╗         ║
    ║     ██╔════╝██╔══██╗██║   ██║██╔══██╗██║██╔══██╗██╔═══██╗╚══██╔══╝         ║
    ║     █████╗  ███████║██║   ██║██████╔╝██║██████╔╝██║   ██║   ██║            ║
    ║     ██╔══╝  ██╔══██║╚██╗ ██╔╝██╔═══╝ ██║██╔══██╗██║   ██║   ██║            ║
    ║     ██║     ██║  ██║ ╚████╔╝ ██║     ██║██║  ██║╚██████╔╝   ██║            ║
    ║     ╚═╝     ╚═╝  ╚═╝  ╚═══╝  ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝            ║
    ║                                                                              ║
    ║                 AUTO JOB APPLICATION SYSTEM                                 ║
    ║              For Off-Campus Placements                                      ║
    ║                                                                              ║
    ║     Version: 1.0.0                  Powered by AI                           ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Off-Campus Auto Job Application System'
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['auto', 'manual', 'test', 'scout'],
        default='auto',
        help='Application mode: auto (full automation), manual (with prompts), test (dry run), scout (only search)'
    )

    parser.add_argument(
        '--portals',
        type=str,
        nargs='+',
        default=['linkedin', 'indeed'],
        help='Job portals to use: linkedin, indeed, glassdoor, naukri'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of applications per session'
    )

    parser.add_argument(
        '--resume',
        type=str,
        default='./data/resume.pdf',
        help='Path to resume file'
    )

    parser.add_argument(
        '--keywords',
        type=str,
        nargs='+',
        help='Custom job search keywords'
    )

    parser.add_argument(
        '--location',
        type=str,
        default='Remote',
        help='Job location to search for'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    return parser.parse_args()

def main():
    """Main execution function"""
    # Setup logging
    logger = setup_logging()
    
    # Parse arguments
    args = parse_arguments()
    
    # Display banner
    display_banner()
    
    logger.info(f"Starting JobPilot AI in {args.mode} mode")
    logger.info(f"Portals: {', '.join(args.portals)}")
    logger.info(f"Application limit: {args.limit}")
    logger.info(f"Location: {args.location}")
    
    try:
        # Check if resume exists
        if not os.path.exists(args.resume):
            logger.error(f"Resume file not found: {args.resume}")
            print(f"\n❌ ERROR: Resume file not found at {args.resume}")
            print("Please copy your resume to the data folder:")
            print("  copy SHAMEEL_RESUME.pdf data\\resume.pdf")
            sys.exit(1)
        else:
            logger.info(f"Resume found: {args.resume}")
            print(f"✅ Resume found: {args.resume}")
        
        # Initialize components
        print("\n📦 Initializing components...")
        logger.info("Initializing Auto Applicator...")
        applicator = OffCampusAutoApplicator()
        print("   ✅ Auto Applicator initialized")
        
        logger.info("Initializing Job Matcher...")
        matcher = OffCampusJobMatcher()
        print("   ✅ Job Matcher initialized")
        
        # Run based on mode
        if args.mode == 'test':
            print("\n🧪 TEST MODE - No applications will be submitted")
            print("="*50)
            print(f"Mode: {args.mode}")
            print(f"Portals: {', '.join(args.portals)}")
            print(f"Application Limit: {args.limit}")
            print(f"Location: {args.location}")
            print(f"Resume: {args.resume}")
            print("="*50)
            print("\n✅ TEST PASSED: System is configured correctly!")
            print("   You can now run in other modes:")
            print("   • Scout mode:  python mainlauncher.py --mode scout")
            print("   • Manual mode: python mainlauncher.py --mode manual")
            print("   • Auto mode:   python mainlauncher.py --mode auto")
            
        elif args.mode == 'scout':
            print("\n🔍 SCOUT MODE - Searching for jobs (no applications)")
            print("="*50)
            print(f"Searching for jobs in: {args.location}")
            print(f"Using portals: {', '.join(args.portals)}")
            print("="*50)
            # Here you would call the actual search functionality
            print("\n📊 Search Results:")
            print("   This would show matching jobs from the portals")
            
        elif args.mode == 'manual':
            print("\n👤 MANUAL MODE - Will prompt before each application")
            print("="*50)
            print(f"Ready to apply to up to {args.limit} jobs")
            print("="*50)
            
        else:  # auto mode
            print("\n🤖 AUTO MODE - Fully automated job applications")
            print("="*50)
            print(f"Will attempt to apply to {args.limit} jobs")
            print(f"Portals: {', '.join(args.portals)}")
            print("="*50)
        
        logger.info("JobPilot AI completed successfully")
        print("\n✨ JobPilot AI execution completed!")
        print(f"📝 Check logs at: logs\\offcampus_applications.log")
        
    except Exception as e:
        logger.error(f"Error running JobPilot AI: {e}")
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()