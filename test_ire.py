#!/usr/bin/env python3
"""
Test script for Identity Resolution Engine (IRE)
"""

import sys
import os

# Add the backend path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all IRE modules can be imported"""
    try:
        from app.services.identity_engine.engine import identity_resolution_engine
        from app.services.identity_engine.matcher import identity_matcher
        from app.services.identity_engine.clusterer import identity_clusterer
        print("✓ All IRE modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_matcher():
    """Test the identity matcher"""
    try:
        from app.services.identity_engine.matcher import identity_matcher

        # Test name matching
        result = identity_matcher.match_names("John Doe", "John Doe")
        assert result['score'] == 1.0, "Exact name match should score 1.0"

        result = identity_matcher.match_names("John Doe", "Jane Doe")
        assert result['score'] < 1.0, "Different names should score less than 1.0"

        # Test address matching
        result = identity_matcher.match_addresses("123 Main St", "123 Main St")
        assert result['score'] == 1.0, "Exact address match should score 1.0"

        print("✓ Identity matcher tests passed")
        return True
    except Exception as e:
        print(f"✗ Matcher test failed: {e}")
        return False

def test_clusterer():
    """Test the identity clusterer"""
    try:
        from app.services.identity_engine.clusterer import identity_clusterer
        import numpy as np

        # Create test data
        identities = [
            {'name': 'John Doe', 'id': 1},
            {'name': 'John Doe', 'id': 2},  # Similar to first
            {'name': 'Jane Smith', 'id': 3}  # Different
        ]

        # Create similarity matrix (1.0 for identical, 0.0 for different)
        similarity_matrix = np.array([
            [1.0, 0.9, 0.0],
            [0.9, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])

        clusters = identity_clusterer.cluster_identities(identities, similarity_matrix)
        assert len(clusters) >= 1, "Should create at least one cluster"

        print("✓ Identity clusterer tests passed")
        return True
    except Exception as e:
        print(f"✗ Clusterer test failed: {e}")
        return False

def test_engine():
    """Test the main IRE engine"""
    try:
        from app.services.identity_engine.engine import identity_resolution_engine

        # Test basic functionality
        assert hasattr(identity_resolution_engine, 'resolve_identity'), "Engine should have resolve_identity method"
        assert hasattr(identity_resolution_engine, 'resolve_identity_async'), "Engine should have async methods"

        print("✓ Identity resolution engine tests passed")
        return True
    except Exception as e:
        print(f"✗ Engine test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Identity Resolution Engine (IRE) Implementation")
    print("=" * 50)

    tests = [
        test_imports,
        test_matcher,
        test_clusterer,
        test_engine
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All IRE tests passed! The implementation is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())