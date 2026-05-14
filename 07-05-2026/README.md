# Programming Exercises - May 07, 2026

## Exercise 1 : Fractional Knapsack Problem

## Question : Write A Program To Solve The Fractional Knapsack Problem Using Greedy Approach

### Algorithm

1. Input the knapsack capacity and the number of items.
2. For each item, input its profit and weight.
3. Calculate the profit-to-weight ratio for each item.
4. Sort the items in descending order based on the profit-to-weight ratio.
5. Initialize the total profit to 0 and the fraction array x[i] to 0 for all items.
6. Iterate through the sorted items:
   - If the current item's weight is less than or equal to the remaining capacity:
     - Set x[i] = 1 (take the full item).
     - Add the item's profit to the total profit.
     - Subtract the item's weight from the remaining capacity.
   - Else if there is remaining capacity:
     - Set x[i] = remaining capacity / item's weight (take a fraction).
     - Add (x[i] * item's profit) to the total profit.
     - Set remaining capacity to 0.
   - If no capacity remains, break the loop.
7. Output the maximum profit and the selected fractions for each item.

### Code

```cpp
#include <stdio.h>

int main()
{
    int i, j, n, m;
    int p[10], w[10];

    float k[10], x[10], profit = 0;
    float temp;

    // User Input For Capacity
    printf("Enter Capacity For Knapsack : ");
    scanf("%d", &m);

    printf("Enter Number Of Items : ");
    scanf("%d", &n);

    printf("Enter Profit and Weight of Each Item :\n");
    for (i = 0; i < n; i++)
    {
        scanf("%d %d", &p[i], &w[i]);
    }

    // Calculate Profit To Weight Ratio
    for (i = 0; i < n; i++)
    {
        k[i] = (float)p[i] / w[i];
    }

    // Sort Items Based On Decending Ratio
    for (i = 0; i < n - 1; i++)
    {
        for (j = 0; j < n - i - 1; j++)
        {
            if (k[j] < k[j + 1])
            {
                // Swap Ratio
                temp = k[j];
                k[j] = k[j + 1];
                k[j + 1] = temp;

                // Swap Profit
                temp = p[j];
                p[j] = p[j + 1];
                p[j + 1] = temp;

                // Swap Weight
                temp = w[j];
                w[j] = w[j + 1];
                w[j + 1] = temp;
            }
        }
    }

    // Initialize x[i] = 0
    for (i = 0; i < n; i++)
    {
        x[i] = 0;
    }

    // Greedy Selection
    for (i = 0; i < n; i++)
    {
        if (w[i] <= m)
        {
            x[i] = 1;
            profit += p[i];
            m -= w[i];
        }
        else if (m > 0)
        {
            x[i] = (float)m / w[i];
            profit += x[i] * p[i];
            m = 0;
        }
        else
        {
            break;
        }
    }

    // Output
    printf("Maximum Profit = %.2f\n", profit);

    printf("Selected Fractions :\n");
    for (i = 0; i < n; i++)
    {
        printf("Item %d = %.2f\n", i + 1, x[i]);
    }

    return 0;
}
```

### Output

```bash
Enter Capacity For Knapsack : 50
Enter Number Of Items : 3
Enter Profit and Weight of Each Item :
60 10
100 20
120 30
Maximum Profit = 240.00
Selected Fractions :
Item 1 = 1.00
Item 2 = 1.00
Item 3 = 0.67
```
