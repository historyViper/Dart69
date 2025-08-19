#!/usr/bin/env python3
"""
Trinity Sector Grouping Analysis
===============================

Test if Trinity sectors group into triplets/multiplets that sum to ~4.2%
and explain the observed angular preferences at 150°, 330°, 225°.

This bridges the gap between:
- Trinity micro-quantum: 1.4% per sector  
- Observed macro-pattern: 4.2% groupings
"""

import math
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple
import itertools

def sieve_of_eratosthenes(n: int) -> List[int]:
    """Generate all primes up to n using Sieve of Eratosthenes"""
    if n < 2:
        return []
    
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    
    return [i for i in range(2, n + 1) if sieve[i]]

class TrinityGroupingAnalyzer:
    def __init__(self, max_n: int = 1000000):
        """Initialize with precomputed primes"""
        self.max_n = max_n
        print(f"Generating primes up to {max_n:,}...")
        self.primes = sieve_of_eratosthenes(max_n)
        print(f"Generated {len(self.primes):,} primes for Trinity grouping analysis")
        
        # Trinity frequencies
        self.trinity_frequencies = {
            '69': {'freq': 69, 'angular_quantum': 360/69, 'sectors': 69},
            '71': {'freq': 71, 'angular_quantum': 360/71, 'sectors': 71}, 
            '138.5': {'freq': 138.5, 'angular_quantum': 360/138.5, 'sectors': int(138.5)}
        }
        
        # Target angular preferences from papers
        self.target_angles = [150, 330, 225]  # High-consistency sectors
        
    def analyze_trinity_groupings(self, dimensions: List[int] = [7, 8, 9, 10, 11, 12]) -> Dict:
        """Analyze Trinity sector groupings for 4.2% pattern"""
        print("TRINITY SECTOR GROUPING ANALYSIS")
        print("=" * 50)
        
        results = {}
        
        for trinity_name, trinity_info in self.trinity_frequencies.items():
            print(f"\nAnalyzing Trinity-{trinity_name} groupings...")
            
            angular_quantum = trinity_info['angular_quantum']
            num_sectors = trinity_info['sectors']
            
            trinity_results = {
                'trinity_name': trinity_name,
                'angular_quantum': angular_quantum,
                'num_sectors': num_sectors,
                'dimensions_analyzed': {},
                'grouping_patterns': {},
                'target_angle_mappings': {}
            }
            
            # Analyze each dimension
            for dim in dimensions:
                dim_result = self._analyze_dimension_groupings(dim, trinity_name, trinity_info)
                if dim_result:
                    trinity_results['dimensions_analyzed'][dim] = dim_result
            
            # Find consistent grouping patterns across dimensions
            trinity_results['grouping_patterns'] = self._find_grouping_patterns(trinity_results['dimensions_analyzed'])
            
            # Map target angles to Trinity sectors
            trinity_results['target_angle_mappings'] = self._map_target_angles_to_trinity(trinity_info)
            
            results[trinity_name] = trinity_results
        
        return results
    
    def _analyze_dimension_groupings(self, dim: int, trinity_name: str, trinity_info: Dict) -> Dict:
        """Analyze Trinity sector groupings for a specific dimension"""
        # Calculate dimension boundaries
        start = math.floor(math.pi ** (dim-1)) + 1 if dim > 1 else 1
        end = math.floor(math.pi ** dim)
        
        # Find primes in this dimension
        primes_in_dim = [p for p in self.primes if start <= p <= end and p <= self.max_n]
        
        if len(primes_in_dim) == 0:
            return None
            
        angular_quantum = trinity_info['angular_quantum']
        num_sectors = trinity_info['sectors']
        
        # Calculate Trinity sector densities
        sector_counts = [0] * num_sectors
        
        for p in primes_in_dim:
            relative_pos = (p - start) / (end - start)
            angle = relative_pos * 2 * math.pi
            angle_degrees = (angle * 180 / math.pi) % 360
            sector = min(int(angle_degrees / angular_quantum), num_sectors - 1)
            sector_counts[sector] += 1
        
        total_primes = len(primes_in_dim)
        sector_densities = [(count / total_primes * 100) for count in sector_counts]
        
        # Test different grouping sizes
        grouping_results = {}
        
        for group_size in [2, 3, 4, 5]:
            groups_near_4_2 = []
            
            # Test all possible consecutive groupings of this size
            for start_sector in range(num_sectors):
                group_sectors = [(start_sector + i) % num_sectors for i in range(group_size)]
                group_density = sum(sector_densities[s] for s in group_sectors)
                
                # Check if this grouping is near 4.2%
                if abs(group_density - 4.2) < 0.5:  # Within 0.5% of 4.2%
                    groups_near_4_2.append({
                        'sectors': group_sectors,
                        'density': group_density,
                        'angle_range': f"{group_sectors[0] * angular_quantum:.1f}°-{((group_sectors[-1] + 1) % num_sectors) * angular_quantum:.1f}°",
                        'center_angle': (sum(s * angular_quantum for s in group_sectors) / group_size) % 360
                    })
            
            grouping_results[group_size] = {
                'count': len(groups_near_4_2),
                'groups': groups_near_4_2,
                'percentage': (len(groups_near_4_2) / (num_sectors / group_size)) * 100 if num_sectors > 0 else 0
            }
        
        return {
            'dimension': dim,
            'total_primes': total_primes,
            'range': [start, end],
            'sector_densities': sector_densities,
            'grouping_results': grouping_results,
            'individual_sector_stats': {
                'mean': np.mean(sector_densities),
                'std': np.std(sector_densities),
                'max': max(sector_densities),
                'min': min(sector_densities)
            }
        }
    
    def _find_grouping_patterns(self, dimensions_data: Dict) -> Dict:
        """Find consistent grouping patterns across dimensions"""
        patterns = {}
        
        if not dimensions_data:
            return patterns
        
        # Get all group sizes tested
        sample_dim = next(iter(dimensions_data.values()))
        group_sizes = sample_dim['grouping_results'].keys()
        
        for group_size in group_sizes:
            pattern_data = {
                'group_size': group_size,
                'avg_groups_per_dim': 0,
                'consistency_score': 0,
                'best_dimensions': [],
                'cross_dim_analysis': {}
            }
            
            # Collect data across dimensions
            counts_per_dim = []
            percentages_per_dim = []
            
            for dim, data in dimensions_data.items():
                if group_size in data['grouping_results']:
                    count = data['grouping_results'][group_size]['count']
                    percentage = data['grouping_results'][group_size]['percentage']
                    counts_per_dim.append(count)
                    percentages_per_dim.append(percentage)
                    
                    pattern_data['cross_dim_analysis'][dim] = {
                        'count': count,
                        'percentage': percentage,
                        'groups': data['grouping_results'][group_size]['groups']
                    }
            
            if counts_per_dim:
                pattern_data['avg_groups_per_dim'] = np.mean(counts_per_dim)
                pattern_data['consistency_score'] = 1 - (np.std(percentages_per_dim) / np.mean(percentages_per_dim)) if np.mean(percentages_per_dim) > 0 else 0
                pattern_data['best_dimensions'] = [dim for dim, count in zip(dimensions_data.keys(), counts_per_dim) if count >= np.mean(counts_per_dim)]
            
            patterns[group_size] = pattern_data
        
        return patterns
    
    def _map_target_angles_to_trinity(self, trinity_info: Dict) -> Dict:
        """Map target angles (150°, 330°, 225°) to Trinity sectors"""
        angular_quantum = trinity_info['angular_quantum']
        mappings = {}
        
        for target_angle in self.target_angles:
            # Find which Trinity sector contains this angle
            trinity_sector = int(target_angle / angular_quantum)
            sector_start_angle = trinity_sector * angular_quantum
            sector_end_angle = (trinity_sector + 1) * angular_quantum
            
            mappings[target_angle] = {
                'trinity_sector': trinity_sector,
                'sector_angle_range': f"{sector_start_angle:.1f}°-{sector_end_angle:.1f}°",
                'angle_within_sector': target_angle - sector_start_angle,
                'sector_coverage': (target_angle - sector_start_angle) / angular_quantum
            }
        
        return mappings
    
    def find_optimal_trinity_groupings(self, results: Dict) -> Dict:
        """Find the optimal Trinity frequency and grouping size for 4.2% pattern"""
        print("\nFINDING OPTIMAL TRINITY GROUPINGS FOR 4.2% PATTERN")
        print("=" * 55)
        
        optimal_analysis = {}
        
        for trinity_name, trinity_data in results.items():
            if 'grouping_patterns' not in trinity_data:
                continue
                
            best_group_size = None
            best_score = 0
            
            print(f"\nTrinity-{trinity_name} analysis:")
            
            for group_size, pattern in trinity_data['grouping_patterns'].items():
                if pattern['avg_groups_per_dim'] > 0:
                    # Score based on consistency and number of groups found
                    score = pattern['consistency_score'] * pattern['avg_groups_per_dim']
                    
                    print(f"  Group size {group_size}: {pattern['avg_groups_per_dim']:.1f} groups/dim, consistency: {pattern['consistency_score']:.3f}")
                    
                    if score > best_score:
                        best_score = score
                        best_group_size = group_size
            
            optimal_analysis[trinity_name] = {
                'best_group_size': best_group_size,
                'best_score': best_score,
                'target_angle_mappings': trinity_data['target_angle_mappings']
            }
            
            if best_group_size:
                print(f"  → Best grouping: {best_group_size} sectors (score: {best_score:.3f})")
                
                # Show some example groups from best dimensions
                pattern = trinity_data['grouping_patterns'][best_group_size]
                for dim in pattern['best_dimensions'][:2]:  # Show top 2 dimensions
                    if dim in pattern['cross_dim_analysis']:
                        groups = pattern['cross_dim_analysis'][dim]['groups'][:3]  # Show top 3 groups
                        examples = [f'{g["density"]:.2f}% at {g["center_angle"]:.0f}°' for g in groups]
                        print(f"    D{dim} examples: {examples}")
        
        # Determine overall best Trinity frequency
        best_trinity = max(optimal_analysis.keys(), 
                          key=lambda k: optimal_analysis[k]['best_score'] if optimal_analysis[k]['best_score'] else 0)
        
        print(f"\n🎯 OPTIMAL TRINITY FREQUENCY: {best_trinity}")
        print(f"   Best group size: {optimal_analysis[best_trinity]['best_group_size']}")
        print(f"   Score: {optimal_analysis[best_trinity]['best_score']:.3f}")
        
        return optimal_analysis
    
    def analyze_target_angle_coverage(self, results: Dict, optimal_analysis: Dict) -> Dict:
        """Analyze how well Trinity groupings explain target angles (150°, 330°, 225°)"""
        print(f"\nTARGET ANGLE COVERAGE ANALYSIS")
        print("=" * 35)
        
        coverage_analysis = {}
        
        for trinity_name, trinity_data in results.items():
            print(f"\nTrinity-{trinity_name} coverage of target angles:")
            
            mappings = trinity_data['target_angle_mappings']
            angular_quantum = self.trinity_frequencies[trinity_name]['angular_quantum']
            
            coverage_data = {
                'trinity_name': trinity_name,
                'angular_quantum': angular_quantum,
                'angle_coverage': {}
            }
            
            for target_angle, mapping in mappings.items():
                print(f"  {target_angle}° → Trinity sector {mapping['trinity_sector']}")
                print(f"    Sector range: {mapping['sector_angle_range']}")
                print(f"    Coverage: {mapping['sector_coverage']:.1%} within sector")
                
                coverage_data['angle_coverage'][target_angle] = mapping
            
            # Check if optimal groupings contain target angles
            if trinity_name in optimal_analysis and optimal_analysis[trinity_name]['best_group_size']:
                best_group_size = optimal_analysis[trinity_name]['best_group_size']
                print(f"  Optimal grouping size: {best_group_size} sectors")
                
                # Test if target angles would be captured by groupings
                target_coverage_score = 0
                for target_angle in self.target_angles:
                    target_sector = int(target_angle / angular_quantum)
                    # Check how many possible groupings would include this sector
                    possible_groups = 0
                    num_sectors = self.trinity_frequencies[trinity_name]['sectors']
                    for start_sector in range(max(0, target_sector - best_group_size + 1), 
                                            min(num_sectors, target_sector + 1)):
                        if start_sector + best_group_size <= num_sectors:
                            possible_groups += 1
                    
                    coverage_ratio = possible_groups / num_sectors
                    target_coverage_score += coverage_ratio
                    print(f"    {target_angle}° grouping coverage: {coverage_ratio:.1%}")
                
                coverage_data['target_coverage_score'] = target_coverage_score / len(self.target_angles)
                print(f"  Overall target coverage: {coverage_data['target_coverage_score']:.1%}")
            
            coverage_analysis[trinity_name] = coverage_data
        
        return coverage_analysis

def run_trinity_grouping_analysis():
    """Main function to run complete Trinity grouping analysis"""
    print("TRINITY SECTOR GROUPING ANALYSIS")
    print("=" * 40)
    print("Testing if Trinity sectors group into multiplets that sum to ~4.2%")
    print("and explain angular preferences at 150°, 330°, 225°")
    print()
    
    analyzer = TrinityGroupingAnalyzer(max_n=1000000)
    
    # Step 1: Analyze Trinity groupings
    results = analyzer.analyze_trinity_groupings()
    
    # Step 2: Find optimal groupings
    optimal_analysis = analyzer.find_optimal_trinity_groupings(results)
    
    # Step 3: Analyze target angle coverage
    coverage_analysis = analyzer.analyze_target_angle_coverage(results, optimal_analysis)
    
    # Step 4: Summary and conclusions
    print(f"\n" + "=" * 60)
    print("TRINITY GROUPING CONCLUSIONS")
    print("=" * 60)
    
    # Find best overall Trinity frequency
    best_trinity = max(optimal_analysis.keys(), 
                      key=lambda k: optimal_analysis[k]['best_score'] if optimal_analysis[k]['best_score'] else 0)
    
    print(f"\n🎯 BEST TRINITY FREQUENCY FOR 4.2% PATTERN:")
    print(f"   Trinity-{best_trinity}")
    print(f"   Angular quantum: {analyzer.trinity_frequencies[best_trinity]['angular_quantum']:.3f}° per sector")
    print(f"   Optimal group size: {optimal_analysis[best_trinity]['best_group_size']} sectors")
    print(f"   Expected group density: {analyzer.trinity_frequencies[best_trinity]['angular_quantum'] * optimal_analysis[best_trinity]['best_group_size'] / 360 * 100:.2f}%")
    
    print(f"\n📐 TARGET ANGLE EXPLANATION:")
    for target_angle in analyzer.target_angles:
        trinity_sector = int(target_angle / analyzer.trinity_frequencies[best_trinity]['angular_quantum'])
        print(f"   {target_angle}° → Trinity-{best_trinity} sector {trinity_sector}")
    
    print(f"\n🔗 BRIDGING THE GAP:")
    individual_density = 100 / analyzer.trinity_frequencies[best_trinity]['sectors']
    group_density = individual_density * optimal_analysis[best_trinity]['best_group_size']
    print(f"   Individual Trinity-{best_trinity} sector: {individual_density:.3f}%")
    print(f"   {optimal_analysis[best_trinity]['best_group_size']}-sector grouping: {group_density:.3f}%")
    print(f"   JavaScript observed: 4.2%")
    print(f"   Match quality: {abs(group_density - 4.2) < 0.5}")
    
    return results, optimal_analysis, coverage_analysis

if __name__ == "__main__":
    results, optimal_analysis, coverage_analysis = run_trinity_grouping_analysis()
