"""
CourseForge - Course File Module
Handles reading and writing PGA 2K course files
"""
import json
import base64
import gzip
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class GameVersion(Enum):
    TGC2019 = "2K19"
    PGA2K23 = "2K23"
    PGA2K25 = "2K25"


class CourseFile:
    """Represents a PGA 2K course file"""
    
    def __init__(self, course_data: Dict[str, Any], outer_data: Dict[str, Any], version: GameVersion):
        """
        Args:
            course_data: The inner CourseDescription JSON
            outer_data: The outer JSON with metadata/thumbnail
            version: Game version
        """
        self.course_data = course_data
        self.outer_data = outer_data
        self.version = version
    
    @classmethod
    def load(cls, filepath: Path) -> 'CourseFile':
        """Load a .course file from disk"""
        with open(filepath, 'rb') as f:
            compressed_data = f.read()
        
        # Decompress outer layer
        decompressed = gzip.decompress(compressed_data)
        
        # Decode UTF-16 (handle BOM if present)
        try:
            json_str = decompressed.decode('utf-16')
        except:
            json_str = decompressed.decode('utf-16-le')
        
        outer_json = json.loads(json_str)
        
        # Decode CourseDescription
        course_desc_b64 = outer_json['binaryData']['CourseDescription']
        course_desc_compressed = base64.b64decode(course_desc_b64)
        course_desc_data = gzip.decompress(course_desc_compressed)
        
        # Skip BOM if present
        if course_desc_data[:2] == b'\xff\xfe':
            course_desc_data = course_desc_data[2:]
        
        course_desc_str = course_desc_data.decode('utf-16-le')
        course_data = json.loads(course_desc_str)
        
        # Detect version
        version = cls._detect_version(course_data)
        
        return cls(course_data, outer_json, version)
    
    @staticmethod
    def _detect_version(data: Dict[str, Any]) -> GameVersion:
        """Detect which game version based on structure"""
        if 'terrainHeight' in data and isinstance(data['terrainHeight'], list):
            return GameVersion.PGA2K25
        elif 'userLayers2' in data:
            return GameVersion.PGA2K23
        elif 'userLayers' in data:
            return GameVersion.TGC2019
        else:
            return GameVersion.PGA2K25
    
    def save(self, filepath: Path):
        """Save course file to disk"""
        # Re-encode CourseDescription
        inner_json_str = json.dumps(self.course_data)
        inner_utf16 = inner_json_str.encode('utf-16-le')
        inner_compressed = gzip.compress(inner_utf16)
        inner_b64 = base64.b64encode(inner_compressed).decode('ascii')
        
        # Update outer structure
        self.outer_data['binaryData']['CourseDescription'] = inner_b64
        
        # Encode outer JSON
        outer_json_str = json.dumps(self.outer_data)
        
        # 2K25 uses UTF-16 with BOM
        if self.version == GameVersion.PGA2K25:
            outer_utf16 = outer_json_str.encode('utf-16')
        else:
            outer_utf16 = outer_json_str.encode('utf-16-le')
        
        # Final compression
        final_compressed = gzip.compress(outer_utf16)
        
        # Write to file
        with open(filepath, 'wb') as f:
            f.write(final_compressed)
    
    def get_name(self) -> str:
        """Get course name"""
        return self.course_data.get('name', 'Unnamed Course')
    
    def set_name(self, name: str):
        """Set course name"""
        self.course_data['name'] = name
    
    def get_theme(self) -> int:
        """Get theme ID"""
        return self.course_data.get('theme', 0)
    
    def set_theme(self, theme_id: int):
        """Set theme"""
        self.course_data['theme'] = theme_id
    
    def export_json(self, filepath: Path):
        """Export course data as readable JSON for debugging"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.course_data, f, indent=2)