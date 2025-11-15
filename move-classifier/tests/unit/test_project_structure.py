"""
Unit Test: Project Structure Verification

Tests that verify the project structure is properly set up:
- All modules can be imported
- Key classes and enums exist
- Constants are defined correctly
- No syntax errors in any files
"""

import pytest
from pathlib import Path


class TestProjectStructure:
    """Verify the project structure is properly set up."""
    
    def test_src_directory_exists(self):
        """Test that the src directory exists."""
        src_path = Path(__file__).parent.parent.parent / "src"
        assert src_path.exists(), "src directory should exist"
        assert src_path.is_dir(), "src should be a directory"
    
    def test_main_package_imports(self):
        """Test that main package can be imported."""
        try:
            import src
            assert hasattr(src, "__version__")
        except ImportError as e:
            pytest.fail(f"Failed to import main package: {e}")


class TestModelsModule:
    """Verify the models module structure."""
    
    def test_models_module_imports(self):
        """Test that models module can be imported."""
        try:
            from src import models
        except ImportError as e:
            pytest.fail(f"Failed to import models module: {e}")
    
    def test_enums_import(self):
        """Test that enums can be imported."""
        try:
            from src.models.enums import PieceColor, Classification, EngineVersion
            
            # Verify enums have expected values
            assert hasattr(PieceColor, "WHITE")
            assert hasattr(PieceColor, "BLACK")
            
            assert hasattr(Classification, "CHECKMATE")
            assert hasattr(Classification, "BEST")
            assert hasattr(Classification, "BRILLIANT")
            
            assert hasattr(EngineVersion, "STOCKFISH_17")
            assert hasattr(EngineVersion, "LICHESS_CLOUD")
        except ImportError as e:
            pytest.fail(f"Failed to import enums: {e}")
    
    def test_state_tree_imports(self):
        """Test that state tree structures can be imported."""
        try:
            from src.models.state_tree import (
                Move,
                Evaluation,
                EngineLine,
                BoardState,
                StateTreeNode
            )
        except ImportError as e:
            pytest.fail(f"Failed to import state tree structures: {e}")
    
    def test_extracted_nodes_imports(self):
        """Test that extracted node structures can be imported."""
        try:
            from src.models.extracted_nodes import (
                ExtractedPreviousNode,
                ExtractedCurrentNode
            )
        except ImportError as e:
            pytest.fail(f"Failed to import extracted nodes: {e}")
    
    def test_game_analysis_imports(self):
        """Test that game analysis structures can be imported."""
        try:
            from src.models.game_analysis import (
                EstimatedRatings,
                GameAnalysis
            )
        except ImportError as e:
            pytest.fail(f"Failed to import game analysis structures: {e}")
    
    def test_models_all_exports(self):
        """Test that models __all__ exports are correct."""
        from src import models
        
        expected_exports = [
            "PieceColor",
            "Classification",
            "EngineVersion",
            "Move",
            "Evaluation",
            "EngineLine",
            "BoardState",
            "StateTreeNode",
            "ExtractedPreviousNode",
            "ExtractedCurrentNode",
            "EstimatedRatings",
            "GameAnalysis",
        ]
        
        for export in expected_exports:
            assert hasattr(models, export), f"models should export {export}"


class TestPreprocessingModule:
    """Verify the preprocessing module structure."""
    
    def test_preprocessing_module_imports(self):
        """Test that preprocessing module can be imported."""
        try:
            from src import preprocessing
        except ImportError as e:
            pytest.fail(f"Failed to import preprocessing module: {e}")
    
    def test_preprocessing_submodules_exist(self):
        """Test that all preprocessing submodules exist."""
        submodules = [
            "parser",
            "engine_analyzer",
            "node_chain_builder",
            "node_extractor",
            "calculator"
        ]
        
        for submodule in submodules:
            try:
                __import__(f"src.preprocessing.{submodule}")
            except ImportError as e:
                pytest.fail(f"Failed to import preprocessing.{submodule}: {e}")


class TestEngineModule:
    """Verify the engine module structure."""
    
    def test_engine_module_imports(self):
        """Test that engine module can be imported."""
        try:
            from src import engine
        except ImportError as e:
            pytest.fail(f"Failed to import engine module: {e}")
    
    def test_engine_submodules_exist(self):
        """Test that all engine submodules exist."""
        submodules = [
            "uci_engine",
            "cloud_evaluator"
        ]
        
        for submodule in submodules:
            try:
                __import__(f"src.engine.{submodule}")
            except ImportError as e:
                pytest.fail(f"Failed to import engine.{submodule}: {e}")


class TestClassificationModule:
    """Verify the classification module structure."""
    
    def test_classification_module_imports(self):
        """Test that classification module can be imported."""
        try:
            from src import classification
        except ImportError as e:
            pytest.fail(f"Failed to import classification module: {e}")
    
    def test_classification_submodules_exist(self):
        """Test that all classification submodules exist."""
        submodules = [
            "classifier",
            "basic_classifier",
            "point_loss_classifier",
            "advanced_classifier",
            "attack_defense_classifier",
            "tactical_analyzer"
        ]
        
        for submodule in submodules:
            try:
                __import__(f"src.classification.{submodule}")
            except ImportError as e:
                pytest.fail(f"Failed to import classification.{submodule}: {e}")


class TestUtilsModule:
    """Verify the utils module structure."""
    
    def test_utils_module_imports(self):
        """Test that utils module can be imported."""
        try:
            from src import utils
        except ImportError as e:
            pytest.fail(f"Failed to import utils module: {e}")
    
    def test_utils_submodules_exist(self):
        """Test that all utils submodules exist."""
        submodules = [
            "chess_utils",
            "evaluation_utils",
            "notation_converter"
        ]
        
        for submodule in submodules:
            try:
                __import__(f"src.utils.{submodule}")
            except ImportError as e:
                pytest.fail(f"Failed to import utils.{submodule}: {e}")


class TestConstants:
    """Verify constants are defined correctly."""
    
    def test_constants_module_imports(self):
        """Test that constants module can be imported."""
        try:
            from src import constants
        except ImportError as e:
            pytest.fail(f"Failed to import constants module: {e}")
    
    def test_centipawn_gradient_defined(self):
        """Test that CENTIPAWN_GRADIENT is defined."""
        from src.constants import CENTIPAWN_GRADIENT
        assert CENTIPAWN_GRADIENT == 0.0035
    
    def test_accuracy_constants_defined(self):
        """Test that accuracy formula constants are defined."""
        from src.constants import (
            ACCURACY_MULTIPLIER,
            ACCURACY_EXPONENT,
            ACCURACY_OFFSET
        )
        assert ACCURACY_MULTIPLIER == 103.16
        assert ACCURACY_EXPONENT == -4.0
        assert ACCURACY_OFFSET == -3.17
    
    def test_starting_fen_defined(self):
        """Test that STARTING_FEN is defined."""
        from src.constants import STARTING_FEN
        expected_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        assert STARTING_FEN == expected_fen
    
    def test_lichess_castling_defined(self):
        """Test that LICHESS_CASTLING mapping is defined."""
        from src.constants import LICHESS_CASTLING
        
        expected_mapping = {
            "e1h1": "e1g1",
            "e1a1": "e1c1",
            "e8h8": "e8g8",
            "e8a8": "e8c8"
        }
        
        assert LICHESS_CASTLING == expected_mapping


class TestConfiguration:
    """Verify configuration classes."""
    
    def test_config_module_imports(self):
        """Test that config module can be imported."""
        try:
            from src import config
        except ImportError as e:
            pytest.fail(f"Failed to import config module: {e}")
    
    def test_engine_config_exists(self):
        """Test that EngineConfig class exists and can be instantiated."""
        from src.config import EngineConfig
        
        # Test default instantiation
        config = EngineConfig()
        assert hasattr(config, "depth")
        assert hasattr(config, "time_limit")
        assert hasattr(config, "multi_pv")
        assert hasattr(config, "use_cloud_eval")
        
        # Test default values
        assert config.depth == 16
        assert config.multi_pv == 2
        assert config.use_cloud_eval is True
    
    def test_classification_config_exists(self):
        """Test that ClassificationConfig class exists."""
        from src.config import ClassificationConfig
        
        config = ClassificationConfig()
        assert hasattr(config, "expand_all_variations")
        assert hasattr(config, "enable_tactical_analysis")
        assert hasattr(config, "enable_attack_defense")
    
    def test_system_config_exists(self):
        """Test that SystemConfig class exists."""
        from src.config import SystemConfig
        
        # Test default factory method
        config = SystemConfig.default()
        assert hasattr(config, "engine")
        assert hasattr(config, "classification")
        
        # Verify nested configs
        assert config.engine.depth == 16
        assert config.classification.enable_tactical_analysis is True


class TestDataStructures:
    """Verify data structures can be instantiated."""
    
    def test_move_structure(self):
        """Test Move dataclass."""
        from src.models.state_tree import Move
        
        move = Move(san="Nf3", uci="g1f3")
        assert move.san == "Nf3"
        assert move.uci == "g1f3"
    
    def test_evaluation_structure(self):
        """Test Evaluation dataclass."""
        from src.models.state_tree import Evaluation
        
        # Centipawn evaluation
        eval_cp = Evaluation(type="centipawn", value=100.0)
        assert eval_cp.type == "centipawn"
        assert eval_cp.value == 100.0
        
        # Mate evaluation
        eval_mate = Evaluation(type="mate", value=3.0)
        assert eval_mate.type == "mate"
        assert eval_mate.value == 3.0
    
    def test_engine_line_structure(self):
        """Test EngineLine dataclass."""
        from src.models.state_tree import EngineLine, Evaluation, Move
        
        line = EngineLine(
            evaluation=Evaluation(type="centipawn", value=45.0),
            source="stockfish-17",
            depth=20,
            index=1,
            moves=[Move(san="e4", uci="e2e4")]
        )
        
        assert line.depth == 20
        assert line.index == 1
        assert len(line.moves) == 1
    
    def test_board_state_structure(self):
        """Test BoardState dataclass."""
        from src.models.state_tree import BoardState
        from src.constants import STARTING_FEN
        
        state = BoardState(fen=STARTING_FEN)
        assert state.fen == STARTING_FEN
        assert state.move is None
        assert len(state.engine_lines) == 0
    
    def test_state_tree_node_structure(self):
        """Test StateTreeNode dataclass."""
        from src.models.state_tree import StateTreeNode, BoardState
        from src.constants import STARTING_FEN
        
        node = StateTreeNode(
            id="root",
            mainline=True,
            parent=None,
            children=[],
            state=BoardState(fen=STARTING_FEN)
        )
        
        assert node.id == "root"
        assert node.mainline is True
        assert node.parent is None
        assert len(node.children) == 0


class TestFileStructure:
    """Verify all expected files exist."""
    
    def test_all_python_files_exist(self):
        """Test that all expected Python files exist."""
        base_path = Path(__file__).parent.parent.parent / "src"
        
        expected_files = [
            "__init__.py",
            "constants.py",
            "config.py",
            "models/__init__.py",
            "models/enums.py",
            "models/state_tree.py",
            "models/extracted_nodes.py",
            "models/game_analysis.py",
            "preprocessing/__init__.py",
            "preprocessing/parser.py",
            "preprocessing/engine_analyzer.py",
            "preprocessing/node_chain_builder.py",
            "preprocessing/node_extractor.py",
            "preprocessing/calculator.py",
            "engine/__init__.py",
            "engine/uci_engine.py",
            "engine/cloud_evaluator.py",
            "classification/__init__.py",
            "classification/classifier.py",
            "classification/basic_classifier.py",
            "classification/point_loss_classifier.py",
            "classification/advanced_classifier.py",
            "classification/attack_defense_classifier.py",
            "classification/tactical_analyzer.py",
            "utils/__init__.py",
            "utils/chess_utils.py",
            "utils/evaluation_utils.py",
            "utils/notation_converter.py",
        ]
        
        for file_path in expected_files:
            full_path = base_path / file_path
            assert full_path.exists(), f"Expected file {file_path} does not exist"
            assert full_path.is_file(), f"{file_path} should be a file"
    
    def test_project_config_files_exist(self):
        """Test that project configuration files exist."""
        project_root = Path(__file__).parent.parent.parent
        
        expected_files = [
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "README.md",
            ".gitignore"
        ]
        
        for file_name in expected_files:
            file_path = project_root / file_name
            assert file_path.exists(), f"Expected file {file_name} does not exist"
            assert file_path.is_file(), f"{file_name} should be a file"


class TestDocumentation:
    """Verify documentation structure."""
    
    def test_docs_directory_exists(self):
        """Test that docs directory exists."""
        docs_path = Path(__file__).parent.parent.parent / "docs"
        assert docs_path.exists(), "docs directory should exist"
        assert docs_path.is_dir(), "docs should be a directory"
    
    def test_architecture_docs_exist(self):
        """Test that architecture documentation exists."""
        arch_path = Path(__file__).parent.parent.parent / "docs" / "architecture"
        assert arch_path.exists(), "docs/architecture directory should exist"
        
        # Check for key architecture documents
        expected_docs = [
            "00-preprocessing-pipeline.md",
            "01-core-concepts.md"
        ]
        
        for doc in expected_docs:
            doc_path = arch_path / doc
            assert doc_path.exists(), f"Expected doc {doc} does not exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

