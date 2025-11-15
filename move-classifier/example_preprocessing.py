"""
Example: Using the Preprocessing Pipeline

This demonstrates how to use the complete 5-stage preprocessing pipeline
to analyze a chess game and prepare it for classification.
"""

from src.preprocessing import run_full_preprocessing_pipeline
from src.config import EngineConfig
from src.preprocessing.node_chain_builder import get_node_chain


def main():
    """
    Example usage of the preprocessing pipeline.
    """
    # Example PGN game (Scholar's Mate)
    pgn = "1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7#"
    
    print("Chess Move Classifier - Preprocessing Pipeline Demo")
    print("=" * 60)
    print(f"\nAnalyzing game: {pgn}\n")
    
    # Configure engine (using defaults: depth=16, multi_pv=2)
    config = EngineConfig(
        depth=16,
        multi_pv=2,
        use_cloud_eval=True  # Try Lichess cloud first
    )
    
    print("Configuration:")
    print(f"  - Depth: {config.depth}")
    print(f"  - MultiPV: {config.multi_pv}")
    print(f"  - Cloud Eval: {config.use_cloud_eval}")
    print()
    
    # Run the complete preprocessing pipeline
    print("Running preprocessing pipeline...")
    print("  Stage 1: Parsing PGN to State Tree...")
    print("  Stage 2: Analyzing with engine...")
    print("  Stage 3: Building node chain...")
    print("  Stage 4: Extracting nodes...")
    print("  Stage 5: Calculating derived values...")
    print()
    
    try:
        root_node = run_full_preprocessing_pipeline(pgn, config=config)
        
        # Get all nodes
        nodes = get_node_chain(root_node, expand_all_variations=False)
        
        print(f"✓ Preprocessing complete!")
        print(f"  - Total positions: {len(nodes)}")
        print()
        
        # Display results for each move
        print("Move Analysis:")
        print("-" * 60)
        
        for i, node in enumerate(nodes):
            if i == 0:
                # Skip root
                continue
            
            if node.state.move:
                move_num = (i + 1) // 2
                color = "White" if node.state.move_color == "WHITE" else "Black"
                
                print(f"\nMove {move_num}. {node.state.move.san} ({color})")
                
                if node.state.engine_lines:
                    top_line = node.state.engine_lines[0]
                    eval_str = f"+{top_line.evaluation.value:.0f}" if top_line.evaluation.value >= 0 else f"{top_line.evaluation.value:.0f}"
                    
                    if top_line.evaluation.type == "mate":
                        eval_str = f"M{int(top_line.evaluation.value)}"
                    
                    print(f"  Evaluation: {eval_str} cp")
                    print(f"  Engine: {top_line.source} (depth {top_line.depth})")
                    
                    if top_line.moves:
                        best_moves = " ".join([m.san for m in top_line.moves[:3]])
                        print(f"  Best line: {best_moves}...")
                
                if node.state.accuracy is not None:
                    print(f"  Accuracy: {node.state.accuracy:.1f}%")
        
        print("\n" + "=" * 60)
        print("Pipeline complete! Data is ready for classification.")
        print("\nNext step: Use classification module to classify moves")
        
    except FileNotFoundError as e:
        print(f"\n⚠️  Error: {e}")
        print("\nNote: Local Stockfish engine is required if cloud evaluation fails.")
        print("Install Stockfish: https://stockfishchess.org/download/")
    except Exception as e:
        print(f"\n⚠️  Error during preprocessing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

