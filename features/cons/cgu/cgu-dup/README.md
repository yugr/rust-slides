This snippet illustrates how CGUs may result in code duplication of local functions or generics:
function `foo` gets duplicated in all CGUs.
Optimizations like IPSCCP or ArgPromotion may cause MergeFunctions or ICF to fail to merge them
and cause code dup.
