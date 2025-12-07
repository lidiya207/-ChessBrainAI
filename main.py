"""
Main entry point for NeuroChess
"""

import argparse
import os
import torch
from engine.neural_net import ChessNet
from engine.trainer import Trainer
from engine.self_play import SelfPlay
from ui.cli import ChessCLI
from ui.simple_gui import ChessGUI
import config


def train_model(num_iterations: int = 10, resume_from: str = None):
    """
    Train the model using self-play.
    
    Args:
        num_iterations: Number of training iterations
        resume_from: Path to checkpoint to resume from
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Initialize trainer
    trainer = Trainer(device=device)
    
    # Load checkpoint if specified
    if resume_from:
        if os.path.exists(resume_from):
            trainer.load_checkpoint(resume_from)
        else:
            print(f"Warning: Checkpoint {resume_from} not found. Starting from scratch.")
    
    # Training loop
    for iteration in range(trainer.iteration, trainer.iteration + num_iterations):
        print(f"\n{'='*60}")
        print(f"Training Iteration {iteration + 1}/{trainer.iteration + num_iterations}")
        print(f"{'='*60}\n")
        
        # Self-play
        model = trainer.get_model()
        self_play = SelfPlay(model, device=device)
        training_data = self_play.generate_games()
        
        print(f"\nGenerated {len(training_data)} training positions")
        
        # Train on self-play data
        stats = trainer.train_iteration(training_data)
        
        print(f"\nTraining Statistics:")
        print(f"  Average Loss: {stats['avg_loss']:.4f}")
        print(f"  Value Loss: {stats['avg_value_loss']:.4f}")
        print(f"  Policy Loss: {stats['avg_policy_loss']:.4f}")
        
        # Save checkpoint
        trainer.save_checkpoint()
    
    print(f"\nTraining complete! Model saved to {config.PATHS['checkpoint_dir']}")


def play_cli(checkpoint_path: str = None, human_plays_white: bool = True):
    """
    Play against the AI using command-line interface.
    
    Args:
        checkpoint_path: Path to model checkpoint
        human_plays_white: Whether human plays as white
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Load model
    model = ChessNet().to(device)
    
    if checkpoint_path and os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Loaded model from {checkpoint_path}")
    else:
        print("Warning: No checkpoint found. Using untrained model.")
        if checkpoint_path:
            print(f"  (Tried to load: {checkpoint_path})")
    
    model.eval()
    
    # Start CLI
    cli = ChessCLI(model, device=device)
    cli.play(human_plays_white=human_plays_white)


def play_gui(checkpoint_path: str = None):
    """
    Play against the AI using GUI.
    
    Args:
        checkpoint_path: Path to model checkpoint
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Load model
    model = ChessNet().to(device)
    
    if checkpoint_path and os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"Loaded model from {checkpoint_path}")
    else:
        print("Warning: No checkpoint found. Using untrained model.")
        if checkpoint_path:
            print(f"  (Tried to load: {checkpoint_path})")
    
    model.eval()
    
    # Start GUI
    gui = ChessGUI(model, device=device)
    gui.run()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='NeuroChess - AI Chess Engine')
    
    parser.add_argument(
        'mode',
        choices=['train', 'play', 'gui'],
        help='Mode: train (self-play training), play (CLI), or gui (GUI)'
    )
    
    parser.add_argument(
        '--iterations',
        type=int,
        default=10,
        help='Number of training iterations (for train mode)'
    )
    
    parser.add_argument(
        '--checkpoint',
        type=str,
        default=None,
        help='Path to model checkpoint to load'
    )
    
    parser.add_argument(
        '--resume',
        type=str,
        default=None,
        help='Path to checkpoint to resume training from'
    )
    
    parser.add_argument(
        '--black',
        action='store_true',
        help='Play as black (for play mode)'
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs(config.PATHS['checkpoint_dir'], exist_ok=True)
    os.makedirs(config.PATHS['game_data_dir'], exist_ok=True)
    
    if args.mode == 'train':
        train_model(num_iterations=args.iterations, resume_from=args.resume)
    elif args.mode == 'play':
        # Find latest checkpoint if not specified
        checkpoint = args.checkpoint
        if checkpoint is None:
            checkpoint_dir = config.PATHS['checkpoint_dir']
            if os.path.exists(checkpoint_dir):
                checkpoints = [f for f in os.listdir(checkpoint_dir) if f.endswith('.pth')]
                if checkpoints:
                    checkpoint = os.path.join(checkpoint_dir, sorted(checkpoints)[-1])
                    print(f"Using latest checkpoint: {checkpoint}")
        
        play_cli(checkpoint_path=checkpoint, human_plays_white=not args.black)
    elif args.mode == 'gui':
        # Find latest checkpoint if not specified
        checkpoint = args.checkpoint
        if checkpoint is None:
            checkpoint_dir = config.PATHS['checkpoint_dir']
            if os.path.exists(checkpoint_dir):
                checkpoints = [f for f in os.listdir(checkpoint_dir) if f.endswith('.pth')]
                if checkpoints:
                    checkpoint = os.path.join(checkpoint_dir, sorted(checkpoints)[-1])
                    print(f"Using latest checkpoint: {checkpoint}")
        
        play_gui(checkpoint_path=checkpoint)


def on_login_success(username):
    """Callback when user successfully logs in."""
    from ui.game_menu import GameMenu
    menu = GameMenu(username)
    menu.run()


if __name__ == '__main__':
    import sys
    
    # If no arguments, show login screen
    if len(sys.argv) == 1:
        from ui.auth import AuthGUI
        auth = AuthGUI(on_login_success)
        auth.run()
    else:
        # Otherwise, use command-line mode (for training, etc.)
        main()

