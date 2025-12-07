"""
Neural network architecture for NeuroChess
PyTorch CNN model with policy and value heads
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple
import config


class ResidualBlock(nn.Module):
    """Residual block for the neural network."""
    
    def __init__(self, num_filters: int):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(num_filters, num_filters, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(num_filters)
        self.conv2 = nn.Conv2d(num_filters, num_filters, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(num_filters)
    
    def forward(self, x):
        residual = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        out = F.relu(out)
        return out


class ChessNet(nn.Module):
    """
    Neural network for chess position evaluation.
    
    Architecture:
    - Input: 18 planes of 8x8 (board representation)
    - Convolutional layers with residual blocks
    - Policy head: outputs move probabilities (4096 possible moves)
    - Value head: outputs position evaluation (-1 to 1)
    """
    
    def __init__(self, num_res_blocks: int = None, num_filters: int = None,
                 value_head_hidden: int = None, policy_head_hidden: int = None,
                 dropout: float = None):
        super(ChessNet, self).__init__()
        
        # Use config defaults if not provided
        num_res_blocks = num_res_blocks or config.NN_CONFIG['num_res_blocks']
        num_filters = num_filters or config.NN_CONFIG['num_filters']
        value_head_hidden = value_head_hidden or config.NN_CONFIG['value_head_hidden']
        policy_head_hidden = policy_head_hidden or config.NN_CONFIG['policy_head_hidden']
        dropout = dropout or config.NN_CONFIG['dropout']
        
        # Input layer
        self.input_conv = nn.Conv2d(18, num_filters, kernel_size=3, padding=1)
        self.input_bn = nn.BatchNorm2d(num_filters)
        
        # Residual blocks
        self.res_blocks = nn.ModuleList([
            ResidualBlock(num_filters) for _ in range(num_res_blocks)
        ])
        
        # Policy head
        self.policy_conv = nn.Conv2d(num_filters, 32, kernel_size=1)
        self.policy_bn = nn.BatchNorm2d(32)
        self.policy_fc = nn.Linear(32 * 8 * 8, policy_head_hidden)
        self.policy_dropout = nn.Dropout(dropout)
        self.policy_out = nn.Linear(policy_head_hidden, 4096)  # 64*64 possible moves
        
        # Value head
        self.value_conv = nn.Conv2d(num_filters, 32, kernel_size=1)
        self.value_bn = nn.BatchNorm2d(32)
        self.value_fc1 = nn.Linear(32 * 8 * 8, value_head_hidden)
        self.value_dropout = nn.Dropout(dropout)
        self.value_fc2 = nn.Linear(value_head_hidden, 1)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, 18, 8, 8)
            
        Returns:
            policy: Policy tensor of shape (batch_size, 4096)
            value: Value tensor of shape (batch_size, 1)
        """
        # Input convolution
        x = F.relu(self.input_bn(self.input_conv(x)))
        
        # Residual blocks
        for res_block in self.res_blocks:
            x = res_block(x)
        
        # Policy head
        policy = F.relu(self.policy_bn(self.policy_conv(x)))
        policy = policy.view(policy.size(0), -1)
        policy = F.relu(self.policy_fc(policy))
        policy = self.policy_dropout(policy)
        policy = self.policy_out(policy)
        
        # Value head
        value = F.relu(self.value_bn(self.value_conv(x)))
        value = value.view(value.size(0), -1)
        value = F.relu(self.value_fc1(value))
        value = self.value_dropout(value)
        value = torch.tanh(self.value_fc2(value))
        
        return policy, value
    
    def predict(self, board_tensor: np.ndarray, device: str = 'cpu') -> Tuple[np.ndarray, float]:
        """
        Predict policy and value for a single board position.
        
        Args:
            board_tensor: numpy array of shape (18, 8, 8)
            device: device to run inference on
            
        Returns:
            policy: numpy array of shape (4096,)
            value: float value
        """
        self.eval()
        with torch.no_grad():
            # Add batch dimension
            x = torch.FloatTensor(board_tensor).unsqueeze(0).to(device)
            policy, value = self.forward(x)
            policy = F.softmax(policy, dim=1)
            policy = policy.cpu().numpy()[0]
            value = value.cpu().numpy()[0, 0]
        return policy, value

