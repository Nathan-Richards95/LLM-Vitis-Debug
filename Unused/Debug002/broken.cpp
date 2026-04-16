#include <vector>

void vec_subtract(std::vector<int> &a, std::vector<int> &b, std::vector<int> &c)
{
    for (int i = 0; i < a.size(); i++)
    {
        c[i] = a[i] - b[i];
    
}