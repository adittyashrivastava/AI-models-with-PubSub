"""
Serializer classes for converting data between different formats
"""

from abc import ABC, abstractmethod
import numpy as np
import json
from typing import Any, Union


class Serializer(ABC):
    """Abstract base class for serializers"""
    
    @abstractmethod
    def serialize(self, data: Any) -> bytes:
        """Serialize data to bytes"""
        pass
    
    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes back to original data type"""
        pass


class NumpySerializer(Serializer):
    """Serializer for numpy arrays"""
    
    def serialize(self, data: np.ndarray) -> bytes:
        """
        Convert numpy array to bytes for transmission
        
        Args:
            data: Numpy array to serialize
            
        Returns:
            Serialized bytes
        """
        # Convert to list, then to JSON string, then to bytes
        return json.dumps(data.tolist()).encode('utf-8')
    
    def deserialize(self, data: bytes) -> np.ndarray:
        """
        Convert bytes back to numpy array
        
        Args:
            data: Bytes to deserialize
            
        Returns:
            Numpy array
        """
        # Convert bytes to string, then to list, then to numpy array
        return np.array(json.loads(data.decode('utf-8')))


class JSONSerializer(Serializer):
    """Serializer for JSON-compatible data"""
    
    def serialize(self, data: Union[dict, list]) -> bytes:
        """
        Convert JSON-compatible data to bytes
        
        Args:
            data: Dictionary or list to serialize
            
        Returns:
            Serialized bytes
        """
        return json.dumps(data).encode('utf-8')
    
    def deserialize(self, data: bytes) -> Union[dict, list]:
        """
        Convert bytes back to JSON data
        
        Args:
            data: Bytes to deserialize
            
        Returns:
            Dictionary or list
        """
        return json.loads(data.decode('utf-8'))
