"""
Analyze Open Food Facts MongoDB Dump

This script analyzes the structure of the OFF MongoDB dump to understand:
- File format and structure
- Collections available
- Sample documents
- Field patterns
- Data quality
- Size estimates for filtered data

Usage:
    python analyze_off_dump.py
"""

import os
import sys
from pathlib import Path
import struct
import json
from collections import defaultdict, Counter
from datetime import datetime

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))


class BSONAnalyzer:
    """Analyze BSON dump file"""
    
    def __init__(self, dump_path: str):
        self.dump_path = Path(dump_path)
        self.file_size = self.dump_path.stat().st_size
        
    def read_bson_document(self, file_handle):
        """Read a single BSON document from file"""
        try:
            # Read document size (first 4 bytes, little-endian int32)
            size_bytes = file_handle.read(4)
            if not size_bytes or len(size_bytes) < 4:
                return None
                
            doc_size = struct.unpack('<i', size_bytes)[0]
            
            # Read rest of document
            remaining = file_handle.read(doc_size - 4)
            if len(remaining) < doc_size - 4:
                return None
            
            # Combine and parse BSON
            bson_data = size_bytes + remaining
            
            # Basic BSON parsing (simplified)
            # We'll return raw data for now since full BSON parsing is complex
            return {'_raw_size': doc_size, '_bson_data': bson_data}
            
        except Exception as e:
            print(f"Error reading BSON: {e}")
            return None
    
    def analyze_structure(self, sample_size: int = 100):
        """Analyze dump structure by sampling documents"""
        print(f"\n{'='*70}")
        print(f"📊 Analyzing Open Food Facts MongoDB Dump")
        print(f"{'='*70}")
        print(f"\n📁 File: {self.dump_path.name}")
        print(f"📦 Size: {self.file_size / 1024 / 1024 / 1024:.2f} GB ({self.file_size:,} bytes)")
        print(f"\n🔍 Sampling first {sample_size} documents...")
        
        doc_sizes = []
        total_docs_sampled = 0
        
        with open(self.dump_path, 'rb') as f:
            while total_docs_sampled < sample_size:
                doc = self.read_bson_document(f)
                if doc is None:
                    break
                    
                doc_sizes.append(doc['_raw_size'])
                total_docs_sampled += 1
                
                if total_docs_sampled % 10 == 0:
                    print(f"   Sampled {total_docs_sampled} documents...")
        
        if doc_sizes:
            avg_size = sum(doc_sizes) / len(doc_sizes)
            estimated_total_docs = int(self.file_size / avg_size)
            
            print(f"\n📈 Analysis Results:")
            print(f"   • Documents sampled: {total_docs_sampled}")
            print(f"   • Average document size: {avg_size:,.0f} bytes ({avg_size/1024:.1f} KB)")
            print(f"   • Min document size: {min(doc_sizes):,} bytes")
            print(f"   • Max document size: {max(doc_sizes):,} bytes")
            print(f"   • Estimated total documents: ~{estimated_total_docs:,}")
            print(f"   • Estimated filtered (10%): ~{estimated_total_docs//10:,} documents")
            print(f"   • Estimated filtered size (10%): ~{self.file_size/10/1024/1024/1024:.2f} GB")
        else:
            print("\n⚠️  Could not read any documents from dump")
        
        return doc_sizes


def check_mongodb_tools():
    """Check if MongoDB tools are available"""
    print(f"\n{'='*70}")
    print(f"🔧 Checking MongoDB Tools")
    print(f"{'='*70}")
    
    tools = ['mongorestore', 'mongodump', 'mongosh']
    available = {}
    
    for tool in tools:
        try:
            import subprocess
            result = subprocess.run([tool, '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                available[tool] = version
                print(f"   ✅ {tool}: {version}")
            else:
                available[tool] = None
                print(f"   ❌ {tool}: Not found")
        except Exception:
            available[tool] = None
            print(f"   ❌ {tool}: Not found")
    
    return available


def get_recommendations(dump_size_gb: float, estimated_docs: int):
    """Provide recommendations based on analysis"""
    print(f"\n{'='*70}")
    print(f"💡 Recommendations")
    print(f"{'='*70}")
    
    print("\n1️⃣  DUMP FORMAT:")
    print("   • This appears to be a raw BSON dump file")
    print("   • Will need MongoDB tools to properly parse and restore")
    print("   • Recommendation: Use mongorestore in MongoDB container")
    
    print("\n2️⃣  DATA VOLUME:")
    if dump_size_gb > 50:
        print(f"   ⚠️  Large dump ({dump_size_gb:.1f} GB) - filtering is ESSENTIAL")
        print("   • Don't restore entire dump to production")
        print("   • Create separate test instance for full restore")
        print("   • Extract only relevant products and taxonomies")
    
    print("\n3️⃣  FILTERING STRATEGY:")
    print("   • Focus on products with images (front, ingredients, or nutrition)")
    print("   • Filter by categories: plant-based foods, beverages, snacks")
    print("   • Prioritize products with French/English names")
    print("   • Target ~10-20% of products (more manageable)")
    
    print("\n4️⃣  NEXT STEPS:")
    print("   a) Start MongoDB container: docker-compose up -d mongodb")
    print("   b) Restore dump to test database")
    print("   c) Analyze collections and schema")
    print("   d) Create filtering script")
    print("   e) Extract filtered data to new database")
    
    print("\n5️⃣  MONGODB TOOLS:")
    print("   • Install in backend container: apt-get install mongodb-database-tools")
    print("   • Or download from: https://www.mongodb.com/try/download/database-tools")


def main():
    """Main analysis function"""
    dump_path = Path(__file__).parent.parent.parent / "data" / "openfoodfacts" / "openfoodfacts-mongodbdump"
    
    if not dump_path.exists():
        print(f"❌ Error: Dump file not found at {dump_path}")
        return
    
    # Check MongoDB tools
    tools = check_mongodb_tools()
    
    # Analyze dump structure
    analyzer = BSONAnalyzer(str(dump_path))
    doc_sizes = analyzer.analyze_structure(sample_size=100)
    
    # Provide recommendations
    if doc_sizes:
        avg_size = sum(doc_sizes) / len(doc_sizes)
        estimated_docs = int(analyzer.file_size / avg_size)
        get_recommendations(analyzer.file_size / 1024**3, estimated_docs)
    
    print(f"\n{'='*70}")
    print("✅ Analysis complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
