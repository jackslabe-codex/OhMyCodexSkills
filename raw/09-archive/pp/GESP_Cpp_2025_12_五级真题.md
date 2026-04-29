GESP C++ 五级 2025年12月真题

## 单选题

| 题号 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 答案 | C | B | C | D | D | B | A | B | C | C | A | A | A | A | B |

### 第 1 题

对如下定义的循环单链表，横线处填写（ ）。

```cpp
// 循环单链表的结点
struct Node {
    int data;      // 数据域
    Node* next;    // 指针域
    Node(int d) : data(d), next(nullptr) {}
};

// 创建一个只有一个结点的循环单链表
Node* createList(int value) {
    Node* head = new Node(value);
    head->next = head;
    return head;
}

// 在循环单链表尾部插入新结点
void insertTail(Node* head, int value) {
    Node* p = head;
    while (p->next != head) {
        p = p->next;
    }
    Node* node = new Node(value);
    node->next = head;
    p->next = node;
}

// 遍历并输出循环单链表
void printList(Node* head) {
    if (head == nullptr) return;
    Node* p = head;
    _______________________ //在此处填入代码
    cout << endl;
}
```

A.

```cpp
while (p != nullptr){
    cout << p->data << " ";
    p = p->next;
}
```

B.

```cpp
while (p->next != nullptr){
    cout << p->data << " ";
    p = p->next;
}
```

C.

```cpp
do {
    cout << p->data << " ";
    p = p->next;
} while (p != head);
```

D.

```cpp
for(; p; p=p->next){
    cout << p->data << " ";
}
```

### 第 2 题

区块链技术是比特币的基础。在区块链中，每个区块指向前一个区块，构成链式列表，新区块只能接在链尾，不允许在中间插入或删除。下面代码实现插入区块添加函数，则横线处填写（ ）。

```cpp
//区块（节点）
struct Block {
    int index;      // 区块编号（高度）
    string data;    // 区块里保存的数据
    Block* prev;    // 指向前一个区块
    Block(int idx, const string& d, Block* p) : index(idx), data(d), prev(p) {}
};

// 区块链
struct Blockchain {
    Block* tail;

    // 初始化
    void init() {
        tail = new Block(0, "Genesis Block", nullptr);
    }

    // 插入新区块
    void addBlock(const string& data) {
        _______________________ //在此处填入代码
    }

    // 释放内存
    void clear() {
        Block* cur = tail;
        while (cur != nullptr) {
            Block* p = cur->prev;
            delete cur;
            cur = p;
        }
        tail = nullptr;
    }
};
```

A.

```cpp
Block* newBlock = new Block(tail->index + 1, data, tail);
tail = newBlock->prev;
```

B.

```cpp
Block* newBlock = new Block(tail->index + 1, data, tail);
tail = newBlock;
```

C.

```cpp
Block* newBlock = new Block(tail->index + 1, data, tail->prev);
tail = newBlock;
```

D.

```cpp
Block* newBlock = new Block(tail->index + 1, data, tail->prev);
tail = newBlock->prev;
```

### 第 3 题

下面关于单链表和双链表的描述中，正确的是（ ）。

```cpp
struct DNode {
    int data;
    DNode* prev;
    DNode* next;
};

// 在双链表中删除指定节点
void deleteNode(DNode* node) {
    if (node->prev) {
        node->prev->next = node->next;
    }
    if (node->next) {
        node->next->prev = node->prev;
    }
    delete node;
}

struct SNode {
    int data;
    SNode* next;
};

// 在单链表中删除指定节点
void deleteSNode(SNode* head, SNode* node) {
    SNode* prev = head;
    while (prev->next != node) {
        prev = prev->next;
    }
    prev->next = node->next;
    delete node;
}
```

A. 双链表删除指定节点是 $O(1)$，单链表是 $O(1)$
B. 双链表删除指定节点是 $O(n)$，单链表是 $O(1)$
C. 双链表删除指定节点是 $O(1)$，单链表是 $O(n)$
D. 双链表删除指定节点是 $O(n)$，单链表是 $O(n)$

### 第 4 题

假设我们有两个数 $a=38$ 和 $b=14$，它们对模 $m$ 同余，即 $a \equiv b \pmod m$。以下哪个值不可能是 $m$？

A. 3
B. 4
C. 6
D. 9

### 第 5 题

下面代码实现了欧几里得算法。下面有关说法，错误的是（ ）。

```cpp
int gcd1(int a, int b) {
    return b == 0 ? a : gcd1(b, a % b);
}

int gcd2(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}
```

A. `gcd1()` 实现为递归方式。
B. `gcd2()` 实现为迭代方式。
C. 当 $a$ 较大时，`gcd1()` 实现会多次调用自身，需要较多额外的辅助空间。
D. 当 $a$ 较大时，`gcd1()` 的实现比 `gcd2()` 执行效率更高。

### 第 6 题

唯一分解定理描述的内容是（ ）。

A. 任何正整数都可以表示为两个素数的和。
B. 任何大于1的合数都可以唯一分解为有限个质数的乘积。
C. 两个正整数的最大公约数总是等于它们的最小公倍数除以它们的乘积。
D. 所有素数都是奇数。

### 第 7 题

下述代码实现素数表的线性筛法，筛选出所有小于等于 $n$ 的素数，则横线上应填的代码是（ ）。

```cpp
vector<int> linear_sieve(int n) {
    vector<bool> is_prime(n +1, true);
    vector<int> primes;

    is_prime[0] = is_prime[1] = 0; //0和1两个数特殊处理
    for (int i = 2; i <= n; ++i) {
        if (is_prime[i]) {
            primes.push_back(i);
        }
        ________________________________ { // 在此处填入代码
            is_prime[ i * primes[j] ] = 0;
            if (i % primes[j] == 0)
                break;
        }
    }
    return primes;
}
```

A. `for (int j = 0; j < primes.size() && i * primes[j] <= n; j++)`
B. `for(int j = sqrt(n); j <= n && i * primes[j] <= n; j++)`
C. `for (int j = 1; j <= sqrt(n); j++)`
D. `for(int j = 1; j < n && i * primes[j] <= n; j++)`

### 第 8 题

下列关于排序的说法，正确的是（ ）。

A. 快速排序是稳定排序
B. 归并排序通常是稳定的
C. 插入排序是不稳定排序
D. 冒泡排序不是原地排序

### 第 9 题

下面代码实现了归并排序。下述关于归并排序的说法中，不正确的是（ ）。

```cpp
void merge(vector<int>& arr, vector<int>& temp, int l, int mid, int r) {
    int i = l, j = mid + 1, k = l;
    while (i <= mid && j <= r) {
        if (arr[i] <= arr[j]) temp[k++] = arr[i++];
        else temp[k++] = arr[j++];
    }
    while (i <= mid) temp[k++] = arr[i++];
    while (j <= r) temp[k++] = arr[j++];
    for (int p = l; p <= r; p++) arr[p] = temp[p];
}

void mergeSort(vector<int>& arr, vector<int>& temp, int l, int r) {
    if (l >= r) return;
    int mid = l + (r - l) / 2;
    mergeSort(arr, temp, l, mid);
    mergeSort(arr, temp, mid + 1, r);
    merge(arr, temp, l, mid, r);
}
```

A. 归并排序的平均复杂度是 $O(n\log n)$。
B. 归并排序需要 $O(n)$ 的额外空间。
C. 归并排序在最坏情况的时间复杂度是 $O(n^2)$。
D. 归并排序适合大规模数据。

### 第 10 题

下述C++代码实现了快速排序算法，最坏情况的时间复杂度是（ ）。

```cpp
int partition(vector<int>& arr, int low, int high) {
    int i = low, j = high;
    int pivot = arr[low]; // 以首元素为基准
    while (i < j) {
        while (i < j && arr[j] >= pivot) j--;
        while (i < j && arr[i] <= pivot) i++;
        if (i < j) swap(arr[i], arr[j]);
    }
    swap(arr[i], arr[low]);
    return i;
}

void quickSort(vector<int>& arr, int low, int high) {
    if (low >= high) return;
    int p = partition(arr, low, high);
    quickSort(arr, low, p - 1);
    quickSort(arr, p + 1, high);
}
```

A. $O(n)$
B. $O(\log n)$
C. $O(n^2)$
D. $O(n\log n)$

### 第 11 题

下面代码尝试在有序数组中查找第一个大于等于 `x` 的元素位置。如果没有大于等于 `x` 的元素，返回 `arr.size()`。以下说法正确的是（ ）。

```cpp
int lower_bound(vector<int>& arr, int x) {
    int l = 0, r = arr.size();
    while(l < r) {
        int mid = l + (r - l) / 2;
        if(arr[mid] >= x) r = mid;
        else l = mid + 1;
    }
    return l;
}
```

A. 上述代码逻辑正确
B. 上述代码逻辑错误，`while` 循环条件应该用 `l <= r`
C. 上述代码逻辑错误，`mid` 计算错误
D. 上述代码逻辑错误，边界条件不对

### 第 12 题

小杨要把一根长度为 $L$ 的木头切成 $K$ 段，使得每段长度小于等于 $x$。已知每切一刀只能把一段木头分成两段，他用二分法找到满足条件的最小 $x$（$x$ 为正整数），则横线处应填写（ ）。

```cpp
// 判断：在不超过 K 次切割内，是否能让每段长度 <= x
bool check(int L, int K, int x) {
    int cuts = (L - 1) / x;
    return cuts <= K;
}

// 二分查找最小可行的 x
int binary_cut(int L, int K) {
    int l = 1, r = L;
    while (l < r) {
        int mid = l + (r - l) / 2;
        ________________________________ // 在此处填入代码
    }
    return l;
}

int main() {
    int L = 10; // 木头长度
    int K = 2;  // 最多切 K 刀

    cout << binary_cut(L, K) << endl;
    return 0;
}
```

A.

```cpp
if (check(L, K, mid))
    r = mid;
else
    l = mid + 1;
```

B.

```cpp
if (check(L, K, mid))
    r = mid+1;
else
    l = mid + 1;
```

C.

```cpp
if (check(L, K, mid))
    r = mid + 1;
else
    l = mid - 1;
```

D.

```cpp
if (check(L, K, mid))
    r = mid + 1;
else
    l = mid;
```

### 第 13 题

下面给出了阶乘计算的两种方式。以下说法正确的是（ ）。

```cpp
int factorial1(int n) {
    if (n <= 1) return 1;
    return n * factorial1(n - 1);
}

int factorial2(int n) {
    int acc = 1;
    while (n > 1) {
        acc = n * acc;
        n = n - 1;
    }
    return acc;
}
```

A. 上面两种实现方式的时间复杂度相同，都为 $O(n)$
B. 上面两种实现方式的空间复杂度相同，都为 $O(n)$
C. 上面两种实现方式的空间复杂度相同，都为 $O(1)$
D. 函数 `factorial1()` 的时间复杂度为 $O(2^n)$，函数 `factorial2()` 的时间复杂度为 $O(n)$

### 第 14 题

给定有 $n$ 个任务，每个任务有截止时间和利润，每个任务耗时 1 个时间单位、必须在截止时间前完成，且每个时间槽最多做 1 个任务。为了在规定时间内获得最大利润，可以采用贪心策略，即按利润从高到低排序，尽量安排，则横线处应填写（ ）。

```cpp
struct Task {
    int deadline; //截止时间
    int profit;   //利润
};

void sortByProfit(vector<Task>& tasks) {
    sort(tasks.begin(), tasks.end(),
        [](const Task& a, const Task& b) {
            return a.profit > b.profit;
        });
}

int maxProfit(vector<Task>& tasks) {
    sortByProfit(tasks);

    int maxTime = 0;
    for (auto& t : tasks) {
        maxTime = max(maxTime, t.deadline);
    }

    vector<bool> slot(maxTime + 1, false);
    int totalProfit = 0;

    for (auto& task : tasks) {
        for (int t = task.deadline; t >= 1; t--) {
            if (!slot[t]) {
                _______________________ //在此处填入代码
                break;
            }
        }
    }
    return totalProfit;
}
```

A.

```cpp
slot[t] = true;
totalProfit += task.profit;
```

B.

```cpp
slot[t] = false;
totalProfit += task.profit;
```

C.

```cpp
slot[t] = true;
totalProfit = task.profit;
```

D.

```cpp
slot[t] = false;
totalProfit = task.profit;
```

### 第 15 题

下面代码实现了对两个数组表示的正整数的高精度加法（数组低位在前），则横线上应填写（ ）。

```cpp
vector<int> add(vector<int> a, vector<int> b) {
    vector<int> c;
    int carry = 0;
    for (int i = 0; i < a.size() || i < b.size(); i++) {
        if (i < a.size()) carry += a[i];
        if (i < b.size()) carry += b[i];
        _______________________ //在此处填入代码
    }
    if (carry) c.push_back(carry);
    return c;
}
```

A.

```cpp
c.push_back(carry / 10);
carry %= 10;
```

B.

```cpp
c.push_back(carry % 10);
carry /= 10;
```

C.

```cpp
c.push_back(carry % 10);
```

D.

```cpp
c.push_back(carry);
carry /= 10;
```

## 判断题

| 题号 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 答案 | F | T | T | F | T | T | T | F | T | F |

### 第 1 题

数组和链表都是线性表。链表的优点是插入删除不需要移动元素，并且能随机查找。

### 第 2 题

假设函数 `gcd()` 函数能正确求两个正整数的最大公约数，则下面的 `lcm(a, b)` 函数能正确找到两个正整数 `a` 和 `b` 的最小公倍数。

```cpp
int lcm(int a, int b) {
    return a / gcd(a, b) * b;
}
```

### 第 3 题

在单链表中，已知指针 `p` 指向要删除的结点（非尾结点），想在 $O(1)$ 删除 `p`，可行做法是用 `p->next` 覆盖 `p` 的值与 `next`，然后删除 `p->next`。

### 第 4 题

在求解所有不大于 $n$ 的素数时，线性筛法（欧拉筛）都应当优先于埃氏筛法使用，因为线性筛法的时间复杂度为 $O(n)$，低于埃氏筛法的 $O(n\log\log n)$。

### 第 5 题

二分查找仅适用于有序数据。若输入数据无序，当仅进行一次查找时，为了使用二分而排序通常不划算。

### 第 6 题

通过在数组的第一个、最中间和最后一个这3个数据中选择中间值作为枢轴（比较基准），快速排序算法可降低落入最坏情况的概率。

### 第 7 题

贪心算法在每一步都做出当前看来最优的局部选择，并且一旦做出选择就不再回溯；而分治算法将问题分解为若干子问题分别求解，再将子问题的解合并得到原问题的解。

### 第 8 题

以下 `fib` 函数计算第 $n$ 项斐波那契数（`fib(0)=0`，`fib(1)=1`），其时间复杂度为 $O(n)$。

```cpp
int fib(int n) {
    if (n <= 1) return n;
    return fib(n-1) + fib(n-2);
}
```

### 第 9 题

递归函数一定要有终止条件，否则可能会造成栈溢出。

### 第 10 题

使用贪心算法解决问题时，通过对每一步求局部最优解，最终一定能找到全局最优解。

## 编程题

### 3.1 编程题 1

试题名称：数字移动

时间限制：1.0 s

内存限制：512.0 MB

#### 题目描述

小 A 有一个包含 $N$ 个正整数的序列 $A=\{A_1,A_2,\ldots,A_N\}$，序列 $A$ 恰好包含 $\frac{N}{2}$ 对不同的正整数。形式化地，对于任意 $1 \le i \le N$，存在唯一一个 $j$ 满足 $1 \le j \le N$，$i \ne j$，$A_i=A_j$。

小 A 希望每对相同的数字在序列中相邻，为了实现这一目的，小 A 每次操作会选择任意 $i$（$1 \le i \le N$），将当前序列的第 $i$ 个数字移动到任意位置，并花费对应数字的体力。

例如，假设序列 $A=\{1,2,1,3,2,3\}$，小 A 可以选择 $i=2$，将 $A_2=2$ 移动到 $A_3=1$ 的后面，此时序列变为 $\{1,1,2,3,2,3\}$，耗费 $2$ 点体力。小 A 也可以选择 $i=3$，将 $A_3=1$ 移动到 $A_2=2$ 的前面，此时序列变为 $\{1,1,2,3,2,3\}$，花费 $1$ 点体力。

小 A 可以执行任意次操作，但他希望自己每次花费的体力尽可能小。小 A 希望你能帮他计算出一个最小的 $x$，使得他能够在每次花费的体力均不超过 $x$ 的情况下令每对相同的数字在序列中相邻。

#### 输入格式

第一行一个正整数 $N$，代表序列长度，保证 $N$ 为偶数。

第二行包含 $N$ 个正整数 $A_1,A_2,\ldots,A_N$，代表序列 $A$。且对于任意 $1 \le i \le N$，存在唯一一个 $j$ 满足 $1 \le j \le N$，$i \ne j$，$A_i=A_j$。

数据保证小 A 至少需要执行一次操作。

#### 输出格式

输出一行，代表满足要求的 $x$ 的最小值。

#### 样例

输入样例：

```text
6
1 2 1 3 2 3
```

输出样例：

```text
1
```

#### 样例解释

原 PDF 未给出样例解释。

#### 数据范围

对于 40% 的测试点，保证 $1 \le N, A_i \le 100$。

对于所有测试点，保证 $1 \le N, A_i \le 10^5$。

#### 参考程序

```cpp
#include <iostream>
using namespace std;
const int N = 100010;
int a[N];
int b[N];
int pos;

int main(){
    int n;
    cin >> n;
    for(int i = 0; i < n; i++){
        cin >> a[i];
    }
    int left = 1, right = 1e6, ans = 1e6;
    while(left <= right){
        int mid = (left + right) / 2;
        bool possible = true;
        pos = 0;
        for(int i = 0; i < n; i++){
            if(a[i]>mid){
                b[pos++]=a[i];
            }
        }
        for(int i = 0; i < pos; i += 2){
            if(b[i]!=b[i+1]){
                possible = false;
                break;
            }
        }
        if(possible){
            ans = mid;
            right = mid - 1;
        } else {
            left = mid + 1;
        }
    }
    cout << ans << endl;
    return 0;
}
```

### 3.2 编程题 2

试题名称：相等序列

时间限制：1.0 s

内存限制：512.0 MB

#### 题目描述

小 A 有一个包含 $N$ 个正整数的序列 $A=\{A_1,A_2,\ldots,A_N\}$。小 A 每次可以花费 1 个金币执行以下任意一种操作：

选择序列中一个正整数 $A_i$（$1 \le i \le N$），将 $A_i$ 变为 $A_i \times P$，$P$ 为任意质数；

选择序列中一个正整数 $A_i$（$1 \le i \le N$），将 $A_i$ 变为 $\frac{A_i}{P}$，$P$ 为任意质数，要求 $A_i$ 能被 $P$ 整除。

小 A 想请你帮他计算出令序列中所有整数都相同，最少需要花费多少金币。

#### 输入格式

第一行一个正整数 $N$，含义如题面所示。

第二行包含 $N$ 个正整数 $A_1,A_2,\ldots,A_N$，代表序列 $A$。

#### 输出格式

输出一行，代表最少需要花费的金币数量。

#### 样例

输入样例：

```text
5
10 6 35 105 42
```

输出样例：

```text
8
```

#### 样例解释

原 PDF 未给出样例解释。

#### 数据范围

对于 60% 的测试点，保证 $1 \le N, A_i \le 100$。

对于所有测试点，保证 $1 \le N, A_i \le 10^5$。

#### 参考程序

```cpp
#include <iostream>
using namespace std;
const int N = 100010;
int num[N][20];
int n, a[N];

void calc_prime_factor(int x){
    for(int i=2;i*i<=x;i++){
        if(x%i==0){
            int cnt=0;
            while(x%i==0){
                x/=i;
                cnt++;
            }
            num[i][cnt]++;
        }
    }
    if(x>1){
        num[x][1]++;
    }
}

int main(){
    scanf("%d",&n);
    for(int i=1;i<=n;i++){
        scanf("%d",&a[i]);
        calc_prime_factor(a[i]);
    }
    long long ans=0;
    for(int i=2;i<100001;i++){
        int pos = 0;
        for(int j=0;j<20;j++){
            pos += num[i][j];
        }
        num[i][0]=n-pos;
        int median_exponent=0;
        pos = 0;
        for(int j=0;j<20;j++){
            pos += num[i][j];
            if(pos*2>=n){
                median_exponent=j;
                break;
            }
        }
        for(int j=0;j<20;j++){
            ans+=num[i][j]*abs(j-median_exponent);
        }
    }
    printf("%lld\n",ans);
}
```
