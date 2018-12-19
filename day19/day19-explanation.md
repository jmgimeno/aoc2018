After making the flowchart for the code, it can be rearranged into:

````javascript
if (r0 == 0)
    r1 = 915;
else
    r1 = 10551315;
r3 = 1;
do {
    r5 = 1;
    do {
        r4 = r3 * r5;
        if (r4 == r1)
            r0 = r3 + r0;
        r5 = r5 + 1;
    } while (r3 <= r1);
    r3 = r3 + 1;
} while (r5 <= r1);
return r0;
````

The factorzation of 10551315 = 1 * 3 * 5 * 31 * 22691

````python
def mult(iter):
    m = 1
    for e in iter:
        m *= e
    return m
    
def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]
        
pset = list(powerset([3,5,31,22691]))
prods = [mult(ps) for ps in pset]
sum(prods) # = 17427456 is the answer !!!

````


