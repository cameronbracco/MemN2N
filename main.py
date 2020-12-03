import os

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import optim

from model import MemN2N
from helpers import dataloader, get_fname, get_params


def train(train_iter, model, optimizer, epochs, max_clip, valid_iter=None):
    print("attempting to train?", epochs)
    total_loss = 0
    valid_data = list(valid_iter)
    valid_loss = None
    next_epoch_to_report = 5
    pad = model.vocab.stoi['<pad>']

    print("Do I see this?", train_iter.repeat)

    epoch_count = 0
    while True:
        print("In the num_epoch loop", epoch_count) # TODO Could make this a finite loop instead of infinite lol
        for _, batch in enumerate(train_iter, start=1):
            # print("attempting to looop in the innnner", epoch_count)
            story = batch.story
            query = batch.query
            answer = batch.answer

            optimizer.zero_grad()
            outputs = model(story, query)
            loss = F.nll_loss(outputs, answer.view(-1), ignore_index=pad, reduction='sum')
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_clip)
            optimizer.step()
            total_loss += loss.item()

            # linear start
            if model.use_ls:
                loss = 0
                for k, batch in enumerate(valid_data, start=1):
                    story = batch.story
                    query = batch.query
                    answer = batch.answer
                    outputs = model(story, query)
                    loss += F.nll_loss(outputs, answer.view(-1), ignore_index=pad, reduction='sum').item()
                loss = loss / k
                if valid_loss and valid_loss <= loss:
                    model.use_ls = False
                else:
                    valid_loss = loss

        if epoch_count == next_epoch_to_report:
            print("#! epoch {:d} average batch loss: {:5.4f}".format(
                int(epoch_count), total_loss / len(train_iter)))
            next_epoch_to_report += 5
        if int(train_iter.epoch) == train_iter.epoch:
            print("Finished an epoch?", train_iter.epoch)
            epoch_count += 1
            total_loss = 0
        if epoch_count == epochs:
            print("Looks like we're outside of epochs")
            break


def eval(test_iter, model):
    total_error = 0

    for k, batch in enumerate(test_iter, start=1):
        story = batch.story
        query = batch.query
        answer = batch.answer
        outputs = model(story, query)
        _, outputs = torch.max(outputs, -1)
        total_error += torch.mean((outputs != answer.view(-1)).float()).item()

        if test_iter.epoch >= 1:
            break
    print("#! average error: {:5.1f}".format(total_error / k * 100))


def run(config):
    print("#! preparing data...")
    train_iter, valid_iter, test_iter, vocab = dataloader(config.batch_size, config.memory_size,
                                                          config.task, config.joint, config.tenk)

    print("#! instantiating model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MemN2N(get_params(config), vocab).to(device)

    if config.file:
        with open(os.path.join(config.save_dir, config.file), 'rb') as f:
            if torch.cuda.is_available():
                state_dict = torch.load(f, map_location=lambda storage, loc: storage.cuda())
            else:
                state_dict = torch.load(f, map_location=lambda storage, loc: storage)
            model.load_state_dict(state_dict)

    if config.train:
        print("#! training...")
        optimizer = optim.Adam(model.parameters(), config.lr)
        train(train_iter, model, optimizer, config.num_epochs, config.max_clip, valid_iter)
        if not os.path.isdir(config.save_dir):
            os.makedirs(config.save_dir)
        print("Finished training")
        torch.save(model.state_dict(), os.path.join(config.save_dir, get_fname(config)))

    print("#! testing...")
    with torch.no_grad():
        eval(test_iter, model)
