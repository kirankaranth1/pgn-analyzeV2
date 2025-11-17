"""
Visualize Chess Games - Node Inspector

This script parses and displays detailed information about each node
from chess games, allowing manual verification of the preprocessing 
pipeline output and classification results.

Supported Pre-built Games:
    - capablanca: Capablanca vs Marshall (1918) - 36 moves
    - morphy: Morphy vs Duke Karl/Count Isouard (1858) - 17 moves

Usage:
    python visualize_game.py [GAME or PGN_FILE] [OPTIONS]
    
Arguments:
    GAME or FILE     Pre-built game name ('capablanca', 'morphy') 
                     or path to PGN file (default: capablanca)
    
Options:
    --with-engine    Run full preprocessing with engine analysis (slow)
    --depth N        Engine analysis depth (default: 12)
    --cloud          Use cloud evaluation
    --classify       Show move classifications
    --save FILE      Save output to file
    
Examples:
    python visualize_game.py morphy --with-engine --classify
    python visualize_game.py my_game.pgn --with-engine --depth 16
    python visualize_game.py capablanca --move 15 --classify
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import chess
from src.preprocessing.parser import parse_pgn_game
from src.preprocessing.node_chain_builder import get_node_chain
from src.preprocessing import run_full_preprocessing_pipeline, extract_node_pair
from src.config import EngineConfig
from src.classification import Classifier
from src.models.enums import Classification


# The famous Capablanca vs Marshall game (1918)
CAPABLANCA_MARSHALL_PGN = """
1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.O-O Be7 6.Re1 b5 7.Bb3
O-O 8.c3 d5 9.exd5 Nxd5 10.Nxe5 Nxe5 11.Rxe5 Nf6 12.Re1 Bd6
13.h3 Ng4 14.Qf3 Qh4 15.d4 Nxf2 16.Re2 Bg4 17.hxg4 Bh2+ 18.Kf1
Bg3 19.Rxf2 Qh1+ 20.Ke2 Bxf2 21.Bd2 Bh4 22.Qh3 Rae8+ 23.Kd3
Qf1+ 24.Kc2 Bf2 25.Qf3 Qg1 26.Bd5 c5 27.dxc5 Bxc5 28.b4 Bd6
29.a4 a5 30.axb5 axb4 31.Ra6 bxc3 32.Nxc3 Bb4 33.b6 Bxc3
34.Bxc3 h6 35.b7 Re3 36.Bxf7+
""".strip()

# The famous Opera Game (1858)
MORPHY_OPERA_PGN = """
1.e4 e5 2.Nf3 d6 3.d4 Bg4 4.dxe5 Bxf3 5.Qxf3 dxe5 6.Bc4 Nf6 7.Qb3 Qe7
8.Nc3 c6 9.Bg5 b5 10.Nxb5 cxb5 11.Bxb5+ Nbd7 12.O-O-O Rd8
13.Rxd7 Rxd7 14.Rd1 Qe6 15.Bxd7+ Nxd7 16.Qb8+ Nxb8 17.Rd8#
""".strip()

# Game metadata
GAMES = {
    "capablanca": {
        "pgn": CAPABLANCA_MARSHALL_PGN,
        "title": "CAPABLANCA vs MARSHALL (1918) - NODE VISUALIZATION",
        "event": "New York 1918, Round 1",
        "white": "Jose Raul Capablanca",
        "black": "Frank James Marshall",
        "result": "1-0",
        "eco": "C89 (Ruy Lopez, Marshall Attack)",
        "moves": 36,
        "ply": 71,
    },
    "morphy": {
        "pgn": MORPHY_OPERA_PGN,
        "title": "MORPHY vs DUKE KARL/COUNT ISOUARD (1858) - NODE VISUALIZATION",
        "event": "Paris 1858 (Opera House)",
        "white": "Paul Morphy",
        "black": "Duke Karl / Count Isouard",
        "result": "1-0",
        "eco": "C41 (Philidor Defense)",
        "moves": 17,
        "ply": 33,
    },
}


def format_move_number(move_count: int, color: str) -> str:
    """Format move number with color."""
    full_move = (move_count + 1) // 2
    if color == "WHITE":
        return f"{full_move}."
    else:
        return f"{full_move}..."


def visualize_node(node, node_index: int, show_fen: bool = False, show_engine: bool = True, show_classification: bool = False, classifier=None):
    """Display detailed information about a single node."""
    
    print("=" * 80)
    if node_index == 0:
        print(f"NODE {node_index}: ROOT NODE (Starting Position)")
    else:
        move_num = format_move_number(node_index, node.state.move_color)
        print(f"NODE {node_index}: {move_num} {node.state.move.san} ({node.state.move_color})")
    print("=" * 80)
    
    # Basic node info
    print(f"Node ID:      {node.id[:8]}...")
    print(f"Mainline:     {node.mainline}")
    print(f"Has Parent:   {node.parent is not None}")
    print(f"Children:     {len(node.children)}")
    
    # Move information (skip for root)
    if node.state.move is not None:
        print(f"\nMove Details:")
        print(f"  SAN:        {node.state.move.san}")
        print(f"  UCI:        {node.state.move.uci}")
        print(f"  Color:      {node.state.move_color}")
    
    # Position information
    print(f"\nPosition:")
    if show_fen:
        print(f"  FEN:        {node.state.fen}")
    
    # Create board to show position
    board = chess.Board(node.state.fen)
    print(f"  Turn:       {'White' if board.turn == chess.WHITE else 'Black'}")
    print(f"  Castling:   {board.castling_rights}")
    print(f"  Check:      {board.is_check()}")
    print(f"  Checkmate:  {board.is_checkmate()}")
    print(f"  Legal:      {board.is_valid()}")
    
    # Material count
    white_material = sum([
        len(board.pieces(chess.PAWN, chess.WHITE)),
        len(board.pieces(chess.KNIGHT, chess.WHITE)) * 3,
        len(board.pieces(chess.BISHOP, chess.WHITE)) * 3,
        len(board.pieces(chess.ROOK, chess.WHITE)) * 5,
        len(board.pieces(chess.QUEEN, chess.WHITE)) * 9,
    ])
    black_material = sum([
        len(board.pieces(chess.PAWN, chess.BLACK)),
        len(board.pieces(chess.KNIGHT, chess.BLACK)) * 3,
        len(board.pieces(chess.BISHOP, chess.BLACK)) * 3,
        len(board.pieces(chess.ROOK, chess.BLACK)) * 5,
        len(board.pieces(chess.QUEEN, chess.BLACK)) * 9,
    ])
    print(f"  Material:   White={white_material}, Black={black_material} (Δ{white_material-black_material:+d})")
    
    # Classification with Point Loss
    if show_classification and classifier and node_index > 0:
        print(f"\n🎯 CLASSIFICATION:")
        try:
            result = classifier.classify(node)
            
            # Display classification with details
            classification_str = result.classification.value
            if result.is_missed_opportunity:
                classification_str += " + MISSED OPPORTUNITY"
            print(f"  Classification: {classification_str}")
            
            # Add explanatory notes
            if result.classification == Classification.FORCED:
                print(f"  Reason:         Only 1 legal move available")
            elif result.classification == Classification.BOOK:
                print(f"  Reason:         Position in opening book")
                if node.state.opening:
                    print(f"  Opening:        {node.state.opening}")
            elif result.classification == Classification.BEST:
                board = chess.Board(node.state.fen)
                if board.is_checkmate():
                    print(f"  Reason:         Delivers checkmate")
                else:
                    print(f"  Reason:         Top engine move played")
            elif result.classification == Classification.CRITICAL:
                print(f"  Reason:         Only move preventing significant loss (≥10% point loss)")
            elif result.classification == Classification.BRILLIANT:
                print(f"  Reason:         Sacrifice or risky move with insufficient counter-threats")
            elif result.classification == Classification.EXCELLENT:
                print(f"  Reason:         Very small point loss (< 0.045)")
            elif result.classification == Classification.GOOD:
                print(f"  Reason:         Small point loss (< 0.08)")
            elif result.classification == Classification.INACCURACY:
                print(f"  Reason:         Moderate point loss (< 0.12)")
            elif result.classification == Classification.MISTAKE:
                print(f"  Reason:         Significant point loss (< 0.22)")
            elif result.classification == Classification.BLUNDER:
                print(f"  Reason:         Large point loss (≥ 0.22)")
            
            # Add note for missed opportunity
            if result.is_missed_opportunity:
                print(f"  Note:           Failed to capitalize on opponent's mistake/blunder")
            
            # Show point loss if available and not special classification
            if result.classification not in [Classification.FORCED, Classification.BOOK]:
                pair = extract_node_pair(node)
                if pair:
                    from src.preprocessing.calculator import calculate_move_metrics
                    previous, current = pair
                    try:
                        point_loss, accuracy = calculate_move_metrics(previous, current)
                        print(f"  Point Loss:     {point_loss:.4f}")
                        print(f"  Accuracy:       {accuracy:.1f}%")
                    except:
                        pass
        except ValueError as e:
            print(f"  Classification: N/A")
            print(f"  Note:           {str(e)}")
        except Exception as e:
            print(f"  Classification: Error")
            print(f"  Note:           {str(e)}")
    
    # Engine analysis
    if show_engine and len(node.state.engine_lines) > 0:
        print(f"\nEngine Analysis ({len(node.state.engine_lines)} lines):")
        for i, line in enumerate(node.state.engine_lines[:2], 1):  # Show top 2 lines
            eval_str = f"{line.evaluation.value:+.2f}" if line.evaluation.type == "centipawn" else f"M{line.evaluation.value:+.0f}"
            moves_str = " ".join([m.san for m in line.moves[:5]])  # First 5 moves
            if len(line.moves) > 5:
                moves_str += "..."
            print(f"  Line {i}:     {eval_str} | depth={line.depth} | {moves_str}")
            print(f"              source={line.source}")
    elif show_engine:
        print(f"\nEngine Analysis: Not available")
    
    # Accuracy
    if node.state.accuracy is not None:
        print(f"\nMove Quality:")
        print(f"  Accuracy:   {node.state.accuracy:.1f}%")
    
    # Opening
    if node.state.opening:
        print(f"\nOpening:")
        print(f"  Name:       {node.state.opening}")
    
    # Classification (will be None until classification is implemented)
    if node.state.classification:
        print(f"\nClassification:")
        print(f"  Tags:       {node.state.classification}")
    
    print()


def visualize_extracted_pair(node_index: int, previous, current):
    """Display extracted node pair for classification."""
    print("─" * 80)
    print(f"EXTRACTED PAIR FOR NODE {node_index}")
    print("─" * 80)
    
    print("\n📋 PREVIOUS NODE (before move):")
    print(f"   FEN:              {previous.state.fen}")
    print(f"   Evaluation:       {previous.evaluation.type}={previous.evaluation.value:+.2f}")
    print(f"   Subjective Eval:  {previous.subjective_evaluation.value:+.2f}")
    print(f"   Top Move:         {previous.top_move.uci() if previous.top_move else 'None'}")
    print(f"   Has 2nd Line:     {previous.second_top_line is not None}")
    
    print("\n📋 CURRENT NODE (after move):")
    print(f"   FEN:              {current.state.fen}")
    print(f"   Played Move:      {current.played_move.uci()}")
    print(f"   Evaluation:       {current.evaluation.type}={current.evaluation.value:+.2f}")
    print(f"   Subjective Eval:  {current.subjective_evaluation.value:+.2f}")
    print(f"   Top Move:         {current.top_move.uci() if current.top_move else 'None'}")
    print(f"   Has 2nd Line:     {current.second_top_line is not None}")
    
    # Calculate and display metrics if possible
    from src.preprocessing.calculator import calculate_move_metrics
    try:
        point_loss, accuracy = calculate_move_metrics(previous, current)
        print("\n📊 CALCULATED METRICS:")
        print(f"   Point Loss:       {point_loss:.4f}")
        print(f"   Move Accuracy:    {accuracy:.1f}%")
    except Exception as e:
        print(f"\n⚠️  Could not calculate metrics: {e}")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Visualize historical chess game nodes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s capablanca --move 8              # Show Marshall Attack
  %(prog)s morphy --move 16                  # Show queen sacrifice
  %(prog)s capablanca --with-engine --move 15
  %(prog)s morphy --start 0 --end 10
  %(prog)s morphy --classify --with-engine  # Show classifications with real engine
        """
    )
    parser.add_argument("game", nargs="?", default="capablanca",
                       help="Pre-built game ('capablanca', 'morphy') or path to PGN file")
    parser.add_argument("--with-engine", action="store_true", help="Run with engine analysis")
    parser.add_argument("--depth", type=int, default=12, help="Engine depth (default: 12)")
    parser.add_argument("--cloud", action="store_true", help="Use cloud evaluation")
    parser.add_argument("--show-fen", action="store_true", help="Show full FEN strings")
    parser.add_argument("--show-extracted", action="store_true", help="Show extracted node pairs")
    parser.add_argument("--classify", action="store_true", help="Show move classifications")
    parser.add_argument("--start", type=int, default=0, help="Start from node N")
    parser.add_argument("--end", type=int, help="End at node N")
    parser.add_argument("--move", type=int, help="Show only this move number")
    parser.add_argument("--save", type=str, help="Save output to file")
    
    args = parser.parse_args()
    
    # Determine if input is a pre-built game or a file
    game_key = args.game
    pgn = None
    game_data = None
    
    # Check if it's a pre-built game
    if game_key in GAMES:
        game_data = GAMES[game_key]
        pgn = game_data["pgn"]
    # Check if it's a file path
    elif Path(game_key).exists():
        pgn_file = Path(game_key)
        print(f"📂 Loading PGN from file: {pgn_file}")
        try:
            with open(pgn_file, 'r') as f:
                pgn = f.read().strip()
            
            # Create basic game data from file
            game_data = {
                "pgn": pgn,
                "title": f"GAME FROM {pgn_file.name.upper()}",
                "event": "Custom Game",
                "white": "Unknown",
                "black": "Unknown",
                "result": "*",
                "eco": "Unknown",
                "moves": "?",
                "ply": "?",
            }
            
            # Try to extract metadata from PGN headers
            import re
            white_match = re.search(r'\[White\s+"([^"]+)"\]', pgn)
            black_match = re.search(r'\[Black\s+"([^"]+)"\]', pgn)
            result_match = re.search(r'\[Result\s+"([^"]+)"\]', pgn)
            event_match = re.search(r'\[Event\s+"([^"]+)"\]', pgn)
            eco_match = re.search(r'\[ECO\s+"([^"]+)"\]', pgn)
            
            if white_match:
                game_data["white"] = white_match.group(1)
            if black_match:
                game_data["black"] = black_match.group(1)
            if result_match:
                game_data["result"] = result_match.group(1)
            if event_match:
                game_data["event"] = event_match.group(1)
            if eco_match:
                game_data["eco"] = eco_match.group(1)
                
        except Exception as e:
            print(f"❌ Error loading PGN file: {e}")
            sys.exit(1)
    else:
        print(f"❌ Error: '{game_key}' is not a recognized pre-built game and file does not exist")
        print(f"\nAvailable pre-built games: {', '.join(GAMES.keys())}")
        print(f"Or provide a path to a PGN file")
        sys.exit(1)
    
    # Redirect output to file if requested
    if args.save:
        sys.stdout = open(args.save, 'w')
    
    print("╔" + "═" * 78 + "╗")
    print("║" + game_data["title"].center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    print(f"Event:  {game_data['event']}")
    print(f"White:  {game_data['white']}")
    print(f"Black:  {game_data['black']}")
    print(f"Result: {game_data['result']}")
    if game_data['eco'] != "Unknown":
        print(f"ECO:    {game_data['eco']}")
    print()
    
    # Initialize classifier if needed
    classifier = None
    if args.classify:
        classifier = Classifier()
        print(f"🎯 Classification Enabled (includes Point Loss classification)")
        print()
    
    # Parse game
    if args.with_engine:
        print(f"⏳ Running full preprocessing pipeline (depth={args.depth})...")
        config = EngineConfig(
            depth=args.depth,
            multi_pv=2,
            use_cloud_eval=args.cloud
        )
        try:
            root = run_full_preprocessing_pipeline(pgn, config=config)
            print("✅ Pipeline complete!\n")
        except Exception as e:
            print(f"⚠️  Pipeline failed: {e}")
            print("📝 Falling back to parsing only...\n")
            root = parse_pgn_game(pgn)
    else:
        print("📝 Parsing game (no engine analysis)...\n")
        root = parse_pgn_game(pgn)
    
    # Get all nodes
    nodes = get_node_chain(root)
    print(f"📊 Total nodes: {len(nodes)} (root + {len(nodes)-1} moves)")
    if game_data['ply'] != "?":
        expected_nodes = game_data['ply'] + 1
        if len(nodes) != expected_nodes:
            print(f"⚠️  Warning: Expected {expected_nodes} nodes")
    print()
    
    # Determine range to display
    start_idx = args.start
    end_idx = args.end if args.end is not None else len(nodes)
    
    # Handle --move option
    if args.move is not None:
        # Convert move number to node indices
        start_idx = args.move * 2 - 1  # White's move
        end_idx = args.move * 2 + 1     # Include Black's move
        print(f"🎯 Showing move {args.move} only (nodes {start_idx}-{end_idx})\n")
    
    # Display nodes
    for i in range(start_idx, min(end_idx, len(nodes))):
        visualize_node(
            nodes[i], 
            i, 
            show_fen=args.show_fen, 
            show_engine=args.with_engine,
            show_classification=args.classify,
            classifier=classifier
        )
        
        # Show extracted pair if requested
        if args.show_extracted and i > 0:
            pair = extract_node_pair(nodes[i])
            if pair is not None:
                previous, current = pair
                visualize_extracted_pair(i, previous, current)
        
        # Add separator between nodes
        if i < min(end_idx, len(nodes)) - 1:
            print("\n")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Game: {args.game.capitalize()}")
    print(f"Nodes displayed: {min(end_idx, len(nodes)) - start_idx}")
    print(f"Total moves: {len(nodes) - 1}")
    
    # Count nodes with engine analysis
    if args.with_engine:
        analyzed = sum(1 for n in nodes if len(n.state.engine_lines) > 0)
        print(f"Nodes with engine analysis: {analyzed}/{len(nodes)}")
    
    # Count extractable pairs
    extractable = sum(1 for i in range(1, len(nodes)) if extract_node_pair(nodes[i]) is not None)
    print(f"Extractable move pairs: {extractable}/{len(nodes)-1}")
    
    # Classification summary
    if args.classify and classifier:
        print(f"\n🎯 CLASSIFICATION SUMMARY:")
        classifications = {
            "FORCED": 0, 
            "THEORY": 0, 
            "BEST": 0, 
            "CRITICAL": 0,
            "BRILLIANT": 0,
            "EXCELLENT": 0,
            "GOOD": 0,
            "INACCURACY": 0,
            "MISTAKE": 0,
            "BLUNDER": 0,
            "N/A": 0
        }
        missed_opportunities = 0
        
        for i in range(1, len(nodes)):
            try:
                result = classifier.classify(nodes[i])
                
                if result.classification == Classification.FORCED:
                    classifications["FORCED"] += 1
                elif result.classification == Classification.BOOK:
                    classifications["THEORY"] += 1
                elif result.classification == Classification.BEST:
                    classifications["BEST"] += 1
                elif result.classification == Classification.CRITICAL:
                    classifications["CRITICAL"] += 1
                elif result.classification == Classification.BRILLIANT:
                    classifications["BRILLIANT"] += 1
                elif result.classification == Classification.EXCELLENT:
                    classifications["EXCELLENT"] += 1
                elif result.classification == Classification.GOOD:
                    classifications["GOOD"] += 1
                elif result.classification == Classification.INACCURACY:
                    classifications["INACCURACY"] += 1
                elif result.classification == Classification.MISTAKE:
                    classifications["MISTAKE"] += 1
                elif result.classification == Classification.BLUNDER:
                    classifications["BLUNDER"] += 1
                
                if result.is_missed_opportunity:
                    missed_opportunities += 1
            except:
                classifications["N/A"] += 1
        
        print(f"  FORCED (only 1 legal move):        {classifications['FORCED']}")
        print(f"  THEORY (in opening book):           {classifications['THEORY']}")
        print(f"  BEST (top move or checkmate):       {classifications['BEST']}")
        print(f"  CRITICAL (prevents major loss):     {classifications['CRITICAL']}")
        print(f"  BRILLIANT (sacrifice/risky):        {classifications['BRILLIANT']}")
        print(f"  EXCELLENT (point loss < 0.045):     {classifications['EXCELLENT']}")
        print(f"  GOOD (point loss < 0.08):           {classifications['GOOD']}")
        print(f"  INACCURACY (point loss < 0.12):     {classifications['INACCURACY']}")
        print(f"  MISTAKE (point loss < 0.22):        {classifications['MISTAKE']}")
        print(f"  BLUNDER (point loss ≥ 0.22):        {classifications['BLUNDER']}")
        print(f"  N/A (extraction failed):            {classifications['N/A']}")
        print()
        print(f"  🚨 MISSED OPPORTUNITIES:              {missed_opportunities}")
    
    print("\n✅ Visualization complete!")
    
    if args.save:
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        print(f"Output saved to: {args.save}")


if __name__ == "__main__":
    main()

