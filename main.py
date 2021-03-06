'''Train CIFAR10 with PyTorch.'''
from __future__ import print_function

import collections
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.backends.cudnn as cudnn

import torchvision
import torchvision.transforms as transforms

import argparse
import csv
import os

from models import *
#from utils import progress_bar

from my_data_downloaders import my_CIFAR10

parser = argparse.ArgumentParser(description='PyTorch CIFAR10 Training')
parser.add_argument('--lr', default=0.1, type=float, help='learning rate')
parser.add_argument('--resume', '-r', action='store_true', help='resume from checkpoint')
parser.add_argument('-p', '--prediction-dir', help='where to write predictions')
parser.add_argument('--threshold', type=float, default=3)
parser.add_argument('--diff-dir', type=str, default=None)
parser.add_argument('--threshold-type', type=int,
                    help="0:none, 1: double side, 2: only below thresh, 3: only above thresh",
                    default=0)
args = parser.parse_args()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
best_acc = 0  # best test accuracy
start_epoch = 0  # start from epoch 0 or last checkpoint epoch

# Data
print('==> Preparing data..')
transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

trainset = my_CIFAR10(root='./data', train=True, download=True, transform=transform_train, diff_dir=args.diff_dir)
if args.threshold_type == 1:
    trainset_2 = [img for img in trainset if np.abs(img[3]) < args.threshold]
elif args.threshold_type == 2:
    trainset_2 = [img for img in trainset if img[3] < args.threshold]
elif args.threshold_type == 3:
    trainset_2 = [img for img in trainset if img[3] > args.threshold]
else:  # ==0
    trainset_2 = trainset

trainset = trainset_2
print('Training set size (threshold={}): {}'.format(args.threshold, len(trainset)))
target_counts = collections.Counter([m[1].item() for m in trainset])
print(target_counts)

trainloader = torch.utils.data.DataLoader(trainset, batch_size=128, shuffle=True, num_workers=2)

testset = my_CIFAR10(root='./data', train=False, download=True, transform=transform_test)
testloader = torch.utils.data.DataLoader(testset, batch_size=100, shuffle=False, num_workers=2)

classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

# Model
print('==> Building model..')
net = VGG('VGG16')
# net = ResNet18()
# net = PreActResNet18()
# net = GoogLeNet()
# net = DenseNet121()
# net = ResNeXt29_2x64d()
# net = MobileNet()
# net = MobileNetV2()
# net = DPN92()
# net = ShuffleNetG2()
# net = SENet18()
net = net.to(device)
if device == 'cuda':
    net = torch.nn.DataParallel(net)
    cudnn.benchmark = True

if args.resume:
    # Load checkpoint.
    print('==> Resuming from checkpoint..')
    assert os.path.isdir('checkpoint'), 'Error: no checkpoint directory found!'
    checkpoint = torch.load('./checkpoint/ckpt.t7')
    net.load_state_dict(checkpoint['net'])
    best_acc = checkpoint['acc']
    start_epoch = checkpoint['epoch']

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=args.lr, momentum=0.9, weight_decay=5e-4)

train_file = open('{}/train_CIFAR_VGG16_{}_{}.csv'.format(args.prediction_dir, args.threshold_type, args.threshold), 'w')
train_writer = csv.writer(train_file, delimiter=',')
train_writer.writerow(['imageID', 'epoch', 'label', 'prediction'])
test_file = open('{}/test_CIFAR_VGG16_{}_{}.csv'.format(args.prediction_dir, args.threshold_type, args.threshold), 'w')
test_writer = csv.writer(test_file, delimiter=',')
test_writer.writerow(['imageID', 'epoch', 'label', 'prediction'])

# Training
def train(epoch):
    print('\nEpoch: %d' % epoch)
    net.train()
    train_loss = 0
    correct = 0
    total = 0
    for batch_idx, (inputs, targets, label, _) in enumerate(trainloader):
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = net(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()

        for i in range(len(inputs)):
            row = [label[i].item(), epoch, targets[i].item(), predicted[i].item()]
            train_writer.writerow(row)

        #progress_bar(batch_idx, len(trainloader), 'Loss: %.3f | Acc: %.3f%% (%d/%d)'
        #    % (train_loss/(batch_idx+1), 100.*correct/total, correct, total))

def test(epoch):
    global best_acc
    net.eval()
    test_loss = 0
    correct = 0
    total = 0
    with torch.no_grad():
        for batch_idx, (inputs, targets, label, _) in enumerate(testloader):
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = net(inputs)
            loss = criterion(outputs, targets)

            test_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

            for i in range(len(inputs)):
                row = [label[i].item(), epoch, targets[i].item(), predicted[i].item()]
                test_writer.writerow(row)

            #progress_bar(batch_idx, len(testloader), 'Loss: %.3f | Acc: %.3f%% (%d/%d)'
            #    % (test_loss/(batch_idx+1), 100.*correct/total, correct, total))

    # Save checkpoint.
    acc = 100.*correct/total
    if acc > best_acc:
        print('Saving..')
        state = {
            'net': net.state_dict(),
            'acc': acc,
            'epoch': epoch,
        }
        if not os.path.isdir('{}/checkpoint'.format(args.prediction_dir)):
            os.mkdir('{}/checkpoint'.format(args.prediction_dir))
        torch.save(state, '{}/checkpoint/ckpt.t7'.format(args.prediction_dir))
        best_acc = acc
        print('epoch: {}, best acc: {}'.format(epoch, best_acc))


for epoch in range(start_epoch, start_epoch+1000):
    train(epoch)
    test(epoch)
