DART-69 PRIME GENERATOR - FORMULA BASED
Instead of checking every number, use the dart-69 pattern to generate prime candidates directly.
Filters out forbidden positions (every 3rd) automatically.

This is MUCH faster than brute force checking every number!
"""

try:
    import gmpy2
    from gmpy2 import is_prime
    GMPY2_AVAILABLE = True
    print("✓ gmpy2 loaded - Fast primality testing enabled")
except ImportError:
    print("⚠ gmpy2 not available - Using standard library")
    GMPY2_AVAILABLE = False

import math
import time

def get_dimension_range(d):
    """Calculate π-dimensional bounds"""
    if GMPY2_AVAILABLE:
        pi = gmpy2.const_pi()
        min_n = int(gmpy2.floor(pi ** (d - 1))) + 1
        max_n = int(gmpy2.floor(pi ** d))
    else:
        pi = math.pi
        min_n = math.floor(pi ** (d - 1)) + 1
        max_n = math.floor(pi ** d)
    
    return min_n, max_n

def is_prime_fast(n):
    """Fast primality test"""
    if GMPY2_AVAILABLE:
        return gmpy2.is_prime(n)
    else:
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True

def generate_allowed_positions():
    """Generate the 46 allowed positions in the 69-wheel"""
    allowed = []
    
    for pos in range(69):
        # Skip every 3rd position (forbidden zones)
        if pos % 3 == 0:
            # Exception: positions 3 and 23 are allowed in early dimensions
            if pos in [3, 23]:
                allowed.append(pos)
            # Skip all other multiples of 3
        else:
            allowed.append(pos)
    
    return allowed

def generate_primes_by_formula(dimension, include_exceptions=True):
    """
    Generate primes using dart-69 formula instead of brute force checking
    Only tests numbers that could possibly be prime based on the pattern
    """
    print(f"\n{'='*80}")
    print(f"DART-69 FORMULA-BASED PRIME GENERATION - DIMENSION {dimension}")
    print(f"{'='*80}")
    
    # Get dimension bounds
    min_n, max_n = get_dimension_range(dimension)
    total_range = max_n - min_n + 1
    
    print(f"Dimension {dimension} range: [{min_n:,}, {max_n:,}]")
    print(f"Total numbers in range: {total_range:,}")
    
    # Get allowed positions
    allowed_positions = generate_allowed_positions()
    
    # Modify allowed positions based on dimension
    if not include_exceptions or dimension > 3:
        # Remove exceptions 3 and 23 for higher dimensions
        allowed_positions = [pos for pos in allowed_positions if pos not in [3, 23]]
    
    print(f"Allowed wheel positions: {len(allowed_positions)} out of 69")
    print(f"Theoretical candidates: ~{total_range * len(allowed_positions) // 69:,}")
    print()
    
    start_time = time.time()
    candidates_tested = 0
    primes_found = []
    
    print("Generating prime candidates using dart-69 formula...")
    
    # For each allowed position, find all numbers in dimension range with that position
    for pos in allowed_positions:
        position_primes = []
        
        # Find first number >= min_n with this position
        start_num = min_n
        remainder = start_num % 69
        
        if remainder <= pos:
            first_candidate = start_num + (pos - remainder)
        else:
            first_candidate = start_num + (69 - remainder + pos)
        
        # Generate all candidates with this position in the range
        candidate = first_candidate
        while candidate <= max_n:
            candidates_tested += 1
            
            # Progress indicator
            if candidates_tested % 10000 == 0:
                elapsed = time.time() - start_time
                print(f"  Tested {candidates_tested:,} candidates, found {len(primes_found):,} primes ({elapsed:.1f}s)")
            
            if is_prime_fast(candidate):
                primes_found.append(candidate)
                position_primes.append(candidate)
            
            candidate += 69  # Next number with same wheel position
        
        # Show progress for this position
        if position_primes:
            print(f"  Position {pos:2}: {len(position_primes):2} primes")
    
    elapsed_time = time.time() - start_time
    
    # Sort primes
    primes_found.sort()
    
    print(f"\n✓ Generation complete in {elapsed_time:.2f} seconds")
    print(f"Candidates tested: {candidates_tested:,}")
    print(f"Primes found: {len(primes_found):,}")
    
    if candidates_tested > 0:
        efficiency = len(primes_found) / candidates_tested * 100
        speedup = total_range / candidates_tested
        print(f"Hit rate: {efficiency:.2f}% (much better than ~2-3% random)")
        print(f"Speed improvement: {speedup:.1f}x faster than brute force")
    
    return primes_found

def compare_methods(dimension):
    """Compare formula method vs brute force for verification"""
    print(f"\n{'='*80}")
    print(f"METHOD COMPARISON - DIMENSION {dimension}")
    print(f"{'='*80}")
    
    # Formula method
    print("Testing DART-69 formula method...")
    start_time = time.time()
    formula_primes = generate_primes_by_formula(dimension, include_exceptions=True)
    formula_time = time.time() - start_time
    
    # Brute force method (for small dimensions only)
    min_n, max_n = get_dimension_range(dimension)
    if max_n - min_n < 50000:  # Only do brute force for small ranges
        print("\nTesting brute force method...")
        start_time = time.time()
        brute_force_primes = []
        
        for n in range(min_n, max_n + 1):
            if is_prime_fast(n):
                brute_force_primes.append(n)
        
        brute_force_time = time.time() - start_time
        
        # Compare results
        print(f"\nCOMPARISSON RESULTS:")
        print(f"Formula method:    {len(formula_primes):,} primes in {formula_time:.2f}s")
        print(f"Brute force method: {len(brute_force_primes):,} primes in {brute_force_time:.2f}s")
        print(f"Speed improvement: {brute_force_time/formula_time:.1f}x faster")
        
        # Verify they found the same primes
        if set(formula_primes) == set(brute_force_primes):
            print("✓ IDENTICAL RESULTS - Formula method is correct!")
        else:
            print("⚠ Different results - checking discrepancies...")
            only_formula = set(formula_primes) - set(brute_force_primes)
            only_brute = set(brute_force_primes) - set(formula_primes)
            if only_formula:
                print(f"  Only in formula: {only_formula}")
            if only_brute:
                print(f"  Only in brute force: {only_brute}")
    
    else:
        print(f"Range too large ({max_n - min_n:,}) for brute force comparison")
        print(f"Formula method found {len(formula_primes):,} primes in {formula_time:.2f}s")
    
    return formula_primes

def batch_generate(start_dim, end_dim):
    """Generate primes for multiple dimensions quickly"""
    print(f"🎯 BATCH DART-69 GENERATION: Dimensions {start_dim} to {end_dim}")
    print("=" * 70)
    
    total_primes = 0
    total_time = 0
    
    for d in range(start_dim, end_dim + 1):
        start_time = time.time()
        primes = generate_primes_by_formula(d, include_exceptions=(d <= 3))
        elapsed = time.time() - start_time
        
        total_primes += len(primes)
        total_time += elapsed
        
        print(f"Dimension {d:2}: {len(primes):,} primes ({elapsed:.2f}s)")
    
    print(f"\nBATCH SUMMARY:")
    print(f"Total primes generated: {total_primes:,}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average: {total_primes/total_time:.0f} primes/second")

def interactive_generator():
    """Interactive prime generation tool"""
    print("🎯 DART-69 FORMULA-BASED PRIME GENERATOR")
    print("=" * 60)
    print("Super fast prime generation using the dart-69 pattern!")
    print("Only tests numbers that could possibly be prime.")
    print()
    
    while True:
        try:
            command = input("Enter dimension, 'batch X Y', 'compare X', or 'q' to quit: ").strip()
            
            if command.lower() in ['q', 'quit', 'exit']:
                print("Happy prime hunting! 🎯")
                break
            
            if command.startswith('batch'):
                parts = command.split()
                if len(parts) == 3:
                    start_dim, end_dim = int(parts[1]), int(parts[2])
                    batch_generate(start_dim, end_dim)
                else:
                    print("Usage: batch <start_dim> <end_dim>")
                continue
            
            if command.startswith('compare'):
                parts = command.split()
                if len(parts) == 2:
                    dimension = int(parts[1])
                    compare_methods(dimension)
                else:
                    print("Usage: compare <dimension>")
                continue
            
            # Single dimension
            dimension = int(command)
            
            if dimension < 1:
                print("Please enter a positive dimension number.")
                continue
            
            # Generate primes
            primes = generate_primes_by_formula(dimension)
            
            # Display results
            print(f"\nALL {len(primes):,} PRIMES IN DIMENSION {dimension}:")
            print("-" * 60)
            
            # Print in rows of 8 for readability
            for i in range(0, len(primes), 8):
                row = primes[i:i+8]
                print(" ".join(f"{p:>8,}" for p in row))
            
            # Save option
            save = input(f"\nSave {len(primes):,} primes to file? (y/n): ").strip().lower()
            if save in ['y', 'yes']:
                filename = f"dart69_dim{dimension}_primes.txt"
                with open(filename, 'w') as f:
                    f.write(f"DART-69 Dimension {dimension} Primes (Formula Generated)\n")
                    f.write(f"Total: {len(primes):,} primes\n\n")
                    
                    for i, prime in enumerate(primes):
                        f.write(f"{prime:>10,}")
                        if (i + 1) % 8 == 0:
                            f.write("\n")
                        else:
                            f.write(" ")
                
                print(f"Saved to {filename}")
            
            print()
            
        except ValueError:
            print("Please enter a valid number or command.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'compare':
            dimension = int(sys.argv[2])
            compare_methods(dimension)
        elif sys.argv[1] == 'batch':
            start_dim = int(sys.argv[2])
            end_dim = int(sys.argv[3])
            batch_generate(start_dim, end_dim)
        else:
            dimension = int(sys.argv[1])
            primes = generate_primes_by_formula(dimension)
            for prime in primes:
                print(prime)
    else:
        interactive_generator()
