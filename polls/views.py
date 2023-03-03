from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from .models import Poll, Choice, Vote, MiningNode
from .forms import PollAddForm, EditPollForm, ChoiceAddForm
from django.template import loader
import datetime
import hashlib
import json
import uuid
import base64
import sys
import time
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.signing import Signer
from os.path import exists
import numpy as np
from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
import os
from configparser import ConfigParser

OUTBOUND_PORT = 10001
INBOUND_PORT = 10002


from django.template.defaulttags import register


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_required()
def polls_list(request):
    all_polls = Poll.objects.all()
    search_term = ''
    if 'name' in request.GET:
        all_polls = all_polls.order_by('text')

    if 'date' in request.GET:
        all_polls = all_polls.order_by('pub_date')

    if 'vote' in request.GET:
        all_polls = all_polls.annotate(Count('vote')).order_by('vote__count')

    if 'search' in request.GET:
        search_term = request.GET['search']
        all_polls = all_polls.filter(text__icontains=search_term)

    paginator = Paginator(all_polls, 6)  # Show 6 contacts per page
    page = request.GET.get('page')
    polls = paginator.get_page(page)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()
    print(params)
    context = {
        'polls': polls,
        'params': params,
        'search_term': search_term,
    }
    return render(request, 'polls/polls_list.html', context)


@login_required()
def list_by_user(request):
    all_polls = Poll.objects.filter(owner=request.user)
    paginator = Paginator(all_polls, 7)  # Show 7 contacts per page

    page = request.GET.get('page')
    polls = paginator.get_page(page)

    context = {
        'polls': polls,
    }
    return render(request, 'polls/polls_list.html', context)

@login_required()
def polls_add(request):
    if request.user.has_perm('polls.add_poll'):
        if request.method == 'POST':
            form = PollAddForm(request.POST)
            if form.is_valid:
                poll = form.save(commit=False)
                poll.owner = request.user
                poll.save()
                new_choice1 = Choice(
                    poll=poll, choice_text=form.cleaned_data['choice1']).save()
                new_choice2 = Choice(
                    poll=poll, choice_text=form.cleaned_data['choice2']).save()

                messages.success(
                    request, "Poll & Choices added successfully.", extra_tags='alert alert-success alert-dismissible fade show')

                return redirect('polls:list')
        else:
            form = PollAddForm()
        context = {
            'form': form,
        }
        return render(request, 'polls/add_poll.html', context)
    else:
        return HttpResponse("Sorry but you don't have permission to do that!")

@login_required
def polls_edit(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = EditPollForm(request.POST, instance=poll)
        if form.is_valid:
            form.save()
            messages.success(request, "Poll Updated successfully.",
                             extra_tags='alert alert-success alert-dismissible fade show')
            return redirect("polls:list")

    else:
        form = EditPollForm(instance=poll)

    return render(request, "polls/poll_edit.html", {'form': form, 'poll': poll})

@login_required
def polls_delete(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')
    poll.delete()
    messages.success(request, "Poll Deleted successfully.",
                     extra_tags='alert alert-success alert-dismissible fade show')
    return redirect("polls:list")

@login_required
def add_choice(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice added successfully.", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('polls:edit', poll.id)
    else:
        form = ChoiceAddForm()
    context = {
        'form': form,
    }
    return render(request, 'polls/add_choice.html', context)

@login_required
def choice_edit(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST, instance=choice)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice Updated successfully.", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('polls:edit', poll.id)
    else:
        form = ChoiceAddForm(instance=choice)
    context = {
        'form': form,
        'edit_choice': True,
        'choice': choice,
    }
    return render(request, 'polls/add_choice.html', context)

@login_required
def choice_delete(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('home')
    choice.delete()
    messages.success(
        request, "Choice Deleted successfully.", extra_tags='alert alert-success alert-dismissible fade show')
    return redirect('polls:edit', poll.id)

def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if not poll.active:
        return render(request, 'polls/poll_result.html', {'poll': poll})
    loop_count = poll.choice_set.count()
    context = {
        'poll': poll,
        'loop_time': range(0, loop_count),
    }
    return render(request, 'polls/poll_detail.html', context)

@login_required
def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choice_id = request.POST.get('choice')
    if not poll.user_can_vote(request.user):
        messages.error(
            request, "You already voted this poll!", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("polls:list")

    if choice_id:
        choice = Choice.objects.get(id=choice_id)
        vote = Vote(user=request.user, poll=poll, choice=choice)
        vote.save()
        print(vote)
        return render(request, 'polls/poll_result.html', {'poll': poll})
    else:
        messages.error(
            request, "No choice selected!", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("polls:detail", poll_id)
    return render(request, 'polls/poll_result.html', {'poll': poll})

@login_required
def endpoll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if poll.active is True:
        poll.active = False
        poll.save()
        return render(request, 'polls/poll_result.html', {'poll': poll})
    else:
        return render(request, 'polls/poll_result.html', {'poll': poll})

def createTestBlock(request):
    if(request.GET.get('create_Test_Block')):
        print("CEIUOJFOIEHJGFEOI")
    #choice = get_object_or_404(Choice, pk=choice_id)
    #poll = get_object_or_404(Poll, pk=choice.poll.id)
    #if request.user != poll.owner:
    #    return redirect('home')
    #choice.delete()
    #messages.success( request, "Choice Deleted successfully.", extra_tags='alert alert-success alert-dismissible fade show')
    return redirect('show_constitution')

def initializeNode(request):
    #check if blockdata exists on drive already
    # Create the object of the class blockchain
    #blockchain = Blockchain()
    miningnode = MiningNode()
    # # Connect with another node, otherwise you do not create any network!
    miningnode.connect_to_node()
    miningnode.requestLatestBlockHeight()
    time = str(datetime.datetime.now())
    #read config file
    config = ConfigParser()
    config.read('config.ini')

    #create initial block with hardcoded seed data
    block_height = 0
    genesis_hash = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f" #"We respect the results of this app"
    prev_hash= genesis_hash
    prev_proof = 1 #aka nonce
    #check for existing blocks on drive
    not_done_processing_blocks = True
    create_genesis_block = False
    data_from_datfile = {}
    print("begin processing blockdata")
    while(not_done_processing_blocks):
        file = "ledgerdata\\block"+str(block_height)+".dat"
        miningnode.mining_node_instance.latestBlockHeight = block_height
        #file = os.path.join(os.sep, "ledgerdata" + os.sep, "block"+str(block_height)+".dat")
        blockdata = ""
        missingFiles = 0
        print(file)
        #if existing file
        if(exists(file)):
            print(str(file))
            print("file exists")
            if(block_height==0):
                with open(file) as datfile:
                    print("data from datfile")
                    lines = datfile.readlines()
                    for line in lines:
                        my_json = base64.b64decode(line).decode("utf-8").replace("'", '"')
                        blockdata += my_json
                    #print(blockdata)
                    blockdata = json.loads(blockdata)
                    miningnode.chain.append(blockdata)
                    miningnode.previousBlock = blockdata
                    for tx in blockdata["transactions"]:
                        print(blockdata["transactions"].get(tx))
                        transaction = blockdata["transactions"].get(tx)
                        if transaction.get("subtype") == "ENTITY":
                            miningnode.legalDictionary[transaction["txid"]] = transaction["data"]["name"]
                print("genesis block data cant be verified until additional blocks are produced")
            else:
                with open(file) as datfile:
                    print("data from datfile")
                    lines = datfile.readlines()
                    for line in lines:
                        my_json = base64.b64decode(line).decode("utf-8").replace("'", '"')
                        blockdata += my_json
                    blockdata = json.loads(blockdata)
                    miningnode.chain.append(blockdata)
                    extractedBlockHeader = blockdata.header
                    extractedBlockTransactions = blockdata.transactions
                    #extractedBlockHeader = {"version":1, "proof":1, "prev_block_height":1, "prev_block_hash":"000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f", "this_block_hash":"000000000099d934ff763ae46a2a6c1726689c085ae165831eb3f1b60a8ce26f", "time": 1651964655.709359}
                    #extractedBlockTransactions = {"transactions":"data"}
                    #if merklerooted transactions of previous block = previous block's hash
                    if(miningnode.verifyBlock(miningnode.previousBlock["transactions"], extractedBlockHeader["prev_block_hash"])):
                        print("previous blocks merkle root hash is equal to this blocks prev_block_hash")
                        print("on to the next block")
                    else:
                        print("BAD BLOCKCHAIN!")
                        break
            block_height+=1
        else:
            #if no files
            print("blockheight")
            print(block_height)
            if create_genesis_block:
                print("create_genesis_block is true")
                # create first block
                miningnode.createGenesisBlock()
                #initialize config file
                config.add_section('blockchainstate')
                config.set('blockchainstate', 'latestBlockHeight', block_height)
                config.set('thisnodesuser', 'username', 'admin')
                config.set('thisnodesuser', 'userid', 'value3')
                with open('config.ini', 'w') as f:
                    config.write(f)
                create_genesis_block = False
            else:
                print("create_genesis_block is false")
                miningnode.requestBlockData(block_height)
            block_height+=1
            #actually add initial block data to chain upon next iteration of chain
            if((miningnode.latestBlockHeight <= block_height) and (block_height >= 1)):
                print("miningnode.latestBlockHeight == block_height")
                #stop processing blocks when no blockX.dat files available to process and blockheight is > 1
                not_done_processing_blocks = False
    miningnode.latestBlockHeight = block_height-1
    print("latest block height tried")
    print(miningnode.latestBlockHeight)
    print("prev block height")
    print(miningnode.chain[0]["header"]["prev_block_height"])
    context = {
            "blockID":miningnode.chain[0]["header"]["prev_block_height"],
            "transactions":miningnode.chain[0]["transactions"]
        }
    print(len(miningnode.chain))
    if miningnode.latestBlockHeight >= len(miningnode.chain):
        if miningnode.latestBlockHeight == 1:
            miningnode.latestBlockHeight = 0
        else:
            miningnode.latestBlockHeight = miningnode.latestBlockHeight-1
        print("latest block height")
        print(miningnode.latestBlockHeight)
        context = {
            "blockID":miningnode.chain[miningnode.latestBlockHeight]["header"]["prev_block_height"],
            "transactions":miningnode.chain[miningnode.latestBlockHeight]["transactions"]
        }
    else:
        print("somethings broken")
    #print(context)
    #print(miningnode.legalDictionary)
    print("DONE PROCESSING BLOCKDATA. blockheight:")
    print(str(block_height))

    return render(request, "polls/show_constitution.html", context)


@register.filter
def get_entity_data(dictionary, key):
    value = dictionary.get(key)
    #print(value)
    if value.get("subtype") == "ENTITY":
        return value["data"]["name"]+": "+value["data"]["desc"]
    elif value.get("subtype") == "LAW":
        return "LAW ID "+value["txid"]+": "+value["data"]["desc"]
    else:
        return value["txid"]
