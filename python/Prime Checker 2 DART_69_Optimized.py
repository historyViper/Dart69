#!/usr/bin/env python3
"""
DART-69 OPTIMIZED PRIME CHECKER - MAXIMUM EFFICIENCY EDITION
Ultra-fast prime checking using optimized pre-filters:
1. Special cases (< 2, small primes)
2. Last digit filter (eliminates 60% immediately)  
3. DART-69 forbidden zones (eliminates additional ~36% of remaining)
4. Full primality test only if needed

Handles arbitrarily large numbers with gmpy2 support.
DART-69 forbidden zones: multiples of 3 AND multiples of 23 (positions 0,3,6,9,12,15,18,21,23,24,27,30,33,36,39,42,45,46,48,51,54,57,60,63,66)
"""

try:
    import gmpy2
    from gmpy2 import mpz, is_prime as gmpy2_is_prime, next_prime, prev_prime
    GMPY2_AVAILABLE = True
    print("✓ gmpy2 loaded - Big number support enabled")
except ImportError:
    print("⚠ gmpy2 not available - Install with: pip install gmpy2")
    print("  Falling back to standard library (limited to smaller numbers)")
    GMPY2_AVAILABLE = False

import math
import time
from decimal import Decimal, getcontext

# Set high precision for π calculations
getcontext().prec = 50

# Pre-computed lookup tables for maximum speed
INVALID_LAST_DIGITS = {0, 2, 4, 5, 6, 8}  # Numbers ending in these can't be prime (except 2, 5)
VALID_LAST_DIGITS = {1, 3, 7, 9}  # Only these endings can be prime for n > 5

# DART-69 forbidden positions (multiples of 3 OR multiples of 23)
DART69_FORBIDDEN = set()
for i in range(69):
    if i % 3 == 0 or i % 23 == 0:
        DART69_FORBIDDEN.add(i)

DART69_ALLOWED = set(range(69)) - DART69_FORBIDDEN
print(f"✓ DART-69 initialized: {len(DART69_FORBIDDEN)}/69 positions forbidden ({len(DART69_FORBIDDEN)/69*100:.1f}%)")

def is_prime_fast(n):
    """Fast primality test using gmpy2 if available"""
    if GMPY2_AVAILABLE:
        return gmpy2_is_prime(int(n)) != 0
    else:
        n = int(n)
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        sqrt_n = int(math.sqrt(n))
        for i in range(3, sqrt_n + 1, 2):
            if n % i == 0:
                return False
        return True

def get_dimension_range(dimension):
    """Calculate π-dimensional bounds."""
    if GMPY2_AVAILABLE:
        pi = float(gmpy2.const_pi())
    else:
        pi = math.pi
    
    start = math.floor(pi ** (dimension - 1)) + 1
    end = math.floor(pi ** dimension)
    return start, end

def get_dimension_for_number(n):
    """Determine which π-dimension a number belongs to"""
    if n <= 1:
        return 0
    
    # Use high precision π for large numbers
    if GMPY2_AVAILABLE:
        pi = float(gmpy2.const_pi())
    else:
        pi = math.pi
    
    # Find dimension d where floor(π^(d-1)) < n <= floor(π^d)
    d = 1
    while True:
        upper_bound = math.floor(pi ** d)
        if n <= upper_bound:
            return d
        d += 1
        if d > 100:  # Safety check
            return d

def get_dart69_position(n):
    """Get the dart-69 wheel position for number n (dimensional method)"""
    dimension = get_dimension_for_number(n)
    start, end = get_dimension_range(dimension)
    
    # Position relative to dimension start
    relative_position = int(n) - start
    return relative_position % 69

def get_dart69_angle(n):
    """Calculate the dart-69 angle in degrees (dimensional method)"""
    position = get_dart69_position(n)
    return position * (360 / 69)

def last_digit_precheck(n):
    """
    Ultra-fast last digit check - eliminates ~60% of numbers instantly
    Returns: (could_be_prime, reason)
    """
    n_int = int(n)
    last_digit = n_int % 10
    
    # Handle special cases first
    if n_int == 2:
        return True, "Special case: 2"
    if n_int == 5:
        return True, "Special case: 5"
    
    # Check invalid endings
    if last_digit in INVALID_LAST_DIGITS:
        return False, f"Invalid last digit: {last_digit}"
    
    return True, f"Valid last digit: {last_digit}"

def dart69_precheck(n):
    """
    Use dart-69 system to check forbidden zones (dimensional method)
    Forbidden zones: multiples of 3 OR multiples of 23
    Returns: (could_be_prime, reason, position, angle)
    """
    n_int = int(n)
    
    # Get dart-69 position and angle using dimensional method
    position = get_dart69_position(n_int)
    angle = get_dart69_angle(n_int)
    dimension = get_dimension_for_number(n_int)
    
    # Check forbidden zones (multiples of 3 OR multiples of 23)
    if position in DART69_FORBIDDEN:
        if position % 3 == 0 and position % 23 == 0:
            return False, f"Forbidden zone (pos {position}, multiple of both 3 and 23)", position, angle
        elif position % 3 == 0:
            return False, f"Forbidden zone (pos {position}, multiple of 3)", position, angle
        else:  # position % 23 == 0
            return False, f"Forbidden zone (pos {position}, multiple of 23)", position, angle
    
    # Passed dart-69 precheck
    return True, f"Allowed position {position} in D{dimension}", position, angle

def optimized_prime_check(n, verbose=False):
    """
    Multi-stage optimized prime check with DART-69 priority
    Returns: (is_prime, stage_passed, details)
    """
    start_time = time.time()
    n_str = str(n)
    n_int = int(n)
    
    # Stage timings
    stage_times = {}
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"DART-69 OPTIMIZED PRIME CHECK: {n_str}")
        print(f"{'='*80}")
        print(f"Number: {n_str}")
        print(f"Digits: {len(n_str):,}")
        print(f"π-Dimension: {get_dimension_for_number(n_int)}")
        print()
    
    # STAGE 1: Special cases
    stage1_start = time.time()
    if n_int < 2:
        stage_times['stage1'] = time.time() - stage1_start
        if verbose:
            print("🚫 STAGE 1: Less than 2")
        return False, 1, {"reason": "Less than 2", "times": stage_times}
    
    if n_int in {2, 3, 5, 7}:
        stage_times['stage1'] = time.time() - stage1_start
        if verbose:
            print(f"🎯 STAGE 1: Special prime case ({n_int})")
        return True, 1, {"reason": f"Special prime: {n_int}", "times": stage_times}
    
    stage_times['stage1'] = time.time() - stage1_start
    
    # STAGE 2: Last digit filter
    stage2_start = time.time()
    last_digit_ok, last_digit_reason = last_digit_precheck(n_int)
    stage_times['stage2'] = time.time() - stage2_start
    
    if not last_digit_ok:
        if verbose:
            print(f"🚫 STAGE 2: {last_digit_reason}")
        return False, 2, {"reason": last_digit_reason, "times": stage_times}
    
    if verbose:
        print(f"✓ STAGE 2: {last_digit_reason}")
    
    # STAGE 3: DART-69 forbidden zones (moved up for efficiency)
    stage3_start = time.time()
    dart69_ok, dart69_reason, position, angle = dart69_precheck(n_int)
    stage_times['stage3'] = time.time() - stage3_start
    
    if not dart69_ok:
        if verbose:
            print(f"🚫 STAGE 3: {dart69_reason} ({angle:.1f}°)")
        return False, 3, {
            "reason": dart69_reason, 
            "position": position, 
            "angle": angle,
            "times": stage_times
        }
    
    if verbose:
        print(f"✓ STAGE 3: {dart69_reason} ({angle:.1f}°)")
        print("\n🔍 Passed all pre-filters - proceeding to full primality test...")
    
    # STAGE 4: Full primality test
    stage4_start = time.time()
    is_prime_result = is_prime_fast(n_int)
    stage_times['stage4'] = time.time() - stage4_start
    stage_times['total'] = time.time() - start_time
    
    if verbose:
        result_icon = "🎯" if is_prime_result else "🚫"
        result_text = "PRIME" if is_prime_result else "COMPOSITE"
        print(f"\n{result_icon} FINAL RESULT: {result_text}")
        print(f"Position {position} ({angle:.1f}°)")
        
        # Show timing breakdown
        print(f"\nTIMING BREAKDOWN:")
        print(f"  Stage 1 (special cases): {stage_times['stage1']:.6f}s")
        print(f"  Stage 2 (last digit):    {stage_times['stage2']:.6f}s") 
        print(f"  Stage 3 (DART-69):       {stage_times['stage3']:.6f}s")
        print(f"  Stage 4 (full test):     {stage_times['stage4']:.6f}s")
        print(f"  Total time:              {stage_times['total']:.6f}s")
        
        prefilter_time = sum(stage_times[k] for k in ['stage1', 'stage2', 'stage3'])
        if stage_times['stage4'] > 0:
            speedup = stage_times['stage4'] / prefilter_time if prefilter_time > 0 else float('inf')
            print(f"  Pre-filter speedup:      {speedup:.1f}x faster than full test")
    
    return is_prime_result, 4, {
        "reason": f"{'Prime' if is_prime_result else 'Composite'} at position {position}",
        "position": position,
        "angle": angle,
        "times": stage_times
    }

def find_nearby_primes(n, count=5):
    """Find a specified number of primes near the given number (DART-69 filtered)"""
    if not GMPY2_AVAILABLE:
        print("⚠ gmpy2 required for nearby prime search")
        return []
    
    print(f"\nFINDING {count} PRIMES NEAR {n}:")
    print("-" * 60)
    
    # Start searching from n
    current = gmpy2.mpz(n)
    found_primes = []
    checked = 0
    max_iterations = count * 1000  # Safety limit
    
    while len(found_primes) < count and checked < max_iterations:
        # Find next potential prime
        if checked == 0:
            # First iteration - start from current number if it's prime
            if gmpy2_is_prime(current):
                candidate = int(current)
            else:
                candidate = int(next_prime(current))
        else:
            candidate = int(next_prime(current))
        
        # Check DART-69 filtering
        position = get_dart69_position(candidate)
        
        # Only include if NOT in forbidden zone
        if position not in DART69_FORBIDDEN:
            found_primes.append(candidate)
        
        current = gmpy2.mpz(candidate)
        checked += 1
    
    if len(found_primes) < count:
        print(f"⚠ Found only {len(found_primes)} DART-69 compliant primes after checking {checked} candidates")
    
    # Display results
    print("Prime | DART-69 Position | Angle | Distance from input")
    print("-" * 60)
    
    for prime in found_primes:
        pos = get_dart69_position(prime)
        angle = get_dart69_angle(prime)
        distance = abs(prime - int(n))
        direction = "+" if prime > int(n) else ""
        
        print(f"{prime:>12,} | {pos:>15} | {angle:>6.1f}° | {direction}{distance:,}")
    
    return found_primes

def batch_analysis(numbers, show_stats=True):
    """Analyze filtering efficiency across multiple numbers"""
    print(f"🎯 BATCH ANALYSIS - {len(numbers)} numbers")
    print("=" * 70)
    
    stage_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    total_times = {f'stage{i}': 0 for i in range(1, 5)}
    total_times['total'] = 0
    
    results = []
    
    for i, n in enumerate(numbers):
        print(f"[{i+1:>3}/{len(numbers)}] {n:>15,}", end=" -> ")
        
        is_prime_result, stage, details = optimized_prime_check(n, verbose=False)
        stage_counts[stage] += 1
        
        # Accumulate timing
        if 'times' in details:
            for key, value in details['times'].items():
                if key in total_times:
                    total_times[key] += value
        
        status = "🎯 PRIME" if is_prime_result else "🚫 COMPOSITE"
        stage_name = ["", "special", "last digit", "DART-69", "full test"][stage]
        print(f"{status} (filtered at: {stage_name})")
        
        results.append((n, is_prime_result, stage, details))
    
    if show_stats:
        print(f"\n{'='*70}")
        print("FILTERING EFFICIENCY ANALYSIS:")
        print("-" * 50)
        
        total_nums = len(numbers)
        print(f"Stage 1 (special cases):  {stage_counts[1]:>6} ({stage_counts[1]/total_nums*100:>5.1f}%)")
        print(f"Stage 2 (last digit):     {stage_counts[2]:>6} ({stage_counts[2]/total_nums*100:>5.1f}%)")
        print(f"Stage 3 (DART-69):        {stage_counts[3]:>6} ({stage_counts[3]/total_nums*100:>5.1f}%)")
        print(f"Stage 4 (full test):      {stage_counts[4]:>6} ({stage_counts[4]/total_nums*100:>5.1f}%)")
        
        # Calculate cumulative filtering
        filtered_by_prefilters = sum(stage_counts[i] for i in range(1, 4))
        print(f"\nPre-filter elimination:   {filtered_by_prefilters:>6} ({filtered_by_prefilters/total_nums*100:>5.1f}%)")
        print(f"Required full testing:    {stage_counts[4]:>6} ({stage_counts[4]/total_nums*100:>5.1f}%)")
        
        if total_times['total'] > 0:
            print(f"\nTIMING SUMMARY:")
            print(f"Total computation time:   {total_times['total']:.3f}s")
            print(f"Average per number:       {total_times['total']/total_nums:.6f}s")
            
            if stage_counts[4] > 0:
                avg_full_test = total_times['stage4'] / stage_counts[4]
                avg_prefilter = sum(total_times[f'stage{i}'] for i in range(1, 4)) / filtered_by_prefilters if filtered_by_prefilters > 0 else 0
                if avg_prefilter > 0:
                    speedup = avg_full_test / avg_prefilter
                    print(f"Pre-filter speedup:       {speedup:.1f}x faster than full test")
    
    return results

def interactive_checker():
    """Interactive prime checking interface"""
    print("🎯 DART-69 OPTIMIZED PRIME CHECKER")
    print("=" * 50)
    print("Multi-stage filtering: Last digit → DART-69 → Full test")
    print("Commands: number, 'batch <n1> <n2> ...', 'random <digits>', 'help', 'q'")
    print()
    
    while True:
        try:
            user_input = input("Enter number or command: ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("Happy prime hunting with DART-69! 🎯")
                break
            
            if user_input.lower() == 'help':
                print("\nCOMMANDS:")
                print("  123456789         - Check if number is prime")
                print("  batch 100 101 102 - Check multiple numbers")
                print("  random 20         - Generate and check random 20-digit number")
                print("  help              - Show this help")
                print("  q                 - Quit")
                continue
            
            if user_input.startswith('batch '):
                try:
                    numbers = [int(x) for x in user_input[6:].split()]
                    if numbers:
                        batch_analysis(numbers)
                    else:
                        print("Please provide numbers after 'batch'")
                except ValueError:
                    print("Please provide valid numbers after 'batch'")
                continue
            
            if user_input.startswith('random '):
                try:
                    digits = int(user_input[7:].strip())
                    if digits < 1 or digits > 1000:
                        print("Please enter a reasonable number of digits (1-1000)")
                        continue
                    
                    import random
                    if digits == 1:
                        number = random.randint(2, 9)  # Start from 2 for single digits
                    else:
                        first_digit = random.randint(1, 9)
                        remaining = ''.join(str(random.randint(0, 9)) for _ in range(digits - 1))
                        # Ensure it ends in a valid digit for efficiency demonstration
                        if random.random() < 0.3:  # 30% chance to make it end in valid digit
                            last_valid = random.choice([1, 3, 7, 9])
                            remaining = remaining[:-1] + str(last_valid)
                        number = int(str(first_digit) + remaining)
                    
                    print(f"\nRandom {digits}-digit number: {number}")
                    optimized_prime_check(number, verbose=True)
                    
                except ValueError:
                    print("Please enter a valid number of digits")
                continue
            
            # Regular number check
            try:
                number = int(user_input)
                if number < 0:
                    print("Please enter a positive number")
                    continue
                
                optimized_prime_check(number, verbose=True)
                
                # Offer to find nearby primes with custom count
                if GMPY2_AVAILABLE:
                    nearby = input("\nFind nearby primes? (y/n): ").strip().lower()
                    if nearby in ['y', 'yes']:
                        try:
                            count_input = input("How many primes to find? (default 5): ").strip()
                            count = int(count_input) if count_input else 5
                            if count > 100:
                                print("Limiting to 100 primes for performance")
                                count = 100
                            find_nearby_primes(number, count)
                        except ValueError:
                            print("Invalid count, using default of 5")
                            find_nearby_primes(number, 5)
                
            except ValueError:
                print("Please enter a valid integer or command")
            
            print()
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def demo_efficiency():
    """Demonstrate the filtering efficiency"""
    print("🎯 DART-69 EFFICIENCY DEMONSTRATION")
    print("=" * 60)
    
    # Generate test numbers with various patterns
    test_numbers = []
    
    # Numbers ending in bad digits (should be filtered at stage 2)
    test_numbers.extend([1234, 5678, 9990, 12345])
    
    # Numbers in DART-69 forbidden zones (should be filtered at stage 3)
    # Test some D6 numbers (307-961) at forbidden positions
    d6_start = 307
    test_numbers.extend([
        d6_start + 0,   # position 0 (forbidden: multiple of 3)
        d6_start + 3,   # position 3 (forbidden: multiple of 3)  
        d6_start + 23,  # position 23 (forbidden: multiple of 23)
        d6_start + 46,  # position 46 (forbidden: multiple of 23)
    ])
    
    # Some actual primes (should reach stage 4)
    test_numbers.extend([101, 113, 127, 139, 149, 151])
    
    # Some large composites that pass pre-filters
    test_numbers.extend([1001, 1003, 1007, 1009])
    
    batch_analysis(test_numbers, show_stats=True)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'demo':
            demo_efficiency()
        elif sys.argv[1] == 'batch':
            numbers = [int(x) for x in sys.argv[2:]]
            batch_analysis(numbers)
        else:
            number = int(sys.argv[1])
            optimized_prime_check(number, verbose=True)
    else:
        interactive_checker()
