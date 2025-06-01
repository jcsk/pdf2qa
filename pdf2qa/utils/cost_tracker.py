"""
Cost tracking utilities for OpenAI and LlamaParse API calls.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from pdf2qa.utils.logging import get_logger

logger = get_logger()


@dataclass
class APICall:
    """Represents a single API call with cost information."""
    timestamp: str
    service: str  # "openai" or "llamaparse"
    operation: str  # "chat_completion", "parse", etc.
    model: Optional[str]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    job_id: Optional[str] = None
    metadata: Optional[Dict] = None


class CostTracker:
    """Tracks and manages API costs for OpenAI and LlamaParse."""
    
    # OpenAI pricing (as of 2024) - prices per 1M tokens
    OPENAI_PRICING = {
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    }
    
    # LlamaParse pricing (as of 2024) - per page
    LLAMAPARSE_PRICING = {
        "per_page": 0.003  # $0.003 per page
    }
    
    def __init__(self, cost_file: str = "costs.json"):
        """Initialize cost tracker with optional cost file."""
        self.cost_file = cost_file
        self.calls: List[APICall] = []
        self.load_costs()
    
    def load_costs(self):
        """Load existing cost data from file."""
        if os.path.exists(self.cost_file):
            try:
                with open(self.cost_file, 'r') as f:
                    data = json.load(f)
                    self.calls = [APICall(**call) for call in data.get('calls', [])]
                logger.info(f"Loaded {len(self.calls)} previous API calls from {self.cost_file}")
            except Exception as e:
                logger.warning(f"Could not load cost file {self.cost_file}: {e}")
                self.calls = []
    
    def save_costs(self):
        """Save cost data to file."""
        try:
            data = {
                "calls": [asdict(call) for call in self.calls],
                "summary": self.get_summary()
            }
            with open(self.cost_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved cost data to {self.cost_file}")
        except Exception as e:
            logger.error(f"Could not save cost file {self.cost_file}: {e}")
    
    def calculate_openai_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for OpenAI API call."""
        if model not in self.OPENAI_PRICING:
            logger.warning(f"Unknown OpenAI model: {model}, using gpt-3.5-turbo pricing")
            model = "gpt-3.5-turbo"
        
        pricing = self.OPENAI_PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    
    def calculate_llamaparse_cost(self, pages: int) -> float:
        """Calculate cost for LlamaParse API call."""
        return pages * self.LLAMAPARSE_PRICING["per_page"]
    
    def track_openai_call(self, model: str, input_tokens: int, output_tokens: int, 
                         operation: str = "chat_completion", job_id: Optional[str] = None,
                         metadata: Optional[Dict] = None) -> float:
        """Track an OpenAI API call and return the cost."""
        total_tokens = input_tokens + output_tokens
        cost = self.calculate_openai_cost(model, input_tokens, output_tokens)
        
        call = APICall(
            timestamp=datetime.now().isoformat(),
            service="openai",
            operation=operation,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            job_id=job_id,
            metadata=metadata
        )
        
        self.calls.append(call)
        logger.info(f"OpenAI call: {model} - {total_tokens} tokens - ${cost:.4f}")
        return cost
    
    def track_llamaparse_call(self, pages: int, job_id: Optional[str] = None,
                             metadata: Optional[Dict] = None) -> float:
        """Track a LlamaParse API call and return the cost."""
        cost = self.calculate_llamaparse_cost(pages)
        
        call = APICall(
            timestamp=datetime.now().isoformat(),
            service="llamaparse",
            operation="parse",
            model=None,
            input_tokens=pages,  # Using input_tokens field to store page count
            output_tokens=0,
            total_tokens=pages,
            cost_usd=cost,
            job_id=job_id,
            metadata=metadata
        )
        
        self.calls.append(call)
        logger.info(f"LlamaParse call: {pages} pages - ${cost:.4f}")
        return cost
    
    def get_summary(self) -> Dict:
        """Get cost summary by service and model."""
        summary = {
            "total_cost": 0.0,
            "total_calls": len(self.calls),
            "by_service": {},
            "by_model": {},
            "by_job": {}
        }
        
        for call in self.calls:
            # Total cost
            summary["total_cost"] += call.cost_usd
            
            # By service
            if call.service not in summary["by_service"]:
                summary["by_service"][call.service] = {"cost": 0.0, "calls": 0}
            summary["by_service"][call.service]["cost"] += call.cost_usd
            summary["by_service"][call.service]["calls"] += 1
            
            # By model
            model_key = call.model or f"{call.service}_default"
            if model_key not in summary["by_model"]:
                summary["by_model"][model_key] = {"cost": 0.0, "calls": 0, "tokens": 0}
            summary["by_model"][model_key]["cost"] += call.cost_usd
            summary["by_model"][model_key]["calls"] += 1
            summary["by_model"][model_key]["tokens"] += call.total_tokens
            
            # By job
            if call.job_id:
                if call.job_id not in summary["by_job"]:
                    summary["by_job"][call.job_id] = {"cost": 0.0, "calls": 0}
                summary["by_job"][call.job_id]["cost"] += call.cost_usd
                summary["by_job"][call.job_id]["calls"] += 1
        
        return summary
    
    def print_summary(self):
        """Print a formatted cost summary."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 API COST SUMMARY")
        print("="*60)
        print(f"💰 Total Cost: ${summary['total_cost']:.4f}")
        print(f"📞 Total Calls: {summary['total_calls']}")
        
        print("\n🔧 By Service:")
        for service, data in summary["by_service"].items():
            print(f"  {service}: ${data['cost']:.4f} ({data['calls']} calls)")
        
        print("\n🤖 By Model:")
        for model, data in summary["by_model"].items():
            if "tokens" in data and data["tokens"] > 0:
                print(f"  {model}: ${data['cost']:.4f} ({data['calls']} calls, {data['tokens']:,} tokens)")
            else:
                print(f"  {model}: ${data['cost']:.4f} ({data['calls']} calls)")
        
        if summary["by_job"]:
            print("\n📋 By Job:")
            for job_id, data in summary["by_job"].items():
                print(f"  {job_id}: ${data['cost']:.4f} ({data['calls']} calls)")
        
        print("="*60)


# Global cost tracker instance
cost_tracker = CostTracker()
