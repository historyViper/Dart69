#!/usr/bin/env python3
"""
DART-69 PRIME CHECKER - BIG NUMBER EDITION
Check if any number is prime using the dart-69 system as a smart pre-filter.
Handles arbitrarily large numbers with gmpy2 support.

The dart-69 system can immediately rule out numbers in forbidden positions,
making this much faster than traditional primality tests for large numbers.
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

def get_dart69_position(n):
    """Get the dart-69 wheel position for number n"""
    return int(n) % 69

def get_dart69_angle(n):
    """Calculate the dart-69 angle in degrees"""
    position = get_dart69_position(n)
    return position * (360 / 69)

def is_forbidden_position(pos, allow_early_exceptions=False):
    """
    Check if a position is in the forbidden zone
    pos: wheel position (0-68)
    allow_early_exceptions: whether to allow positions 3 and 23 (for early dimensions)
    """
    if pos % 3 == 0:
        if allow_early_exceptions and pos in [3, 23]:
            return False  # Not forbidden in early dimensions
        return True  # Forbidden
    return False  # Allowed

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

def dart69_precheck(n):
    """
    Use dart-69 system to quickly check if a number could be prime
    Returns: (could_be_prime, reason, position, angle)
    """
    n = int(n)
    
    # Handle special cases
    if n < 2:
        return False, "Less than 2", 0, 0
    if n == 2:
        return True, "Special case: 2", 2, get_dart69_angle(2)
    if n == 3:
        return True, "Special case: 3", 3, get_dart69_angle(3)
    if n % 2 == 0:
        return False, "Even number", get_dart69_position(n), get_dart69_angle(n)
    
    # Get dart-69 position and angle
    position = get_dart69_position(n)
    angle = get_dart69_angle(n)
    
    # Determine dimension for exception handling
    dimension = get_dimension_for_number(n)
    allow_exceptions = dimension <= 3
    
    # Check forbidden zones
    if is_forbidden_position(position, allow_exceptions):
        if position == 3:
            return False, f"Forbidden zone (pos 3, only prime 3 allowed)", position, angle
        elif position == 23:
            return False, f"Forbidden zone (pos 23, only prime 23 allowed)", position, angle
        else:
            return False, f"Forbidden zone (position {position})", position, angle
    
    # Passed dart-69 precheck
    return True, f"Allowed position {position}", position, angle

def check_prime_with_dart69(n):
    """
    Complete prime check using dart-69 system + full primality test
    Returns detailed results
    """
    start_time = time.time()
    n_str = str(n)
    
    print(f"\n{'='*80}")
    print(f"DART-69 PRIME CHECK: {n_str}")
    print(f"{'='*80}")
    
    # Basic info
    num_digits = len(n_str)
    dimension = get_dimension_for_number(n)
    
    print(f"Number: {n_str}")
    print(f"Digits: {num_digits:,}")
    print(f"π-Dimension: {dimension}")
    print()
    
    # Dart-69 precheck
    print("DART-69 PRECHECK:")
    print("-" * 40)
    
    could_be_prime, reason, position, angle = dart69_precheck(n)
    print(f"Wheel position: {position}")
    print(f"Angle: {angle:.2f}°")
    print(f"Zone status: {reason}")
    
    precheck_time = time.time() - start_time
    print(f"Precheck time: {precheck_time:.6f} seconds")
    
    if not could_be_prime:
        total_time = time.time() - start_time
        print()
        print("🚫 RESULT: COMPOSITE (ruled out by dart-69 system)")
        print(f"⚡ Total time: {total_time:.6f} seconds")
        print("🎯 No expensive primality test needed!")
        return False, f"Composite - {reason}"
    
    print("✓ Passed dart-69 precheck - proceeding to full primality test...")
    print()
    
    # Full primality test
    print("FULL PRIMALITY TEST:")
    print("-" * 40)
    
    primality_start = time.time()
    is_prime_result = is_prime_fast(n)
    primality_time = time.time() - primality_start
    total_time = time.time() - start_time
    
    print(f"Primality test time: {primality_time:.6f} seconds")
    print(f"Total time: {total_time:.6f} seconds")
    print()
    
    if is_prime_result:
        print("🎯 RESULT: PRIME")
        print(f"✓ Confirmed prime at dart-69 position {position} ({angle:.2f}°)")
        return True, f"Prime at position {position}"
    else:
        print("🚫 RESULT: COMPOSITE")
        print(f"⚠ Composite number in allowed dart-69 position {position}")
        return False, f"Composite at position {position}"

def find_nearby_primes(n, count=5):
    """Find primes near the given number"""
    if not GMPY2_AVAILABLE:
        print("⚠ gmpy2 required for nearby prime search")
        return
    
    print(f"\nFINDING {count} PRIMES NEAR {n}:")
    print("-" * 50)
    
    # Find previous primes
    current = gmpy2.mpz(n)
    prev_primes = []
    
    for i in range(count):
        try:
            prev_prime = prev_prime(current - 1) if i == 0 else prev_prime(current)
            if prev_prime > 0:
                prev_primes.append(int(prev_prime))
                current = prev_prime
            else:
                break
        except:
            break
    
    prev_primes.reverse()
    
    # Find next primes
    current = gmpy2.mpz(n)
    next_primes = []
    
    for i in range(count):
        try:
            next_prime_val = next_prime(current + 1) if i == 0 else next_prime(current)
            next_primes.append(int(next_prime_val))
            current = next_prime_val
        except:
            break
    
    # Display results
    all_primes = prev_primes + next_primes
    all_primes.sort()
    
    print("Prime | Dart-69 Position | Angle | Distance from input")
    print("-" * 60)
    
    for prime in all_primes:
        pos = get_dart69_position(prime)
        angle = get_dart69_angle(prime)
        distance = abs(prime - int(n))
        direction = "+" if prime > int(n) else "-"
        
        print(f"{prime:>12,} | {pos:>15} | {angle:>6.1f}° | {direction}{distance:,}")

def interactive_checker():
    """Interactive prime checking interface"""
    print("🎯 DART-69 PRIME CHECKER - BIG NUMBER EDITION")
    print("=" * 70)
    print("Enter any number to check if it's prime using the dart-69 system!")
    print("Type 'help' for commands or 'q' to quit.")
    print()
    
    while True:
        try:
            user_input = input("Enter number to check: ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("Thanks for using the dart-69 prime checker! 🎯")
                break
            
            if user_input.lower() == 'help':
                print("\nCOMMANDS:")
                print("- Enter any integer to check if it's prime")
                print("- 'nearby <number>' - find primes near the number")
                print("- 'random <digits>' - check a random number with specified digits")
                print("- 'help' - show this help")
                print("- 'q' - quit")
                continue
            
            if user_input.startswith('nearby '):
                number_str = user_input[7:].strip()
                try:
                    number = int(number_str)
                    find_nearby_primes(number)
                except ValueError:
                    print("Please enter a valid number after 'nearby'")
                continue
            
            if user_input.startswith('random '):
                try:
                    digits = int(user_input[7:].strip())
                    if digits < 1 or digits > 1000:
                        print("Please enter a reasonable number of digits (1-1000)")
                        continue
                    
                    # Generate random number with specified digits
                    import random
                    if digits == 1:
                        number = random.randint(1, 9)
                    else:
                        first_digit = random.randint(1, 9)
                        remaining = ''.join(str(random.randint(0, 9)) for _ in range(digits - 1))
                        number = int(str(first_digit) + remaining)
                    
                    print(f"Random {digits}-digit number: {number}")
                    check_prime_with_dart69(number)
                    
                except ValueError:
                    print("Please enter a valid number of digits after 'random'")
                continue
            
            # Regular number check
            try:
                number = int(user_input)
                if number < 0:
                    print("Please enter a positive number")
                    continue
                
                check_prime_with_dart69(number)
                
                # Offer to find nearby primes
                if GMPY2_AVAILABLE:
                    nearby = input("\nFind nearby primes? (y/n): ").strip().lower()
                    if nearby in ['y', 'yes']:
                        find_nearby_primes(number)
                
            except ValueError:
                print("Please enter a valid integer")
            
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def batch_check(numbers):
    """Check multiple numbers at once"""
    print(f"🎯 BATCH PRIME CHECK - {len(numbers)} numbers")
    print("=" * 60)
    
    results = []
    total_time = 0
    dart69_filtered = 0
    
    for i, n in enumerate(numbers):
        print(f"\n[{i+1}/{len(numbers)}] Checking {n}...")
        
        start_time = time.time()
        could_be_prime, reason, pos, angle = dart69_precheck(n)
        
        if not could_be_prime:
            dart69_filtered += 1
            result = False, reason
            elapsed = time.time() - start_time
            print(f"  🚫 Filtered by dart-69: {reason} ({elapsed:.6f}s)")
        else:
            is_prime_result = is_prime_fast(n)
            elapsed = time.time() - start_time
            result = is_prime_result, f"{'Prime' if is_prime_result else 'Composite'} at pos {pos}"
            status = "🎯 PRIME" if is_prime_result else "🚫 COMPOSITE"
            print(f"  {status} ({elapsed:.6f}s)")
        
        results.append((n, result[0], result[1]))
        total_time += elapsed
    
    # Summary
    print(f"\n{'='*60}")
    print("BATCH SUMMARY:")
    print(f"Numbers checked: {len(numbers)}")
    print(f"Filtered by dart-69: {dart69_filtered} ({dart69_filtered/len(numbers)*100:.1f}%)")
    print(f"Full tests needed: {len(numbers) - dart69_filtered}")
    print(f"Total time: {total_time:.3f} seconds")
    print(f"Average per number: {total_time/len(numbers):.6f} seconds")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line usage
        if sys.argv[1] == 'batch':
            numbers = [int(x) for x in sys.argv[2:]]
            batch_check(numbers)
        else:
            number = int(sys.argv[1])
            check_prime_with_dart69(number)
    else:
        # Interactive mode
        interactive_checker()
