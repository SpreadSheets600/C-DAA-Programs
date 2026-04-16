# Programming Exercises - April 10, 2026

## Exercise 1 : Binary Search With Iteration

### Algorithm :

1. Start with `left = 0` and `right = size - 1`
2. While `left <= right`:
    - Calculate `mid = left + (right - left) / 2`
    - If `arr[mid] == target` → Return `mid` (Element Found)
    - If `arr[mid] < target` → Set `left = mid + 1` (Search Right Half)
    - Else → Set `right = mid - 1` (Search Left Half)
3. Return `-1` (Element Not Found)

### Code :

```cpp
#include <stdio.h>

int binarySearch(int arr[], int size, int target) {
    int left = 0;
    int right = size - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return -1;
}

int main() {
    // Array Implementation ~ Array Must Be Sorted
    int arr[] = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
    int size = sizeof(arr) / sizeof(arr[0]);
    int target = 7;

    // Calling Binary Search With Array, Size, And Target
    int result = binarySearch(arr, size, target);

    if (result != -1) {
        printf("Element Found At Index %d\n", result);
    } else {
        printf("Element Not Found\n");
    }

    return 0;
}
```

### Output :

```bash
Element Found At Index 3
```

---

## Exercise 2 : Binary Search With Reccursion

### Algorithm :

1. **Base Case** : If `size == 0`, return `-1` (Element Not Found)
2. Calculate `mid = size / 2`
3. If `arr[mid] == target` → Return `mid` (Element Found)
4. If `arr[mid] > target` → Recursively search left half: `binarySearch(arr, mid, target)`
5. Else → Recursively search right half: `binarySearch(arr + mid + 1, size - mid - 1, target)`

### Code :

```cpp
#include <stdio.h>

int binarySearch(int arr[], int size, int target) {
    if (size == 0) {
        return -1;
    }

    int mid = size / 2;

    if (arr[mid] == target) {
        return mid;
    } else if (arr[mid] > target) {
        return binarySearch(arr, mid, target);
    } else {
        return binarySearch(arr + mid + 1, size - mid - 1, target);
    }
}

int main() {
    // Array Implementation ~ Array Must Be Sorted
    int arr[] = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
    int size = sizeof(arr) / sizeof(arr[0]);
    int target = 7;

    // Calling Binary Search With Array, Size, And Target
    int result = binarySearch(arr, size, target);

    if (result != -1) {
        printf("Element Found At Index %d\n", result);
    } else {
        printf("Element Not Found\n");
    }

    return 0;
}
```

### Output :

```bash
Element Found At Index 0
```

---

## Exercise 3 : Binary Search With Unsorted Array

### Algorithm :

1. Take user input for the array size and elements
2. Print the unsorted array
3. Sort the array using **Bubble Sort** :
    - Outer loop runs `size - 1` passes
    - Inner loop compares adjacent elements and swaps if out of order
    - Repeat until the array is fully sorted
4. Print the sorted array
5. Take user input for the target element
6. Apply recursive **Binary Search** on the sorted array
7. Print the result (Element Found at Index / Element Not Found)

### Code :

```cpp
#include <stdio.h>

int bubbleSort(int arr[], int size) {
    for (int i = 0; i < size - 1; i++) {
        for (int j = 0; j < size - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }

    return 0;
}

int binarySearch(int arr[], int size, int target) {
    if (size == 0) {
        return -1;
    }

    int mid = size / 2;

    if (arr[mid] == target) {
        return mid;
    } else if (arr[mid] > target) {
        return binarySearch(arr, mid, target);
    } else {
        return binarySearch(arr + mid + 1, size - mid - 1, target);
    }
}

int main() {
    int size;

    // Array Size Input
    printf("Enter The Number Of Elements : ");
    scanf("%d", &size);
    int arr[size];

    // Taking User Input In Array
    for (int i = 0; i < size; i++) {
        printf("Enter Element %d: ", i + 1);
        scanf("%d", &arr[i]);
    }

    // Printing Unsorted Array
    printf("Unsorted Array: ");
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");

    // Sorting Array
    bubbleSort(arr, size);

    // Printing Sorted Array
    printf("Sorted Array: ");
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");

    // Binary Search
    int target;
    printf("Enter The Element To Search: ");
    scanf("%d", &target);

    int result = binarySearch(arr, size, target);

    if (result == -1) {
        printf("Element Not Found\n");
    } else {
        printf("Element Found At Index %d\n", result);
    }

    return 0;
}
```

### Output :

```bash
Enter The Number Of Elements : 5
Enter Element 1: 9
Enter Element 2: 3
Enter Element 3: 7
Enter Element 4: 1
Enter Element 5: 5

Unsorted Array: 9 3 7 1 5
Sorted Array: 1 3 5 7 9

Enter The Element To Search: 7
Element Found At Index 0
```
