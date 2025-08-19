# 连续代数——微积分图形解释[选自《普适性场方程与角动量不守恒》](/pdfs/6e342834-6f72-4b22-b9d4-eef574a39351.pdf)
目前，对微积分存在的合理性有两种解释：主流的标准分析和鲁滨逊的非标准分析。标准分析是一套诡辩术。极限概念超越了函数概念；$\lim_{x \to 0}$  中x取值不明；$\varepsilon -\delta $语言中$\varepsilon$取值不明；邻域半径r取值不明；0和无穷小不区分。鲁滨逊的非标准分析就更离谱了。本章介绍我自行研究的一套解释体系。我将它命名为连续代数。
## 数学思想
微积分不再看作数学分析而是把它当作对实数的代数来看。代数和几何是一一对应的。因此我们可以通过研究几何来研究微积分。从上帝视角，眼睛像显微镜一样在识海放大几何图形的微观细节，从区分两点的方法入手推演整个理论体系。
## 全序集合的几何形状
![](/images/2854a381-0486-45a2-81de-e70e58556556.jpg)
**[全序关系]**
集合中的每一个点有且只有两个接口，按照特定的关系链接其他点，从任意一点都可以到达集合中的其他点，我们把这种关系称为全序关系。这种集合称为全序集合。

**[邻点]**
    具有全序关系的集合，点的接口所链接的点称为邻点。若称其中一个邻点为左邻点，另一个称为右邻点。没有邻点的接口称为开放的。

**[线]**
具有全序关系的集合，有两个接口开放，则称该集合为线。

**[圈]**
具有全序关系的集合，每个接口都有邻点，则称该集合为圈。

    具有全序关系的集合只有两种几何形态，要么为线，要么为圈。


## 数集与结构
为了加强对无穷大的认识，让读者明白无穷大与集合内的其他元素一样是构造的，我们用循环群来定义数集，又因为我们把正号、负号、乘号、除号理解成数的结构。因此纯粹的数集用加法半群定义，只在不严格区分结构的时候才用加法群定义。

**[整数]**
    由1生成的加法半群称为整数，记为$Z^+$。相应加法群记为Z。

**[有理数]**
    由1、$\tfrac{1}{2}$、$\tfrac{1}{3}$、……、$\tfrac{1}{\lfloor \infty \rfloor }$生成的加法半群称为有理数记为$Q^+$。相应加法群记为Q。其中${\lfloor \infty \rfloor \in Z^+}$。


**[实数]**
    由$\varepsilon$ 生成的加法半群称为实数记为$R^+$。相应加法群记为R。

## 量度
**[量度]** 特定位置的数轴称为量度。不同位置的数轴，量度单位不同，不能直接比较，需要换算。

举一个例子。在X-Y二维空间中，假设X轴与Y轴的量度单位相同，则$\infty_Y$=$\infty_X$，假如Y轴的量度单位是X轴的3倍，即$y=3x$,则$\infty_Y$=3$\infty_X$。
    
    通常，我们将不同数集$Z^+,Q^+,R^+$直接比较是假定在同一量度，即同一数轴上比较。
## 无穷小与无穷大   
**[无穷小与无穷大]**
    数集的最小值称为无穷小，数集的最大值称为无穷大。

不同数集，它所能表示的无穷小和无穷大是不同的。实数的无穷小为$\varepsilon $,实数的无穷大为$\infty$。整数的无穷小为1，整数的无穷大是对实数的无穷大向下取整，记为$\lfloor \infty \rfloor$ 。有理数的无穷小为$\tfrac{1}{\lfloor \infty \rfloor}$,有理数的无穷大为$\lfloor \infty \rfloor$。实数的$\varepsilon=\tfrac{1}{\infty}$。由于$\lfloor \infty \rfloor\leq \infty$,所以$\varepsilon \leq \tfrac{1}{\lfloor \infty \rfloor}$。
## 基数
**[基数]**
    数集中元素的个数称为基数。

整数的基数为$\lfloor \infty \rfloor$,偶数的基数为$\lfloor \tfrac{\infty}{2} \rfloor$,奇数的基数为$\lfloor \tfrac{\infty+1}{2} \rfloor$。
有理数的基数小于$\lfloor \infty \rfloor^2$，实数的基数为$\infty^2$。
## 小数
    十进制小数不能表示所有分数，是有理数的一部分。

$\tfrac{1}{3}$的十进制小数表示用有序对$\langle a,b\rangle$,a表示商，b表示相应的余数。
    
$$
            \tfrac{1}{3}
= \langle 0.3,\tfrac{1}{10}\rangle\\
=\langle 0.33,\tfrac{1}{10^2}\rangle\\
=\langle 0.333\cdots ,\tfrac{1}{10^\infty}\rangle
$$

十进制小数的无穷小也是$\tfrac{1}{10^\infty}$,所以当 $\tfrac{1}{3}$表示成$0.333\cdots$无限循环小数时，还有一个余数无穷小。

    $ 1\neq 0.999\cdots$

## 离散与连续
**[连续集与离散集]**
    设定实数为连续集。实数的无穷小为$\varepsilon $,无穷小大于$\varepsilon $的数集称为离散集。

大概率上，$ \tfrac{1}{\lfloor \infty \rfloor  }\gt\varepsilon$,所以有理数是离散集。$1 \gt\varepsilon $,所以整数是离散集。

**[连续代数与离散代数]**
    研究连续集的代数运算称为连续代数。研究离散集的代数运算称为离散代数。


## 点的宽度与两邻点距离
![](/images/9ab57ebf-1619-4506-a471-d524e9c7bdcc.jpg)
由图可知，实数的点的宽度和两邻点的距离都是$\varepsilon $。
## 商函数
**[商函数]**
    设函数$y=f(x)$,点$\lt x_0,f(x_0)\gt$和点$ \lt x,f(x)\gt$分别是函数图形$y=f(x)$上的两点，则
    
$$
        \dfrac{f(x)-f(x_0)}{x-x_0}
$$
称为商函数，记为$L(x-x_0)$，表示Y轴与X轴两点距离之比。设Y轴两点距离$\Delta y$,X轴两点距离$\Delta x$：
$$
       \Delta x= x-x_0, \\
       \Delta y=f(x)-f(x_0)=f(x_0+\Delta x)-f(x_0)
$$
    故()式也可写成$$
    L(\Delta x)=\dfrac{\Delta y}{\Delta x}\]或\[L(\Delta x)=\dfrac{f(x_0+\Delta x)-f(x_0)}{\Delta x}$$

进一步，可以将$x_0$替换成自变量x，有：

$$
    L(\Delta x)=\dfrac{f(x+\Delta x)-f(x)}{\Delta x}
$$

## 导函数
**[导函数]**
    设商函数为()式，当$\Delta x=0$时，即：
    
$$
L(\Delta x)\Bigg|_{\Delta x=0}$$

$$=\dfrac{f(x+\Delta x)-f(x)}{\Delta x} \Bigg|_{\Delta x=0}
$$

称为导函数，表示函数图形$y=f(x)$上点$\lt x,f(x)\gt$处的Y轴与X轴点的宽度之比，记作 y',f'(x),$\frac{d y}{d x}$或$\frac{d f(x)}{d x}$。

*设$y=x^2$,求y的导函数*
$$
        y'=\frac{(x+h)^2-x^2}{h}\Bigg|_{h=0} $$

$$
        =\frac{x^2+2xh+h^2-x^2}{h}\Bigg|_{h=0}$$

$$
        =\frac{(2x+h)h}{h}\Bigg|_{h=0}$$

$$
      =2x+h\Bigg|_{h=0} =2x
$$

## 0作为除数

    0可以作为除数。0作为除数时，被除数必须是0。$\tfrac{0}{0}$的结果是导函数。

已知:$0*a=0,a \in R$,移项，得：$\tfrac{0}{0}=a $。从例子中可以看出求导过程中分式都是$\tfrac{0}{0}$型的，求导的关键在于把零因子同时从分子和分母中消去。

    $\tfrac{\sin x}{x}\Bigg|_{x=0}=a,a \in R$。


*求$y=\sin x$的导函数*
$$
    y'=\frac{\sin (x+h)-\sin x}{h}\Bigg|_{h=0}$$

$$
    =\frac{1}{h}\cdot 2\cos\big(x+\tfrac{h}{2}\big)\sin\tfrac{h}{2}\Bigg|_{h=0}$$

$$
    =\cos\big(x+\tfrac{h}{2}\big)\cdot\frac{\sin\tfrac{h}{2}}{\tfrac{h}{2}}\Bigg|_{h=0}$$

$$
    =a\cos x,a \in R
$$


*求$y=\cos x$的导函数*

$$
       y'=\frac{\cos (x+h)-\cos x}{h}\Bigg|_{h=0}$$

$$
       =-\frac{1}{h}\cdot 2\sin\big(x+\tfrac{h}{2}\big)\sin\tfrac{h}{2}\Bigg|_{h=0}$$

$$
       =-\sin\big(x+\tfrac{h}{2}\big)\cdot\frac{\sin\tfrac{h}{2}}{\tfrac{h}{2}}\Bigg|_{h=0}$$

$$
       =-a\sin x,a \in R
$$

## 待定系数泰勒展开求导法
假定我们不知道定理,可以用待定系数泰勒展开求例子和例子中函数的导函数。$\sin x$的待定系数泰勒展开
$$\sin x = \sin 0 +a_1x+a_2x^2+a_3x^3+\dots +a_{\infty}x^\infty,(a_1,a_2,a_3,\dots,a_{\infty} \in R)$$
$\cos x$的待定系数泰勒展开
$$\cos x = \cos 0 +b_1x+b_2x^2+b_3x^3+\dots +b_{\infty}x^\infty,(b_1,b_2,b_3,\dots,b_{\infty} \in R)$$
在$\sin x$和$\cos x$求导过程中,泰勒展开式从大等于2次的项因其中一个因子与分母消去，另一个因子使分子归零，对求导结果无贡献，所以下面展示的过程只代入泰勒展开前两项，以便更简洁易懂。

*$\sin x$求导：*

$$
    \sin x'=\frac{\sin (x+h)-\sin x}{h}\Bigg|_{h=0}$$

$$
    =\frac{\sin x\cos h+\cos x \sin h-\sin x}{h}\Bigg|_{h=0}$$

$$
    =\frac{\sin x\cdot(\cos 0 +b_1h)+\cos x  \cdot(\sin 0 +a_1h)-\sin x}{h}\Bigg|_{h=0}$$

$$
    =b_1\sin x +a_1\cos x
$$
*$\cos x$求导：*

$$
    \cos x'=\frac{\cos (x+h)-\cos x}{h}\Bigg|_{h=0}$$

$$
    =\frac{\cos x\cos h-\sin x \sin h-\cos x}{h}\Bigg|_{h=0}$$

$$
    =\frac{\cos x\cdot(\cos 0 +b_1h)-\sin x  \cdot(\sin 0 +a_1h)-\cos x}{h}\Bigg|_{h=0}$$

$$
    =b_1\cos x -a_1\sin x
$$
 为了进一步消去待定系数，找到关系式:$$\sin x^2+\cos x^2=1$$
 两边同时求导：$$2\sin x\sin x'+2\cos x\cos x'=0$$将$\sin x$和$\cos x$求导结果代入：
 
$$
\sin x(b_1\sin x +a_1\cos x)+\cos x(b_1\cos x -a_1\sin x)=0$$

$$ b_1+a_1(\sin x \cos x -\cos x \sin x)=0$$
$$ b_1=0
$$

 可以看出两种求导方法结果是一样的，相互验证了理论的准确性。
 ## e的等价刻画
$$e=(1+\varepsilon )^{\tfrac{1}{\varepsilon }}=\big(1+\tfrac{1}{\infty}\big)^\infty$$
*求$y=e^x$的导函数*
$e^x$的待定系数泰勒展开
$$e^x = e^0 +a_1x+a_2x^2+a_3x^3+\dots +a_{\infty}x^\infty,(a_1,a_2,a_3,\dots,a_{\infty} \in R)$$
$$
        y'=\frac{e^{x+h}-e^x}{h}\Bigg|_{h=0}$$

$$
        =\frac{e^x(e^h-1)}{h}\Bigg|_{h=0}$$

$$
        =\frac{e^x(e^0 +a_1h-1)}{h}\Bigg|_{h=0}$$

$$
        =a_1e^x
$$

 ## 异常导函数
**[异常导函数]**
    当$\Delta x=\varepsilon $时，即：
    
$$
L(\Delta x)\Bigg|_{\Delta x=\varepsilon }
$$

$$=\dfrac{f(x+\Delta x)-f(x)}{\Delta x} \Bigg|_{\Delta x=\varepsilon }
$$

称为异常导函数，表示函数图形$y=f(x)$上点$\lt x,f(x)\gt$与邻点$\lt x+\varepsilon ,f(x+\varepsilon )\gt$处的Y轴与X轴两点距离之比
*求函数$y = a^x, \quad a\gt0,  a\neq 1$的异常导函数*
$$
        y'=\frac{a^{x+h}-a^x}{h}\Bigg|_{h=\varepsilon }$$

$$
        =\frac{a^x(a^h-1)}{h}\Bigg|_{h=\varepsilon }$$

$$
$$
    令$a^h-1=t$,则$h=\log_a(1+t) $,当$t=0$时，$h=0$,所以当$h=\varepsilon_h$时$t=\varepsilon_t$,所以
$$
        y'=a^x\cdot\frac{t}{\log_a(1+t)}\Bigg|_{t=\varepsilon }$$$$
        =a^x\cdot \frac{1}{\log_a(1+\varepsilon )^{\tfrac{1}{\varepsilon }}}$$$$=a^x\ln a
$$

*求函数$y=\log_ax,  \quad a\gt0,a\neq 1$的异常导函数*
$$
    y'=\frac{\log_a(x+h)-\log_ax}{h}\Bigg|_{h=\varepsilon }$$

$$
    =\frac{1}{h}\log_a\frac{x+h}{x}\Bigg|_{h=\varepsilon }$$

$$
    =\frac{1}{x}\frac{x}{h}\log_a\big(1+\frac{h}{x}\big)\Bigg|_{h=\varepsilon }$$

$$
    =\frac{1}{x\ln a}
$$

## 微分均值定理

**[连续区间]**
    隶属实数集的一条线段称为连续区间。假设该线段的左右两端分别记为a和b,则区间表示为$[a,b]$，去除a的线段表示为$( a,b] $或$ [a+\varepsilon ,b ]$ 去除b的线段表示为$[a,b ) $或$[a,b-\varepsilon  ] $,两端同时去除a和b，则表示为(a,b )或$[a+\varepsilon ,b-\varepsilon  ]$  。由此可知任意线段都可以表示成闭区间。

**[微分]**
    设函数$y=f(x)$，在连续区间[a,b ] 上有定义,函数图形上任意一点的宽度或两邻点的距离称为微分。X轴方向的的微分记为dx，Y轴方向的微分记为dy。

**[解析函数]**
    设函数$y=f(x)$在连续区间[a,b ] 上可导，即可求导函数或异常导函数，则称该函数为解析函数。

**[微分均值定理]**
    设解析函数$y=f(x)$，在连续区间[a,b ] 上有定义，那么至少存在一点x，(a<x<b),使等式
    
$$
        \frac{f(b)-f(a)}{b-a}=f'(x)dx
$$
    成立。其中f(b)-f(a)是函数y增量，b-a是自变量x增量。f'(x)dx是y增量均值。dx是点位x的微分。f'(x)是点位x的相对增量。该定理的几何意义是增量均值必在统计区间中。

## 微商定理
**[微商定理]**
    设解析函数$y_1=f(x)$及$y_2=F(x)$在连续区间[a,b ] 上有定义，有等式
    
$$
        \frac{d y_1}{d y_2}=\frac{f'(x)}{F'(x)}
$$
    成立。
      $d y_1=f'(x)d x,\quad d y_2=F'(x)d x$  ,两式相除，得之。

## 积分定理
**[积分定理]**
    设解析函数$y=f(x)$，在连续区间[a,b ] 上有定义，有等式
    
$$
        f(b)-f(a)=\int _{a}^{b}f'(x)dx
$$
    成立。其中f(b)-f(a)是函数y增量，任意一点x，$(a\leq x \leq b)$，f'(x)dx是点x上的y增量。dx是点位x的微分。f'(x)是点位x的相对增量。该定理的几何意义是在统计区间累加所有点的y增量。
\end{thm}
从()式和()式可以看出微积分的本质原理是一样的，不定积分、定积分及反常积分等都是其变种。该微积分存在的合理性解释只承认牛顿-莱布尼茨公式，不再分黎曼积分和勒贝格积分。而是把求导、微分、微商、积分当成连续集的结构来研究，由此本质上只研究解析函数，从不讨论函数的连续性问题。