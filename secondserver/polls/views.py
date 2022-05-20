from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from .models import OUTBOUND_PORT, Poll, Choice, Vote, MiningNode
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


OUTBOUND_PORT = 10002
INBOUND_PORT = 10001

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




def initializeNode(request):
    #check if blockdata exists on drive already
    # Create the object of the class blockchain
    #blockchain = Blockchain()
    miningnode = MiningNode()
    time = str(datetime.datetime.now())
    #create initial block
    block_height = 0
    prev_hash="000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
    prev_proof = 1 #aka nonce

    print("begin looking for nodes")

    
    #miningnode.send_to_nodes('{"message": "hoi from node 1"}')
    #check for existing blocks on drive
    not_done_processing_blocks = True
    data_from_datfile = {}
    print("begin processing blockdata")
    while(not_done_processing_blocks):
        file = "block"+str(block_height)+".dat"
        blockdata = ""
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
            print("blockheight")
            print(block_height)
            if(block_height==0):
                #if no existing blocks, create first block
                # nodeversion, proof, prev_block_height, prev_hash
                #miningnode.createBlock(miningnode.miningnodeversion, 1, initial_block_height, initial_prev_hash)
                #automatically create first entity (users), then create citizen so there is at least 1 transaction, genesis block hash same as vouching user id
                miningnode.createNewEntity(prev_hash, {"name":"USER", "type":"noun", "desc":"a human who is using this software as intended"})
                miningnode.createNewCitizen(prev_hash, {"name":"admin", "age":33})
                #then create the other initial entities using newly generated USERID
                miningnode.createNewEntity(miningnode.tempUser, {"name":"LAW", "type":"noun", "desc":"a law created using this software"})
                miningnode.createNewEntity(miningnode.tempUser, {"name":"DISPUTE", "type":"noun", "desc":"a dispute between two users created using this software"})
                miningnode.createNewEntity(miningnode.tempUser, {"name":"POINTS", "type":"noun", "desc":"the default currency"})    
                miningnode.createNewEntity(miningnode.tempUser, {"name":"INITIATE", "type":"verb", "desc":"initiating a transaction with this software"})
                miningnode.createNewEntity(miningnode.tempUser, {"name":"STEAL", "type":"verb", "desc":"take something you dont own without consent"})
                miningnode.createNewEntity(miningnode.tempUser, {"name":"VOTE", "type":"verb", "desc":"impose your will on society"})
                miningnode.createNewEntity(miningnode.tempUser, {"name":"OWN", "type":"verb", "desc":"possess full rights over an asset"})
                #miningnode.createNewEntity(prev_hash, {"name":"ADULT", "type":"qualifier", "desc":"if age>25"})
                miningnode.createBasicIncome(miningnode.tempUser, {"POINTS":100.0})
                #automatically create candidate block so there is something there 
                print("CREATE CANDIDATE BLOCK")
                miningnode.createCandidateBlock(block_height+1, prev_proof, prev_hash)
                #actually add initial block data to chain upon next iteration of chain
            else:
                #stop processing blocks when no blockX.dat files available to process and blockheight is > 0
                not_done_processing_blocks = False
    miningnode.latestBlockHeight = block_height
    # print(miningnode.chain)
    context = {
        "blockID":miningnode.chain[int(block_height-1)]["header"]["prev_block_height"],
        "transactions":miningnode.chain[int(block_height-1)]["transactions"]
    }
    #print(context)
    #print(miningnode.legalDictionary)
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

# def poll_detail(request, poll_id):
#     poll = get_object_or_404(Poll, id=poll_id)

#     if not poll.active:
#         return render(request, 'polls/poll_result.html', {'poll': poll})
#     loop_count = poll.choice_set.count()
#     context = {
#         'poll': poll,
#         'loop_time': range(0, loop_count),
#     }
#     return render(request, 'polls/poll_detail.html', context)