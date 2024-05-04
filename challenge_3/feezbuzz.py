def feez_buzz(n, conditions):
    return [''.join(conditions[divisor] for divisor in conditions if i % divisor == 0) or str(i) for i in range(1, n + 1)]

# Example usage:
n = 20
conditions = {3: "Fizz", 5: "Buzz", 7: "Beez"}  # Extendable to include "Beez" for multiples of 7
result = feez_buzz(n, conditions)
print(result)
