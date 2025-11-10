#!/usr/bin/env python3
"""Chess Move Classifier - Main entry point."""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.analyzer import GameAnalyzer
from src.engine.engine_config import EngineConfig
from src.classification.classifier import AnalysisOptions
from src.output.json_reporter import JSONReporter


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze chess games and classify moves",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a PGN file with default settings
  python main.py --pgn game.pgn --stockfish /usr/local/bin/stockfish --output analysis.json
  
  # Analyze with custom depth
  python main.py --pgn game.pgn --stockfish stockfish --output analysis.json --depth 25
  
  # Disable BRILLIANT classification for faster analysis
  python main.py --pgn game.pgn --stockfish stockfish --output analysis.json --no-brilliant
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--pgn",
        required=True,
        help="Path to PGN file to analyze"
    )
    
    parser.add_argument(
        "--stockfish",
        required=True,
        help="Path to Stockfish binary"
    )
    
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path"
    )
    
    # Engine configuration
    parser.add_argument(
        "--depth",
        type=int,
        default=20,
        help="Search depth in plies (default: 20)"
    )
    
    parser.add_argument(
        "--multipv",
        type=int,
        default=2,
        help="Number of principal variations (default: 2)"
    )
    
    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of CPU threads (default: 1)"
    )
    
    parser.add_argument(
        "--hash",
        type=int,
        default=128,
        help="Hash table size in MB (default: 128)"
    )
    
    # Classification options
    parser.add_argument(
        "--no-theory",
        action="store_true",
        help="Disable THEORY classification"
    )
    
    parser.add_argument(
        "--no-critical",
        action="store_true",
        help="Disable CRITICAL classification"
    )
    
    parser.add_argument(
        "--no-brilliant",
        action="store_true",
        help="Disable BRILLIANT classification (faster)"
    )
    
    # Opening book
    parser.add_argument(
        "--openings",
        default="openings.json",
        help="Path to openings.json (default: openings.json)"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.pgn):
        print(f"Error: PGN file not found: {args.pgn}")
        sys.exit(1)
    
    if not os.path.exists(args.stockfish):
        print(f"Error: Stockfish binary not found: {args.stockfish}")
        sys.exit(1)
    
    openings_path = os.path.join(os.path.dirname(__file__), args.openings)
    if not os.path.exists(openings_path):
        print(f"Warning: Openings file not found: {openings_path}")
        print("THEORY classification will not be available.")
    
    # Create engine config
    engine_config = EngineConfig(
        stockfish_path=args.stockfish,
        depth=args.depth,
        multi_pv=args.multipv,
        threads=args.threads,
        hash_size=args.hash
    )
    
    # Create analysis options
    analysis_options = AnalysisOptions(
        include_theory=not args.no_theory,
        include_critical=not args.no_critical,
        include_brilliant=not args.no_brilliant
    )
    
    print("=" * 60)
    print("Chess Move Classifier")
    print("=" * 60)
    print(f"PGN File: {args.pgn}")
    print(f"Stockfish: {args.stockfish}")
    print(f"Depth: {args.depth}")
    print(f"Multi-PV: {args.multipv}")
    print(f"THEORY: {'Enabled' if analysis_options.include_theory else 'Disabled'}")
    print(f"CRITICAL: {'Enabled' if analysis_options.include_critical else 'Disabled'}")
    print(f"BRILLIANT: {'Enabled' if analysis_options.include_brilliant else 'Disabled'}")
    print("=" * 60)
    print()
    
    try:
        # Create analyzer
        analyzer = GameAnalyzer(
            engine_config=engine_config,
            openings_file=openings_path,
            analysis_options=analysis_options
        )
        
        # Analyze game
        result = analyzer.analyze_pgn_file(args.pgn)
        
        if not result:
            print("Error: Failed to analyze game")
            sys.exit(1)
        
        # Generate report
        print("\nGenerating report...")
        report = JSONReporter.generate_report(
            headers=result["headers"],
            root=result["root"]
        )
        
        # Save report
        JSONReporter.save_report(report, args.output)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Analysis Summary")
        print("=" * 60)
        
        white_stats = report["statistics"]["white"]
        black_stats = report["statistics"]["black"]
        
        print(f"\nWhite: {report['game_info']['white']}")
        print(f"  Average Accuracy: {white_stats['average_accuracy']}%")
        print(f"  Brilliant: {white_stats['brilliant']}")
        print(f"  Critical: {white_stats['critical']}")
        print(f"  Best: {white_stats['best']}")
        print(f"  Excellent: {white_stats['excellent']}")
        print(f"  Okay: {white_stats['okay']}")
        print(f"  Inaccuracy: {white_stats['inaccuracy']}")
        print(f"  Mistake: {white_stats['mistake']}")
        print(f"  Blunder: {white_stats['blunder']}")
        
        print(f"\nBlack: {report['game_info']['black']}")
        print(f"  Average Accuracy: {black_stats['average_accuracy']}%")
        print(f"  Brilliant: {black_stats['brilliant']}")
        print(f"  Critical: {black_stats['critical']}")
        print(f"  Best: {black_stats['best']}")
        print(f"  Excellent: {black_stats['excellent']}")
        print(f"  Okay: {black_stats['okay']}")
        print(f"  Inaccuracy: {black_stats['inaccuracy']}")
        print(f"  Mistake: {black_stats['mistake']}")
        print(f"  Blunder: {black_stats['blunder']}")
        
        print("\n" + "=" * 60)
        print("Analysis complete!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

