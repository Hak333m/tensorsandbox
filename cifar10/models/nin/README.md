# NIN-like variants of the Tensorflow CIFAR10 tutorial

In this directory, we test several models inspired by the [Network in
Network](https://arxiv.org/abs/1312.4400)paper.

These models differ from the traditional Alex style CNN, using inner layers
combining regular convolutions with 1x1 convolutions.
These fully convolutional models also replace the final FC nets by a global
average to obtain the class scores.

All these models also share some common features that have been tested on the
tutorial model itself as improving training and/or accuracy:
- pooling kernels have a size of 3, but a stride of 2,
- biases for the first and last layers are initialized with zeroes,
- biases for the other layers are initialized with 0.1 values.

The goal is to reach at least the same accuracy as the tutorial model:
- 81,0% after 10,000 iterations,
- 85,5% after 50,000 iterations,
- 86,0% after 100,000 iterations.

All models are trained using data augmentation and variables moving averages.

# NIN 0

Two level NIN network:

5x5x3x64 -> 1x1x64x64 -> 1x1x64x64
maxpoolx2
5x5x64x64 -> 1x1x64x64 -> 1x1x64x10
global average pool

Results:

@10,000:  70,9%
@50,000:  82,2%
@100,000: 83,4%

We use a significantly lower number of parameters than the traditional Alex
style architecture, but the processing cost increases.
The training also takes longer to converge.

# NIN 1

Just a minor deviation from the first model: we use more 1x1 filters in the
first NiN.

5x5x3x64 -> 1x1x64x96 -> 1x1x96x96
maxpoolx2
5x5x96x64 -> 1x1x64x64 -> 1x1x64x10
global average pool

Results:

@10,000:  69,7%
@50,000:  82,8%
@100,000: 83,7%

Almost no impact.
