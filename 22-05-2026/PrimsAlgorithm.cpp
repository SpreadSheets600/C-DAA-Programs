#include <stdio.h>

int main()
{
    int n;

    printf("Enter Number Of Vertices : ");
    scanf("%d", &n);

    int graph[n][n];
    int selected[n];

    printf("Enter Adjacency Matrix :\n");
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            scanf("%d", &graph[i][j]);
        }
    }

    for (int i = 0; i < n; i++)
        selected[i] = 0;

    selected[0] = 1; // Start From Vertex 0

    int edges = 0, totalCost = 0;

    printf("\nMinimum Spanning Tree :\n");
    printf("Edge\tWeight\n");

    while (edges < n - 1)
    {
        int min = 9999;
        int x = -1, y = -1;

        for (int i = 0; i < n; i++)
        {
            if (selected[i])
            {
                for (int j = 0; j < n; j++)
                {
                    if (!selected[j] && graph[i][j] != 0)
                    {
                        if (graph[i][j] < min)
                        {
                            min = graph[i][j];
                            x = i;
                            y = j;
                        }
                    }
                }
            }
        }

        printf("%d - %d\t%d\n", x, y, min);

        totalCost += min;
        selected[y] = 1;
        edges++;
    }

    printf("Total Cost = %d\n", totalCost);

    return 0;
}
