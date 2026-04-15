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
