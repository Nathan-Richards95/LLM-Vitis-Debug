#include <vector>
// error will be a missing semicolon on the following line: c[i] = a[i] + b[i];
static void vec_add(std::vector<int> &a, std::vector<int> &b, std::vector<int> &c)
{
    for (int i = 0; i < a.size(); i++)
    {
        c[i] = a[i] - b[i];
    }
}