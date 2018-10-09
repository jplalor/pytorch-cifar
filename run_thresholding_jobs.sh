#!/usr/bin/env bash

# baseline
#sbatch -p 1080ti-short --gres=gpu:2 --mem=80000 --output=logs/cifar_threshold_baseline.log --wrap="python -u main.py --threshold 0 --diff-dir /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/ --threshold-type 0 -p /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/thresholds/"

# test first
#sbatch -p titanx-short --gres=gpu:2 --mem=80000 --output=logs/cifar_threshold_test.log --wrap="python -u main.py --threshold 2 --diff-dir /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/ --threshold-type 1 -p /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/thresholds/"

for t in $(seq 0 0.5 8)
do
sbatch -p 1080ti-short --gres=gpu:2 --mem=80000 --output=logs/cifar_threshold_$t.log --wrap="python -u main.py --threshold $t --diff-dir /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/ --threshold-type 1 -p /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/thresholds/"
done

for t in $(seq -3.25 0.5 8)
do
sbatch -p 1080ti-short --gres=gpu:2 --mem=80000 --output=logs/cifar_threshold_upper_bound_$t.log --wrap="python -u main.py --threshold $t --diff-dir /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/ --threshold-type 2 -p /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/thresholds/"
sbatch -p 1080ti-short --gres=gpu:2 --mem=80000 --output=logs/cifar_threshold_lower_bound_$t.log --wrap="python -u main.py --threshold $t --diff-dir /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/ --threshold-type 3 -p /mnt/nfs/work1/hongyu/lalor/data/irt-svi/CIFAR/thresholds/"
done
