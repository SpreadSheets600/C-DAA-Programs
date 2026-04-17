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
