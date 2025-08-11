#!/usr/bin/env python3
"""
DART-69 High-Performance Prime Sieve
Professional implementation with gmpy2 optimization
"""

import math
import time
import argparse
import sys
from typing import List, Tuple, Optional

try:
    import gmpy2
    HAS_GMPY2 = True
    print("🚀 Using gmpy2 for maximum performance")
except ImportError:
    HAS_GMPY2 = False
    print("⚠️  gmpy2 not found - install with: pip install gmpy2")

class DART69Sieve:
    """Ultra-fast DART-69 prime sieve with gmpy2 optimization."""
    
    def __init__(self, use_gmpy2: bool = True):
        self.use_gmpy2 = use_gmpy2 and HAS_GMPY2
        self.stats = {}
        
    def get_dimension_range(self, dimension: int) -> Tuple[int, int]:
        """Get start and end for π-dimension."""
        if dimension == 1:
            return 2, 3
        
        if self.use_gmpy2:
            pi = gmpy2.const_pi()
            start = int(gmpy2.floor(pi ** (dimension - 1))) + 1
            end = int(gmpy2.floor(pi ** dimension))
        else:
            start = math.floor(math.pi ** (dimension - 1)) + 1
            end = math.floor(math.pi ** dimension)
        
        return start, end
    
    def dart69_filter(self, n: int) -> bool:
        """DART-69 angular + digit filtering."""
        # Angular filter
        sector = n % 69
        if (sector % 3 == 0 or sector % 23 == 0) and n not in (3, 23):
            return False
        
        # Digit filter
        return n % 10 in (1, 3, 7, 9)
    
    def is_prime_gmpy2(self, n: int) -> bool:
        """Ultra-fast primality test using gmpy2."""
        if n < 2:
            return False
        return gmpy2.is_prime(n) != 0
    
    def is_prime_basic(self, n: int) -> bool:
        """Optimized trial division primality test."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        if n < 9:
            return True
        if n % 3 == 0:
            return False
        
        # 6k±1 optimization
        limit = int(math.sqrt(n)) + 1
        for i in range(5, limit, 6):
            if n % i == 0 or n % (i + 2) == 0:
                return False
        return True
    
    def is_prime(self, n: int) -> bool:
        """Choose best primality test based on available libraries."""
        if self.use_gmpy2:
            return self.is_prime_gmpy2(n)
        else:
            return self.is_prime_basic(n)
    
    def sieve_dimension(self, dimension: int, show_progress: bool = True, 
                       chunk_size: int = 1000000) -> List[int]:
        """
        Sieve a complete π-dimension for primes.
        
        Args:
            dimension: π-dimension to sieve
            show_progress: Show progress updates
            chunk_size: Numbers to process per progress update
        
        Returns:
            List of all primes in the dimension
        """
        start_time = time.perf_counter()
        start_num, end_num = self.get_dimension_range(dimension)
        total_numbers = end_num - start_num + 1
        
        if show_progress:
            print(f"\n🎯 DART-69 Sieve D{dimension}")
            print(f"Range: {start_num:,} to {end_num:,} ({total_numbers:,} numbers)")
            print(f"Engine: {'gmpy2' if self.use_gmpy2 else 'pure Python'}")
            print("-" * 60)
        
        primes = []
        processed = 0
        candidates_tested = 0
        last_progress_time = start_time
        
        for n in range(start_num, end_num + 1):
            processed += 1
            
            # Apply DART-69 filters
            if self.dart69_filter(n):
                candidates_tested += 1
                
                # Prime test
                if self.is_prime(n):
                    primes.append(n)
            
            # Progress updates
            if show_progress and processed % chunk_size == 0:
                current_time = time.perf_counter()
                elapsed = current_time - start_time
                chunk_elapsed = current_time - last_progress_time
                
                progress = (processed / total_numbers) * 100
                total_speed = processed / elapsed if elapsed > 0 else 0
                chunk_speed = chunk_size / chunk_elapsed if chunk_elapsed > 0 else 0
                
                eta_seconds = (total_numbers - processed) / total_speed if total_speed > 0 else 0
                eta_min = int(eta_seconds // 60)
                eta_sec = int(eta_seconds % 60)
                
                print(f"Progress: {progress:6.2f}% | "
                      f"Primes: {len(primes):,} | "
                      f"Speed: {chunk_speed:,.0f}/sec | "
                      f"ETA: {eta_min:02d}:{eta_sec:02d}", end='\r')
                
                last_progress_time = current_time
        
        total_time = time.perf_counter() - start_time
        
        # Store statistics
        self.stats = {
            'dimension': dimension,
            'range': (start_num, end_num),
            'total_numbers': total_numbers,
            'candidates_tested': candidates_tested,
            'primes_found': len(primes),
            'processing_time': total_time,
            'numbers_per_second': total_numbers / total_time,
            'primes_per_second': len(primes) / total_time,
            'elimination_rate': ((total_numbers - candidates_tested) / total_numbers) * 100,
            'hit_rate': (len(primes) / candidates_tested * 100) if candidates_tested > 0 else 0
        }
        
        if show_progress:
            print()  # New line after progress
            self.print_stats()
        
        return primes
    
    def print_stats(self):
        """Print detailed performance statistics."""
        s = self.stats
        print(f"\n📊 Results Summary")
        print("-" * 40)
        print(f"Dimension:          D{s['dimension']}")
        print(f"Range:              {s['range'][0]:,} - {s['range'][1]:,}")
        print(f"Total Numbers:      {s['total_numbers']:,}")
        print(f"Candidates Tested:  {s['candidates_tested']:,}")
        print(f"Elimination Rate:   {s['elimination_rate']:.1f}%")
        print(f"Primes Found:       {s['primes_found']:,}")
        print(f"Hit Rate:           {s['hit_rate']:.1f}%")
        print(f"Processing Time:    {s['processing_time']:.2f} seconds")
        print(f"Total Speed:        {s['numbers_per_second']:,.0f} numbers/sec")
        print(f"Prime Generation:   {s['primes_per_second']:,.0f} primes/sec")
        
        # Efficiency comparison
        if s['candidates_tested'] > 0:
            speedup = s['total_numbers'] / s['candidates_tested']
            print(f"DART-69 Speedup:    {speedup:.1f}x vs brute force")
    
    def benchmark_performance(self, max_dimension: int = 12):
        """Run performance benchmark across multiple dimensions."""
        print(f"\n🏁 DART-69 Performance Benchmark")
        print(f"Testing dimensions 5 through {max_dimension}")
        print("=" * 80)
        
        results = []
        for dim in range(5, max_dimension + 1):
            print(f"\nBenchmarking D{dim}...")
            start_time = time.perf_counter()
            
            primes = self.sieve_dimension(dim, show_progress=False)
            
            elapsed = time.perf_counter() - start_time
            start_num, end_num = self.get_dimension_range(dim)
            total_numbers = end_num - start_num + 1
            
            results.append({
                'dimension': dim,
                'total_numbers': total_numbers,
                'primes_found': len(primes),
                'time': elapsed,
                'numbers_per_sec': total_numbers / elapsed,
                'primes_per_sec': len(primes) / elapsed
            })
            
            print(f"D{dim}: {len(primes):,} primes in {elapsed:.2f}s "
                  f"({total_numbers/elapsed:,.0f} numbers/sec)")
        
        # Summary table
        print(f"\n📈 Benchmark Summary")
        print("-" * 80)
        print(f"{'Dim':<4} {'Numbers':<12} {'Primes':<10} {'Time':<8} {'Num/sec':<12} {'Prime/sec':<10}")
        print("-" * 80)
        
        for r in results:
            print(f"D{r['dimension']:<3} {r['total_numbers']:<12,} {r['primes_found']:<10,} "
                  f"{r['time']:<8.2f} {r['numbers_per_sec']:<12,.0f} {r['primes_per_sec']:<10,.0f}")

def main():
    """Command line interface for DART-69 sieve."""
    parser = argparse.ArgumentParser(description='DART-69 High-Performance Prime Sieve')
    parser.add_argument('dimension', type=int, nargs='?', 
                       help='π-dimension to sieve (e.g., 15 for D15)')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run performance benchmark')
    parser.add_argument('--max-dim', type=int, default=12,
                       help='Maximum dimension for benchmark (default: 12)')
    parser.add_argument('--no-gmpy2', action='store_true',
                       help='Disable gmpy2 even if available')
    parser.add_argument('--save', type=str,
                       help='Save primes to file (CSV format)')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output')
    
    args = parser.parse_args()
    
    # Initialize sieve
    sieve = DART69Sieve(use_gmpy2=not args.no_gmpy2)
    
    if args.benchmark:
        sieve.benchmark_performance(args.max_dim)
        return
    
    if args.dimension is None:
        print("🎯 DART-69 Prime Sieve")
        print("Usage examples:")
        print("  python dart69.py 15           # Sieve dimension 15")
        print("  python dart69.py 20 --save primes_d20.csv")
        print("  python dart69.py --benchmark  # Performance test")
        print("  python dart69.py --benchmark --max-dim 15")
        return
    
    # Sieve specified dimension
    dimension = args.dimension
    if dimension < 1:
        print("Error: Dimension must be positive")
        return
    
    if dimension > 25:
        confirm = input(f"D{dimension} will process billions of numbers. Continue? (y/N): ")
        if confirm.lower() != 'y':
            return
    
    print(f"🚀 Starting DART-69 sieve for dimension {dimension}")
    
    primes = sieve.sieve_dimension(dimension, show_progress=not args.quiet)
    
    if not args.quiet:
        print(f"\n🎉 Found {len(primes):,} primes in D{dimension}")
        
        if len(primes) <= 20:
            print(f"Primes: {primes}")
        else:
            print(f"First 10: {primes[:10]}")
            print(f"Last 10:  {primes[-10:]}")
    
    # Save if requested
    if args.save:
        with open(args.save, 'w') as f:
            f.write("prime\n")
            for p in primes:
                f.write(f"{p}\n")
        print(f"💾 Saved {len(primes):,} primes to {args.save}")

if __name__ == "__main__":
    main()
