"""
Configuration management for AETS.
Centralized settings with environment variable fallbacks.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class TradingMode(Enum):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"

class EvolutionStrategy(Enum):
    NEUROEVOLUTION = "neuroevolution"
    RL = "reinforcement_learning"
    HYBRID = "hybrid"

@dataclass
class DatabaseConfig:
    """Firebase configuration"""
    project_id: str = field(default_factory=lambda: os.getenv("FIREBASE_PROJECT_ID", ""))
    credentials_path: str = field(default_factory=lambda: os.getenv("FIREBASE_CREDENTIALS_PATH", "./config/firebase_credentials.json"))
    collections: Dict[str, str] = field(default_factory=lambda: {
        "strategies": "evolutionary_strategies",
        "trades": "executed_trades",
        "performance": "strategy_performance",
        "market_data": "market_snapshots"
    })
    
    def validate(self) -> bool:
        """Validate Firebase configuration"""
        if not self.project_id:
            raise ValueError("FIREBASE_PROJECT_ID environment variable must be set")
        if not Path(self.credentials_path).exists():
            raise FileNotFoundError(f"Firebase credentials not found at: {self.credentials_path}")
        return True

@dataclass
class TradingConfig:
    """Trading platform configuration"""
    mode: TradingMode = field(default_factory=lambda: TradingMode[os.getenv("TRADING_MODE", "PAPER").upper()])
    exchange: str = field(default_factory=lambda: os.getenv("EXCHANGE", "binance").lower())
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("EXCHANGE_API_KEY"))
    api_secret: Optional[str] = field(default_factory=lambda: os.getenv("EXCHANGE_API_SECRET"))
    symbols: list = field(default_factory=lambda: json.loads(os.getenv("TRADING_SYMBOLS", '["BTC/USDT", "ETH/USDT"]')))
    base_currency: str = field(default_factory=lambda: os.getenv("BASE_CURRENCY", "USDT"))
    max_position_size: float = field(default_factory=lambda: float(os.getenv("MAX_POSITION_SIZE", "0.1")))  # 10% of portfolio
    
    def validate(self) -> bool:
        """Validate trading configuration"""
        if self.mode in [TradingMode.PAPER, TradingMode.LIVE]:
            if not self.api_key or not self.api_secret:
                raise ValueError("API credentials required for paper/live trading")
        return True

@dataclass
class EvolutionConfig:
    """Evolution algorithm configuration"""
    strategy: EvolutionStrategy = field(default_factory=lambda: EvolutionStrategy[os.getenv("EVOLUTION_STRATEGY", "HYBRID").upper()])
    population_size: int = field(default_factory=lambda: int(os.getenv("POPULATION_SIZE", "50")))
    generations: int = field(default_factory=lambda: int(os.getenv("GENERATIONS", "100")))
    mutation_rate: float = field(default_factory=lambda: float(os.getenv("MUTATION_RATE", "0.1")))
    crossover_rate: float = field(default_factory=lambda: float(os.getenv("CROSSOVER_RATE", "0.7")))
    elitism_count: int = field(default_factory=lambda: int(os.getenv("ELITISM_COUNT", "2")))
    
    def validate(self) -> bool:
        """Validate evolution configuration"""
        if self.population_size < 10:
            raise ValueError("Population size must be at least 10")
        if not 0 <= self.mutation_rate <= 1:
            raise ValueError("Mutation rate must be between 0 and 1")
        return True

@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_drawdown: float = field(default_factory=lambda: float(os.getenv("MAX_DRAWDOWN", "0.2")))  # 20%
    max_daily_loss: float = field(default_factory=lambda: float(os.getenv("MAX_DAILY_LOSS", "0.05")))  # 5%
    stop_loss_pct: float = field(default_factory=lambda: float(os.getenv("STOP_LOSS_PCT", "0.02")))  # 2%
    take_profit_pct: float = field(default_factory=lambda: float(os.getenv("TAKE_PROFIT_PCT", "0.04")))  # 4%
    max_leverage: float = field(default_factory=lambda: float(os.getenv("MAX_LEVERAGE", "3.0")))
    risk_per_trade: float