"""
Training pipeline for NeuroChess
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Tuple
from tqdm import tqdm
from engine.neural_net import ChessNet
from engine.utils import save_checkpoint, load_checkpoint
import config


class Trainer:
    """Handles training of the neural network."""
    
    def __init__(self, model: ChessNet = None, device: str = 'cpu'):
        """
        Initialize trainer.
        
        Args:
            model: Neural network model (creates new if None)
            device: Device to train on
        """
        self.device = device
        
        if model is None:
            self.model = ChessNet().to(device)
        else:
            self.model = model.to(device)
        
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=config.TRAINING_CONFIG['learning_rate'],
            weight_decay=config.TRAINING_CONFIG['weight_decay']
        )
        
        self.iteration = 0
    
    def train_on_data(self, training_data: List[Tuple], num_epochs: int = None) -> dict:
        """
        Train model on self-play data.
        
        Args:
            training_data: List of (board_state, policy, value) tuples
            num_epochs: Number of training epochs
            
        Returns:
            Dictionary with training statistics
        """
        num_epochs = num_epochs or config.TRAINING_CONFIG['num_epochs']
        batch_size = config.TRAINING_CONFIG['batch_size']
        
        # Convert to tensors
        boards = torch.FloatTensor([data[0] for data in training_data]).to(self.device)
        policies = torch.FloatTensor([data[1] for data in training_data]).to(self.device)
        values = torch.FloatTensor([data[2] for data in training_data]).to(self.device).unsqueeze(1)
        
        dataset = torch.utils.data.TensorDataset(boards, policies, values)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        self.model.train()
        total_loss = 0.0
        total_value_loss = 0.0
        total_policy_loss = 0.0
        
        for epoch in range(num_epochs):
            epoch_loss = 0.0
            epoch_value_loss = 0.0
            epoch_policy_loss = 0.0
            
            for batch_boards, batch_policies, batch_values in tqdm(
                dataloader, desc=f"Epoch {epoch+1}/{num_epochs}", leave=False
            ):
                self.optimizer.zero_grad()
                
                # Forward pass
                pred_policies, pred_values = self.model(batch_boards)
                
                # Compute losses
                # Policy loss: KL divergence (since we have probability distributions)
                pred_policies_softmax = nn.functional.log_softmax(pred_policies, dim=1)
                policy_loss = nn.functional.kl_div(
                    pred_policies_softmax,
                    batch_policies,
                    reduction='batchmean'
                )
                
                # Value loss: MSE
                value_loss = nn.functional.mse_loss(pred_values, batch_values)
                
                # Total loss
                loss = (
                    config.TRAINING_CONFIG['value_loss_weight'] * value_loss +
                    config.TRAINING_CONFIG['policy_loss_weight'] * policy_loss
                )
                
                # Backward pass
                loss.backward()
                self.optimizer.step()
                
                epoch_loss += loss.item()
                epoch_value_loss += value_loss.item()
                epoch_policy_loss += policy_loss.item()
            
            total_loss += epoch_loss / len(dataloader)
            total_value_loss += epoch_value_loss / len(dataloader)
            total_policy_loss += epoch_policy_loss / len(dataloader)
        
        self.model.eval()
        
        return {
            'avg_loss': total_loss / num_epochs,
            'avg_value_loss': total_value_loss / num_epochs,
            'avg_policy_loss': total_policy_loss / num_epochs,
        }
    
    def save_checkpoint(self, filepath: str = None):
        """Save model checkpoint."""
        if filepath is None:
            os.makedirs(config.PATHS['checkpoint_dir'], exist_ok=True)
            filepath = os.path.join(
                config.PATHS['checkpoint_dir'],
                f"{config.PATHS['model_name']}_iter_{self.iteration}.pth"
            )
        
        save_checkpoint(self.model, self.optimizer, self.iteration, filepath)
        print(f"Saved checkpoint to {filepath}")
    
    def load_checkpoint(self, filepath: str):
        """Load model checkpoint."""
        self.iteration = load_checkpoint(self.model, self.optimizer, filepath)
        print(f"Loaded checkpoint from {filepath} (iteration {self.iteration})")
    
    def get_model(self) -> ChessNet:
        """Get the trained model."""
        return self.model
    
    def train_iteration(self, training_data: List[Tuple]) -> dict:
        """
        Perform one training iteration.
        
        Args:
            training_data: Training data from self-play
            
        Returns:
            Training statistics
        """
        stats = self.train_on_data(training_data)
        self.iteration += 1
        
        # Save checkpoint periodically
        if self.iteration % config.TRAINING_CONFIG['checkpoint_interval'] == 0:
            self.save_checkpoint()
        
        return stats

