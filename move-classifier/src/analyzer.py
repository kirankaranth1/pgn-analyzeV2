"""Main game analyzer pipeline."""

import chess.pgn
from typing import Dict, Optional
from .core.state_tree import StateTreeNode
from .engine.stockfish_engine import StockfishEngine
from .engine.engine_config import EngineConfig
from .parser.pgn_parser import PGNParser
from .parser.state_tree_builder import StateTreeBuilder
from .classification.classifier import MoveClassifier, AnalysisOptions
from .utils.opening_book import OpeningBook


class GameAnalyzer:
    """Analyzes chess games with move classification."""
    
    def __init__(
        self,
        engine_config: EngineConfig,
        openings_file: str,
        analysis_options: Optional[AnalysisOptions] = None
    ):
        """Initialize game analyzer.
        
        Args:
            engine_config: Stockfish configuration
            openings_file: Path to openings.json
            analysis_options: Classification options
        """
        self.engine_config = engine_config
        self.opening_book = OpeningBook(openings_file)
        self.analysis_options = analysis_options or AnalysisOptions()
    
    def analyze_pgn_file(self, pgn_file: str) -> Optional[Dict]:
        """Analyze a PGN file.
        
        Args:
            pgn_file: Path to PGN file
            
        Returns:
            Analysis result dictionary
        """
        # Parse PGN
        game = PGNParser.parse_file(pgn_file)
        if not game:
            print(f"Failed to parse PGN file: {pgn_file}")
            return None
        
        return self.analyze_game(game)
    
    def analyze_pgn_string(self, pgn_content: str) -> Optional[Dict]:
        """Analyze a PGN string.
        
        Args:
            pgn_content: PGN content as string
            
        Returns:
            Analysis result dictionary
        """
        # Parse PGN
        game = PGNParser.parse_game(pgn_content)
        if not game:
            print("Failed to parse PGN content")
            return None
        
        return self.analyze_game(game)
    
    def analyze_game(self, game: chess.pgn.Game) -> Dict:
        """Analyze a chess game.
        
        Args:
            game: chess.pgn.Game object
            
        Returns:
            Analysis result dictionary
        """
        print("Building state tree...")
        # Build state tree
        root = StateTreeBuilder.build_tree(game)
        
        # Extract game headers
        headers = PGNParser.extract_headers(game)
        
        print("Starting engine analysis...")
        # Analyze with engine
        with StockfishEngine(self.engine_config) as engine:
            self._analyze_positions(root, engine)
        
        print("Classifying moves...")
        # Classify moves
        classifier = MoveClassifier(self.opening_book, self.analysis_options)
        self._classify_moves(root, classifier)
        
        print("Analysis complete!")
        
        # Return results
        return {
            "headers": headers,
            "root": root
        }
    
    def _analyze_positions(self, root: StateTreeNode, engine: StockfishEngine) -> None:
        """Analyze all positions in the game tree.
        
        Args:
            root: Root state tree node
            engine: Stockfish engine
        """
        # Get all mainline nodes
        nodes = root.traverse_mainline()
        
        for i, node in enumerate(nodes):
            # Show progress
            if i % 5 == 0:
                print(f"  Analyzing position {i + 1}/{len(nodes)}...")
            
            # Skip terminal positions (checkmate, stalemate)
            import chess
            board = chess.Board(node.state.fen)
            if board.is_game_over():
                node.state.engine_lines = []
                continue
            
            # Analyze position
            fen = node.state.fen
            engine_lines = engine.analyze_position(fen)
            node.state.engine_lines = engine_lines
    
    def _classify_moves(self, root: StateTreeNode, classifier: MoveClassifier) -> None:
        """Classify all moves in the game tree.
        
        Args:
            root: Root state tree node
            classifier: Move classifier
        """
        # Get all mainline nodes (skip root since it has no move)
        nodes = root.traverse_mainline()[1:]
        
        for node in nodes:
            # Classify move
            classification, accuracy, opening = classifier.classify_move(node)
            
            # Store results
            node.state.classification = classification
            node.state.accuracy = accuracy
            if opening:
                node.state.opening = opening

