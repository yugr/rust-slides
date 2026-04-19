Some info on architecture of branch predictors in x86 processors.

[Reverse Engineering of Intel’s Branch Prediction](https://www.its.uni-luebeck.de/fileadmin/files/theses/BA_NickMahling_ReverseEngineeringIntelsBranchPrediction.pdf)
suggests that Intel cores
  - use path-based history (i.e. combination of source/target addresses
    for N last _taken_ branches)
  - are not influenced by never-taken branches

[Indirector: High-Precision Branch Target Injection Attacks Exploiting the Indirect Branch Predictor](https://www.usenix.org/system/files/usenixsecurity24-li-luyi.pdf)
provides rev-enged formulas for PHR computation and
state that only taken branches are used.
It also cites
  - [Half&Half: Demystifying Intel’s Directional Branch Predictors for Fast, Secure Partitioned Execution](https://cseweb.ucsd.edu/~tullsen/halfandhalf.pdf) (2023)
  - [Pathfinder: High-Resolution Control-Flow Attacks Exploiting the Conditional Branch Predictor](https://cseweb.ucsd.edu/~dstefan/pubs/yavarzadeh:2024:pathfinder.pdf)

which also confirm that only taken branches are considered in GHR.

Finally [The AMD Branch (Mis)predictor](https://grsecurity.net/amd_branch_mispredictor_just_set_it_and_forget_it)
cites "AMD Software Optimization Guide" that also claims that
```
Global history is not updated for never-taken branches.
...
Conditional branches that have not yet been discovered to be taken are not marked in the BTB.
These branches are implicitly predicted not-taken.
```

[Exploiting Inaccurate Branch History in Side-Channel Attack](https://arxiv.org/pdf/2506.07263v1)
confirms that never taken ("not recorded") branches are also ignored
on Cortex cores (A72, A76, A78).

This means that _probably_ Rust's runtime checks should not pollute BP tables
(at least on modern x86/AArch64 cores).
