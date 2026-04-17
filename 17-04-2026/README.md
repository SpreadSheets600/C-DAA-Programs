# Programming Exercises - April 17, 2026

## Exercise 1 : Minimum And Maximum Using Reccursion

## Question : Write A Program To Find Minimum And Maximum Of An Array Using Reccursion

### Algorithm :

1. Start with the array range defined by `low` and `high`
2. If the segment has only one element (`low == high`):
    - Set both `min` and `max` to that element

3. If the segment has more than two elements:
    - Calculate `mid = low + (high - low) / 2`
    - Recursively find `min1, max1` in the left half (`low → mid`)
    - Recursively find `min2, max2` in the right half (`mid+1 → high`)
    - Set `min = smaller(min1, min2)`
    - Set `max = larger(max1, max2)`

4. Return the final `min` and `max` values

### Code :

```cpp
#include <stdio.h>

// Global Minimum And Maximum
int min, max;

void findMinMax(int arr[], int low, int high) {
    // Case 1 : Only One Element
    if (low == high) {
        min = arr[low];
        max = arr[low];
    }

    // Case 2 : Divide And Conquer
    if (high > low + 1) {

        // Split The Array in Two Parts
        int mid = low + (high - low) / 2;

        // LocalMin And LocaLMax
        int leftMin, leftMax, rightMin, rightMax;

        // For Left Side ~ Low To Mid
        findMinMax(arr, low, mid);
        leftMin = min;
        leftMax = max;

        // For Right Side ~ Mid To High
        findMinMax(arr, mid, high);
        rightMin = min;
        rightMax = max;

        // Final Pass
        min = (leftMin < rightMin) ? leftMin : rightMin;
        max = (leftMax > rightMax) ? leftMax : rightMax;
    }
}

int main() {
    int size;

    printf("Enter The Size Of Array : ");
    scanf("%d", &size);

    int arr[size];

    for (int i = 0; i < size; i++) {
        printf("Enter The Value Of Element %d : ", i);
        scanf("%d", &arr[i]);
    }

    printf("\nThe Array : ");

    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }

    findMinMax(arr, 0, size - 1);

    printf("\n\nThe Maximum Element : %d", max);
    printf("\nThe Minimum Element : %d", min);

    return 0;
}
```

### Output :

```bash
Enter The Size Of Array : 5
Enter The Value Of Element 0 : 9
Enter The Value Of Element 1 : 78
Enter The Value Of Element 2 : 23
Enter The Value Of Element 3 : 67
Enter The Value Of Element 4 : 1

The Array : 9 78 23 67 1

The Maximum Element : 78
The Minimum Element : 1
```
