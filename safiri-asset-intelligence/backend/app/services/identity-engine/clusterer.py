"""
Identity Clusterer - Groups similar identities into clusters
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
import statistics

class IdentityClusterer:
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold

    def cluster_identities(self, candidates: List[Dict], similarity_matrix: np.ndarray) -> List[List[Dict]]:
        """Cluster identities based on similarity scores"""
        if not candidates:
            return []

        n = len(candidates)

        # Create adjacency list for connected components
        adjacency_list = [[] for _ in range(n)]

        # Add edges where similarity exceeds threshold
        for i in range(n):
            for j in range(i + 1, n):
                if similarity_matrix[i, j] >= self.similarity_threshold:
                    adjacency_list[i].append(j)
                    adjacency_list[j].append(i)

        # Find connected components using DFS
        visited = [False] * n
        clusters = []

        for i in range(n):
            if not visited[i]:
                # Start a new cluster
                cluster_indices = []
                self._dfs(i, adjacency_list, visited, cluster_indices)
                cluster = [candidates[idx] for idx in cluster_indices]
                clusters.append(cluster)

        return clusters

    def _dfs(self, node: int, adjacency_list: List[List[int]], visited: List[bool], cluster: List[int]):
        """Depth-first search to find connected components"""
        visited[node] = True
        cluster.append(node)

        for neighbor in adjacency_list[node]:
            if not visited[neighbor]:
                self._dfs(neighbor, adjacency_list, visited, cluster)

    def merge_clusters(self, clusters: List[List[Dict]]) -> List[Dict]:
        """Merge each cluster into a single representative identity"""
        merged_identities = []

        for cluster in clusters:
            if not cluster:
                continue

            if len(cluster) == 1:
                # Single identity, no merging needed
                merged_identities.append(cluster[0])
                continue

            # Merge multiple identities
            merged = self._merge_identity_cluster(cluster)
            merged_identities.append(merged)

        return merged_identities

    def _merge_identity_cluster(self, cluster: List[Dict]) -> Dict:
        """Merge a cluster of similar identities into one"""
        if not cluster:
            return {}

        if len(cluster) == 1:
            return cluster[0]

        # Start with the first identity as base
        merged = cluster[0].copy()

        # Collect all names, addresses, identifiers
        all_names = set()
        all_addresses = set()
        all_identifiers = set()
        all_assets = set()

        for identity in cluster:
            # Collect names
            if 'name' in identity and identity['name']:
                all_names.add(identity['name'])
            if 'aliases' in identity and identity['aliases']:
                all_names.update(identity['aliases'])

            # Collect addresses
            if 'address' in identity and identity['address']:
                all_addresses.add(identity['address'])

            # Collect identifiers
            if 'identifiers' in identity and identity['identifiers']:
                all_identifiers.update(identity['identifiers'])

            # Collect assets
            if 'assets' in identity and identity['assets']:
                all_assets.update(identity['assets'])

        # Update merged identity
        merged['aliases'] = list(all_names - {merged.get('name')})
        merged['all_addresses'] = list(all_addresses)
        merged['all_identifiers'] = list(all_identifiers)
        merged['all_assets'] = list(all_assets)
        merged['cluster_size'] = len(cluster)
        merged['confidence_score'] = self._calculate_cluster_confidence(cluster)

        # Set primary name (most common or first)
        if all_names:
            merged['name'] = max(all_names, key=lambda x: len(x))  # Longest name as primary

        # Set primary address
        if all_addresses:
            merged['address'] = list(all_addresses)[0]  # First address as primary

        return merged

    def _calculate_cluster_confidence(self, cluster: List[Dict]) -> float:
        """Calculate confidence score for a merged cluster"""
        if len(cluster) <= 1:
            return 1.0

        # Simple confidence based on cluster size and consistency
        # Larger clusters with consistent data get higher confidence
        base_confidence = min(0.9, 0.5 + (len(cluster) - 1) * 0.1)

        # Check name consistency
        names = set()
        for identity in cluster:
            if 'name' in identity and identity['name']:
                names.add(identity['name'])

        name_consistency = 1.0 if len(names) == 1 else 0.8 / len(names)

        return base_confidence * name_consistency

    def find_cluster_representative(self, cluster: List[Dict]) -> Dict:
        """Find the most representative identity in a cluster"""
        if not cluster:
            return {}

        if len(cluster) == 1:
            return cluster[0]

        # Score each identity based on completeness and centrality
        scores = []
        for identity in cluster:
            score = self._score_identity_completeness(identity)
            scores.append(score)

        # Return identity with highest score
        best_idx = scores.index(max(scores))
        return cluster[best_idx]

    def _score_identity_completeness(self, identity: Dict) -> float:
        """Score identity based on how complete the information is"""
        score = 0.0

        # Name completeness
        if identity.get('name'):
            score += 0.3

        # Address completeness
        if identity.get('address'):
            score += 0.2

        # Identifier completeness
        if identity.get('identifiers') and len(identity['identifiers']) > 0:
            score += 0.3

        # Asset information
        if identity.get('assets') and len(identity['assets']) > 0:
            score += 0.2

        return score

    def detect_outliers(self, cluster: List[Dict], similarity_matrix: np.ndarray) -> List[int]:
        """Detect outlier identities in a cluster that might not belong"""
        if len(cluster) <= 2:
            return []  # Too small to have outliers

        # Calculate average similarity for each identity
        avg_similarities = []
        indices = list(range(len(cluster)))

        for i in indices:
            similarities = [similarity_matrix[i, j] for j in indices if j != i]
            avg_sim = statistics.mean(similarities) if similarities else 0.0
            avg_similarities.append(avg_sim)

        # Find outliers (identities with low average similarity)
        if avg_similarities:
            mean_sim = statistics.mean(avg_similarities)
            std_sim = statistics.stdev(avg_similarities) if len(avg_similarities) > 1 else 0.0
            threshold = mean_sim - std_sim
        else:
            threshold = 0.0
        outliers = [i for i, sim in enumerate(avg_similarities) if sim < threshold]

        return outliers

    def split_cluster(self, cluster: List[Dict], similarity_matrix: np.ndarray) -> List[List[Dict]]:
        """Split a cluster if it contains distinct subgroups"""
        if len(cluster) <= 3:
            return [cluster]  # Too small to split

        # Simple clustering based on similarity threshold
        # Group identities that are highly similar to each other
        subgroups = defaultdict(list)
        processed = set()

        for i in range(len(cluster)):
            if i in processed:
                continue

            # Start a new subgroup
            subgroup = [cluster[i]]
            processed.add(i)

            # Find all identities similar to this one
            for j in range(len(cluster)):
                if j not in processed and similarity_matrix[i, j] >= self.similarity_threshold:
                    subgroup.append(cluster[j])
                    processed.add(j)

            # Only create subgroup if it has more than one member
            if len(subgroup) > 1:
                subgroups[len(subgroups)].extend(subgroup)
            else:
                # Single identity - put in its own group
                subgroups[len(subgroups)].extend(subgroup)

        return list(subgroups.values())

# Global instance
identity_clusterer = IdentityClusterer()