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
