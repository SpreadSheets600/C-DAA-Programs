#include <stdio.h>

// Global Minimum And Maximum
int min, max;

void findMinMax(int arr[], int low, int high) {
    // Case 1 : Only One Element
    if (low == high) {
        min = arr[low];
        max = arr[low];
    }

    // Case 2 : Only Two Element
    if (high == low + 1) {
        if (arr[high] > arr[low]) {
            min = arr[low];
            max = arr[high];
        } else {
            min = arr[high];
            max = arr[low];
        }
    }

    // Case 3 : Divide And Conquer
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
    int arr[5] = {1, 4, 9, 2, 8};
    int size = sizeof(arr) / sizeof(arr[0]);

    findMinMax(arr, 0, size - 1);

    printf("The Maximum Element : %d\n", max);
    printf("The Minimum Element : %d", min);

    return 0;
}
