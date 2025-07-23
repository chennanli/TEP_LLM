
这是TE开源的一个**Python interface to a modified Fortran program of the Tennessee Eastman Process (TEP) Control Test Problem provided by gmxavier**，我希望 run the TEP simulation, including its dynamic behaviors and faults, directly from Python without needing a MATLAB license or installation. This maintains the fidelity of the original TEP dynamics, which are well-established for benchmarking。

## 分析任务指令

请帮我深度分析这个Other_Repo/tep2py-master和Other_Repo/tennessee-eastman-profBraatz-master文件夹里的项目，他是我下载的前面说的TEP的Python接口和TEP的Fortran文件。
我需要能够运行他，在python中运行TEP的动态行为和故障。请按照以下结构进行**系统性分析**：

### 1. 项目架构深度解析
**请详细分析以下关键架构要素：**

- **入口点定位**：找到项目的主启动文件和命令行接口实现
- **Python服务架构**：解释一下python如何使用这些fortran文件
- **如何运行和改写fortan code**：给我建议需不需要把fortran code改写为python，还是不需要因为很容易运行


### 2. 其他LLM给的建议
ow to use:
▪
Obtain Fortran Source: Clone or download the Fortran 77 codes for the TEP from camaramm/tennessee-eastman-profBraatz. You will primarily need temain_mod.f (for closed-loop simulation) and teprob.f (the subprogram for the simulation codes).
▪
Build Python Extension: Follow the instructions in the tep2py repository to build the Fortran program from source using f2py. The command provided is python -m numpy.f2py -c temain_mod-smart.pyf src/tep/temain_mod.f src/tep/teprob.f.
▪
Run Simulations: Instantiate the tep2py object and run simulations. You can retrieve simulated data as a DataFrame.
▪
Trigger Faults: The underlying Fortran code wrapped by tep2py allows you to implement any of the 21 programmed disturbances (faults) by setting specific IDV flags. For example, IDV(2)=1 would implement disturbance 2. You will need to programmatically adjust the inputs to tep2py to trigger these faults.。


## git 项目解释，作者自己写的
This repository provides a Python interface to a modified Fortran program of the Tennessee Eastman Process (TEP) Control Test Problem provided by gmxavier. Users of this modified version should cite it as:

G. M. Xavier and J. M. de Seixas, "Fault Detection and Diagnosis in a Chemical Process using Long Short-Term Memory Recurrent Neural Network", 2018 International Joint Conference on Neural Networks (IJCNN), 2018, pp. 1-8, doi: 10.1109/IJCNN.2018.8489385.
In order to use it properly, you should build the fortran program from source using f2py. You may refer to the instructions below to build it yourself or, if you are on a linux system, you may try the file provided in this repository, which was compiled on a linux machine according to:

$ uname -srvmpio
Linux 4.15.0-51-generic #55-Ubuntu SMP Wed May 15 14:27:21 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
How to use

# modules
import numpy as np 
from tep2py import tep2py

# matrix of disturbances
idata = np.zeros((5,20))  

# instantiate tep2py object for given `idata`
tep = tep2py(idata)

# run simulation
tep.simulate()

# retrieve simulated data as DataFrame
print(tep.process_data)

# retrieve table of disturbances
print(tep.info_disturbance)

# retrieve table of variables
print(tep.info_variable)
Wrap Fortran code in Python using f2py (following the smart way)

See this for more details.

Create a signature file from fortran source code by running:

$ python -m numpy.f2py src/tep/temain_mod.f src/tep/teprob.f -m temain_mod -h temain_mod-auto.pyf
Explicit what are the intent of the arguments of the target functions (use intent(in) and intent(out) attribute) . You should do this by editing the signature file temain_mod-auto.pyf.

The final version is:

subroutine temain(npts,nx,idata,xdata,verbose) ! in :temain_mod:temain.f
        integer, intent(in) :: npts
        integer, intent(in) :: nx
        integer dimension(nx,20), intent(in), depend(nx) :: idata
        double precision dimension(nx,52),depend(nx), intent(out) :: xdata
        integer, intent(in) :: verbose
Build the extension module by running:

python -m numpy.f2py -c temain_mod-smart.pyf src/tep/temain_mod.f src/tep/teprob.f
Import the module in python:

import temain_mod

## 总之，我希望能利用好这两个现有的github repo，能详细的告诉我，如何运行这个dynamic simulation，能让我在python中直接运行这个dynamic simulation，能够看到如何trigger fault可以用它来进行下一步的学习。请给予建议。