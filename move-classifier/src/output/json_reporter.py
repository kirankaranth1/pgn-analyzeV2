"""JSON report generation."""

import json
from typing import Dict, List
from ..core.state_tree import StateTreeNode
from ..core.types import Classification


class JSONReporter:
    """Generates JSON analysis reports."""
    
    @staticmethod
    def generate_report(headers: Dict[str, str], root: StateTreeNode) -> Dict:
        """Generate complete JSON report.
        
        Args:
            headers: Game headers
            root: Root state tree node
            
        Returns:
            Report dictionary
        """
        # Get mainline nodes (skip root)
        nodes = root.traverse_mainline()[1:]
        
        # Extract moves
        moves = []
        move_number = 1
        half_move = 1
        
        for node in nodes:
            if not node.state.move:
                continue
            
            move_data = {
                "move_number": move_number,
                "half_move": half_move,
                "color": node.state.move_color.value if node.state.move_color else "unknown",
                "san": node.state.move.san,
                "uci": node.state.move.uci,
                "fen_after": node.state.fen,
            }
            
            # Add classification if available
            if node.state.classification:
                move_data["classification"] = node.state.classification.value
            
            # Add accuracy if available
            if node.state.accuracy is not None:
                move_data["accuracy"] = round(node.state.accuracy, 2)
            
            # Add opening if available
            if node.state.opening:
                move_data["opening"] = node.state.opening
            
            # Add evaluation if available
            top_line = node.state.get_top_line()
            if top_line:
                move_data["evaluation"] = top_line.evaluation.to_dict()
                if top_line.moves:
                    move_data["best_move"] = top_line.moves[0].san
            
            # Add point loss
            if node.parent and node.parent.state.get_top_line():
                parent_top = node.parent.state.get_top_line()
                if parent_top and parent_top.moves:
                    move_data["engine_best_move"] = parent_top.moves[0].san
            
            moves.append(move_data)
            
            # Increment move numbers
            half_move += 1
            if node.state.move_color and node.state.move_color.value == "black":
                move_number += 1
        
        # Calculate statistics
        statistics = JSONReporter._calculate_statistics(nodes)
        
        # Build report
        report = {
            "game_info": {
                "white": headers.get("white", "Unknown"),
                "black": headers.get("black", "Unknown"),
                "result": headers.get("result", "*"),
                "date": headers.get("date", "????.??.??"),
                "event": headers.get("event", ""),
                "site": headers.get("site", ""),
            },
            "moves": moves,
            "statistics": statistics
        }
        
        return report
    
    @staticmethod
    def _calculate_statistics(nodes: List[StateTreeNode]) -> Dict:
        """Calculate game statistics.
        
        Args:
            nodes: List of state tree nodes
            
        Returns:
            Statistics dictionary
        """
        white_stats = {
            "brilliant": 0,
            "critical": 0,
            "best": 0,
            "excellent": 0,
            "okay": 0,
            "inaccuracy": 0,
            "mistake": 0,
            "blunder": 0,
            "theory": 0,
            "forced": 0,
            "total_moves": 0,
            "total_accuracy": 0.0,
            "average_accuracy": 0.0
        }
        
        black_stats = white_stats.copy()
        
        for node in nodes:
            if not node.state.classification or not node.state.move_color:
                continue
            
            # Determine which stats to update
            stats = white_stats if node.state.move_color.value == "white" else black_stats
            
            # Update classification counts
            classification = node.state.classification.value
            if classification in stats:
                stats[classification] += 1
            
            # Update accuracy
            stats["total_moves"] += 1
            if node.state.accuracy is not None:
                stats["total_accuracy"] += node.state.accuracy
        
        # Calculate averages
        if white_stats["total_moves"] > 0:
            white_stats["average_accuracy"] = round(
                white_stats["total_accuracy"] / white_stats["total_moves"], 2
            )
        
        if black_stats["total_moves"] > 0:
            black_stats["average_accuracy"] = round(
                black_stats["total_accuracy"] / black_stats["total_moves"], 2
            )
        
        # Remove temporary fields
        del white_stats["total_accuracy"]
        del black_stats["total_accuracy"]
        
        return {
            "white": white_stats,
            "black": black_stats
        }
    
    @staticmethod
    def save_report(report: Dict, output_file: str) -> None:
        """Save report to JSON file.
        
        Args:
            report: Report dictionary
            output_file: Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Report saved to: {output_file}")

