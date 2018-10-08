#!/usr/bin/env bash


# test first
sbatch -p titanx-short --gres=gpu:2 --mem=80000 --output=logs/cifar_threshold_$t.log --wrap="python -u main.py --threshold 2 --diff-dir /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/ --threshold-type 1 -p /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/thresholds/"

#for t in $(seq -6 0.1 6)
#do
#sbatch -p titanx-short --gres=gpu:2 --mem=80000 --output=logs/cifar_threshold_$t.log --wrap="python -u main.py --threshold -1 --diff-dir /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/ --threshold-type 1 -p /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/thresholds/"
#sbatch -p titanx-short --gres=gpu:2 --mem=80000 --output=logs/cifar_threshold_upper_bound_$t.log --wrap="python -u main.py --threshold -1 --diff-dir /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/ --threshold-type 2 -p /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/thresholds/"
#sbatch -p titanx-short --gres=gpu:2 --mem=80000 --output=logs/cifar_threshold_lower_bound_$t.log --wrap="python -u main.py --threshold -1 --diff-dir /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/ --threshold-type 3 -p /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/thresholds/"
#done