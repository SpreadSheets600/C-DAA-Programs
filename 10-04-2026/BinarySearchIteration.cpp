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
